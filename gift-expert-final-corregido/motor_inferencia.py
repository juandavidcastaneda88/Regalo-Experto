from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from modelos import Consulta


class ErrorBaseConocimiento(RuntimeError):
    pass


class MotorInferencia:
    """Motor explicable basado en hechos, reglas ponderadas y resolución de conflictos."""

    ARCHIVOS = ("regalos.json", "reglas.json", "ocasiones.json", "intereses.json", "configuracion.json")

    def __init__(self, ruta_base: str | Path):
        self.ruta_base = Path(ruta_base)
        self.recargar()

    def _cargar_json(self, nombre: str) -> Any:
        ruta = self.ruta_base / nombre
        try:
            with ruta.open("r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except FileNotFoundError as exc:
            raise ErrorBaseConocimiento(f"No existe {nombre} en la base de conocimiento.") from exc
        except json.JSONDecodeError as exc:
            raise ErrorBaseConocimiento(f"El archivo {nombre} contiene JSON inválido: {exc}.") from exc

    def recargar(self) -> None:
        self.regalos = self._cargar_json("regalos.json")
        self.reglas = self._cargar_json("reglas.json")
        self.ocasiones = self._cargar_json("ocasiones.json")
        self.intereses = self._cargar_json("intereses.json")
        self.configuracion = self._cargar_json("configuracion.json")
        self._validar_base()

    def _validar_base(self) -> None:
        if not isinstance(self.regalos, list) or not self.regalos:
            raise ErrorBaseConocimiento("regalos.json debe contener una lista no vacía.")
        if not isinstance(self.reglas, list) or not self.reglas:
            raise ErrorBaseConocimiento("reglas.json debe contener una lista no vacía.")
        ids = [regalo.get("id") for regalo in self.regalos]
        if len(ids) != len(set(ids)):
            raise ErrorBaseConocimiento("Hay identificadores de regalos duplicados.")
        reglas_ids = [regla.get("id") for regla in self.reglas]
        if len(reglas_ids) != len(set(reglas_ids)):
            raise ErrorBaseConocimiento("Hay reglas duplicadas.")
        obligatorios = {"id", "nombre", "categoria", "precio", "descripcion", "intereses", "ocasiones", "relaciones", "personalidades", "tipos", "edad_min", "edad_max"}
        for regalo in self.regalos:
            faltantes = obligatorios.difference(regalo)
            if faltantes:
                raise ErrorBaseConocimiento(f"El regalo {regalo.get('id', '?')} no tiene: {', '.join(sorted(faltantes))}.")

    def catalogo_publico(self) -> dict[str, Any]:
        return {
            **self.configuracion,
            "ocasiones": self.ocasiones,
            "intereses": self.intereses,
            "total_regalos": len(self.regalos),
            "total_reglas": len(self.reglas),
        }

    def recomendar(self, consulta: Consulta | dict[str, Any], limite: int = 8) -> dict[str, Any]:
        hechos = consulta.a_dict() if isinstance(consulta, Consulta) else dict(consulta)
        evaluados: list[dict[str, Any]] = []
        descartados = 0

        for regalo in self.regalos:
            resultado = self._evaluar(regalo, hechos)
            if resultado is None:
                descartados += 1
            else:
                evaluados.append(resultado)

        # Resolución de conflictos: afinidad, número de coincidencias, ajuste al presupuesto y menor precio.
        evaluados.sort(
            key=lambda item: (
                -item["porcentaje"],
                -len(item["coincidencias"]),
                item["distancia_presupuesto"],
                item["precio"],
                item["nombre"],
            )
        )
        recomendaciones = evaluados[: max(1, min(int(limite), 20))]

        mensaje = (
            "Las alternativas se calcularon con reglas ponderadas, presupuesto, contexto y preferencias; nunca por género."
            if recomendaciones
            else "No encontramos un regalo compatible con el presupuesto y todas las restricciones. Ajusta uno de esos criterios."
        )
        return {
            "recomendaciones": recomendaciones,
            "mensaje": mensaje,
            "resumen_inferencia": {
                "metodo": "Encadenamiento hacia adelante con puntuación ponderada",
                "reglas_evaluadas": len(self.reglas),
                "regalos_evaluados": len(self.regalos),
                "regalos_descartados": descartados,
                "alternativas_compatibles": len(evaluados),
                "resolucion_conflictos": "Mayor afinidad, más coincidencias, mejor ajuste al presupuesto y menor precio",
            },
        }

    def _evaluar(self, regalo: dict[str, Any], hechos: dict[str, Any]) -> dict[str, Any] | None:
        presupuesto = int(hechos["presupuesto"])
        if int(regalo["precio"]) > presupuesto:
            return None

        restricciones = set(hechos.get("restricciones", []))
        if restricciones.intersection(regalo.get("restricciones", [])):
            return None

        puntaje = 0.0
        maximo = 0.0
        coincidencias: list[str] = []
        razones: list[str] = []
        detalle_reglas: list[dict[str, Any]] = []

        for regla in self.reglas:
            peso = float(regla["peso"])
            maximo += peso
            fraccion, detalle = self._aplicar_regla(regla, regalo, hechos)
            puntos = round(peso * fraccion, 3)
            puntaje += puntos
            activada = fraccion > 0

            if activada:
                coincidencias.append(regla["etiqueta"])
                explicacion = regla["explicacion"]
                if "{coincidencias}" in explicacion:
                    explicacion = explicacion.format(coincidencias=detalle or "sus gustos")
                razones.append(explicacion)

            detalle_reglas.append({
                "regla": regla["id"],
                "activada": activada,
                "puntos": points_round(puntos),
                "maximo": points_round(peso),
            })

        porcentaje = round((puntaje / maximo) * 100) if maximo else 0
        porcentaje = max(0, min(99, porcentaje))
        ratio = int(regalo["precio"]) / max(presupuesto, 1)

        return {
            "id": regalo["id"],
            "nombre": regalo["nombre"],
            "categoria": regalo["categoria"],
            "precio": int(regalo["precio"]),
            "imagen": regalo.get("imagen", "🎁"),
            "descripcion": regalo["descripcion"],
            "porcentaje": porcentaje,
            "coincidencias": coincidencias,
            "explicacion": " ".join(dict.fromkeys(razones)) or "Cumple el presupuesto y no presenta incompatibilidades.",
            "detalle_reglas": detalle_reglas,
            "distancia_presupuesto": round(abs(0.75 - ratio), 4),
        }

    def _aplicar_regla(self, regla: dict[str, Any], regalo: dict[str, Any], hechos: dict[str, Any]) -> tuple[float, str]:
        operador = regla["operador"]
        campo = regla.get("campo")
        atributo = regla.get("atributo_regalo")
        valor_usuario = hechos.get(campo)
        valor_regalo = regalo.get(atributo) if atributo else None

        if operador == "interseccion_proporcional":
            usuario = set(valor_usuario or [])
            regalo_valores = set(valor_regalo or [])
            comunes = sorted(usuario.intersection(regalo_valores))
            if not comunes:
                return 0.0, ""
            denominador = max(1, min(3, len(usuario)))
            proporcion = min(1.0, len(comunes) / denominador)
            return 0.70 + 0.30 * proporcion, ", ".join(comunes)

        if operador == "incluye":
            return (1.0, str(valor_usuario)) if valor_usuario in (valor_regalo or []) else (0.0, "")

        if operador == "incluye_o_cualquiera":
            if valor_usuario == "Cualquiera" or valor_usuario in (valor_regalo or []):
                return 1.0, str(valor_usuario)
            return 0.0, ""

        if operador == "rango_edad":
            edad = int(hechos["edad"])
            return (1.0, str(edad)) if int(regalo["edad_min"]) <= edad <= int(regalo["edad_max"]) else (0.0, "")

        if operador == "ajuste_presupuesto":
            ratio = int(regalo["precio"]) / max(int(hechos["presupuesto"]), 1)
            if 0.35 <= ratio <= 0.95:
                return 1.0, ""
            if ratio < 0.35:
                return 0.55, ""
            return 0.70, ""

        if operador == "disponibilidad":
            urgencia = hechos.get("urgencia", "sin_prisa")
            if urgencia == "sin_prisa":
                return 1.0, urgencia
            return (1.0, urgencia) if urgencia in (valor_regalo or []) else (0.0, "")

        raise ErrorBaseConocimiento(f"Operador de regla no reconocido: {operador}.")


def points_round(valor: float) -> int | float:
    return int(valor) if valor.is_integer() else round(valor, 2)
