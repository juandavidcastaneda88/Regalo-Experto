from pathlib import Path
import json

BASE = Path(__file__).resolve().parent
requeridos = [
    "index.html", "app.py", "launcher.py", "motor_inferencia.py", "modelos.py",
    "templates/index.html", "static/css/styles.css", "static/js/app.js",
    "base_conocimiento/regalos.json", "base_conocimiento/reglas.json"
]
faltantes = [ruta for ruta in requeridos if not (BASE / ruta).exists()]
if faltantes:
    print("FALTAN ARCHIVOS:")
    for ruta in faltantes:
        print(" -", ruta)
    raise SystemExit(1)

for nombre in ["regalos.json", "reglas.json", "ocasiones.json", "intereses.json", "configuracion.json"]:
    json.loads((BASE / "base_conocimiento" / nombre).read_text(encoding="utf-8"))

print("Proyecto verificado correctamente.")
print("Abre EJECUTAR_GIFT_EXPERT.bat para iniciar la aplicación.")
