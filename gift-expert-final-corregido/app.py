from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, render_template, request

from modelos import ErrorValidacion, validar_y_normalizar_consulta
from motor_inferencia import ErrorBaseConocimiento, MotorInferencia
from servicios.historial import HistorialService


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    base_dir = Path(__file__).resolve().parent
    app.config.update(
        BASE_CONOCIMIENTO=str(base_dir / "base_conocimiento"),
        JSON_SORT_KEYS=False,
        SEND_FILE_MAX_AGE_DEFAULT=0,
    )
    if test_config:
        app.config.update(test_config)

    ruta_base = Path(app.config["BASE_CONOCIMIENTO"])
    motor = MotorInferencia(ruta_base)
    historial = HistorialService(ruta_base / "historial.json")
    app.extensions["motor_inferencia"] = motor
    app.extensions["historial_service"] = historial

    @app.get("/")
    @app.get("/index.html")
    def inicio():
        return render_template("index.html")

    @app.after_request
    def agregar_cabeceras(respuesta):
        # Permite que el index.html abierto directamente (file://) se conecte
        # al backend local. Esto también evita que el navegador conserve CSS/JS antiguos.
        respuesta.headers["Access-Control-Allow-Origin"] = "*"
        respuesta.headers["Access-Control-Allow-Headers"] = "Content-Type"
        respuesta.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
        respuesta.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        return respuesta

    @app.get("/api/estado")
    def estado():
        return jsonify({
            "ok": True,
            "estado": "operativo",
            "motor": "Python",
            "servidor": "Flask",
            "regalos": len(motor.regalos),
            "reglas": len(motor.reglas),
        })

    @app.get("/api/catalogo")
    def catalogo():
        return jsonify({"ok": True, **motor.catalogo_publico()})

    @app.post("/api/recomendar")
    def recomendar():
        datos = request.get_json(silent=True)
        if not isinstance(datos, dict):
            return jsonify({"ok": False, "errores": ["Envía los datos de la consulta en formato JSON."]}), 400
        try:
            consulta = validar_y_normalizar_consulta(datos, motor.catalogo_publico())
            resultado = motor.recomendar(consulta, limite=10)
            registro = {
                "id": str(uuid4()),
                "fecha": datetime.now().astimezone().isoformat(timespec="seconds"),
                "consulta": consulta.a_dict(),
                "resultado": resultado,
            }
            historial.agregar(registro)
            return jsonify({"ok": True, "consulta": consulta.a_dict(), **resultado})
        except ErrorValidacion as exc:
            return jsonify({"ok": False, "errores": exc.errores}), 400

    @app.get("/api/historial")
    def obtener_historial():
        registros = historial.listar()
        return jsonify({
            "ok": True,
            "historial": registros,
            "estadisticas": {
                **historial.estadisticas(registros),
                "regalos_disponibles": len(motor.regalos),
                "reglas_activas": len(motor.reglas),
            },
        })

    @app.delete("/api/historial")
    def limpiar_historial():
        historial.limpiar()
        return jsonify({"ok": True, "mensaje": "Historial eliminado correctamente."})

    @app.post("/api/base-conocimiento/recargar")
    def recargar_base():
        motor.recargar()
        return jsonify({
            "ok": True,
            "mensaje": "Base de conocimiento recargada.",
            "regalos": len(motor.regalos),
            "reglas": len(motor.reglas),
        })

    @app.errorhandler(ErrorBaseConocimiento)
    def error_base(exc: ErrorBaseConocimiento):
        return jsonify({"ok": False, "errores": [str(exc)]}), 500

    @app.errorhandler(404)
    def no_encontrado(_):
        if request.path.startswith("/api/"):
            return jsonify({"ok": False, "errores": ["Ruta de API no encontrada."]}), 404
        return render_template("index.html"), 404

    @app.errorhandler(500)
    def error_interno(exc):
        app.logger.exception("Error interno", exc_info=exc)
        return jsonify({"ok": False, "errores": ["Ocurrió un error interno en el servidor."]}), 500

    return app


app = create_app()


if __name__ == "__main__":
    puerto = int(os.getenv("PORT", "5000"))
    app.run(host="127.0.0.1", port=puerto, debug=os.getenv("FLASK_DEBUG") == "1")
