from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


class ErrorValidacion(ValueError):
    """Agrupa todos los errores encontrados en una consulta."""

    def __init__(self, errores: list[str]):
        super().__init__(" ".join(errores))
        self.errores = errores


@dataclass(frozen=True)
class Consulta:
    edad: int
    relacion: str
    ocasion: str
    urgencia: str
    intereses: list[str]
    personalidad: str
    tipo_regalo: str
    presupuesto: int
    restricciones: list[str]

    def a_dict(self) -> dict[str, Any]:
        return asdict(self)


def _texto(valor: Any) -> str:
    return str(valor or "").strip()


def _lista_textos(valor: Any) -> list[str]:
    if not isinstance(valor, list):
        return []
    vistos: set[str] = set()
    salida: list[str] = []
    for elemento in valor:
        texto = _texto(elemento)
        if texto and texto not in vistos:
            vistos.add(texto)
            salida.append(texto)
    return salida


def validar_y_normalizar_consulta(datos: dict[str, Any], catalogo: dict[str, Any]) -> Consulta:
    errores: list[str] = []
    limites = catalogo.get("limites", {})

    try:
        edad = int(datos.get("edad"))
    except (TypeError, ValueError):
        edad = 0
    if not limites.get("edad_min", 1) <= edad <= limites.get("edad_max", 110):
        errores.append("La edad debe estar entre 1 y 110 años.")

    try:
        presupuesto = int(datos.get("presupuesto"))
    except (TypeError, ValueError):
        presupuesto = 0
    if presupuesto < limites.get("presupuesto_min", 10000):
        errores.append("El presupuesto mínimo es de $10.000 COP.")
    if presupuesto > limites.get("presupuesto_max", 20000000):
        errores.append("El presupuesto máximo es de $20.000.000 COP.")

    relacion = _texto(datos.get("relacion"))
    ocasion = _texto(datos.get("ocasion"))
    urgencia = _texto(datos.get("urgencia")) or "sin_prisa"
    personalidad = _texto(datos.get("personalidad"))
    tipo_regalo = _texto(datos.get("tipo_regalo"))
    intereses = _lista_textos(datos.get("intereses"))
    restricciones = _lista_textos(datos.get("restricciones", []))

    validaciones = [
        (relacion, catalogo.get("relaciones", []), "Selecciona una relación válida."),
        (ocasion, [x["nombre"] for x in catalogo.get("ocasiones", [])], "Selecciona una ocasión válida."),
        (urgencia, [x["valor"] for x in catalogo.get("urgencias", [])], "Selecciona un plazo válido."),
        (personalidad, catalogo.get("personalidades", []), "Selecciona una personalidad válida."),
        (tipo_regalo, catalogo.get("tipos_regalo", []), "Selecciona un tipo de regalo válido."),
    ]
    for valor, permitidos, mensaje in validaciones:
        if not valor or valor not in permitidos:
            errores.append(mensaje)

    intereses_validos = {x["nombre"] for x in catalogo.get("intereses", [])}
    if not intereses:
        errores.append("Selecciona al menos un interés.")
    elif any(x not in intereses_validos for x in intereses):
        errores.append("La consulta contiene intereses no reconocidos.")

    restricciones_validas = {x["valor"] for x in catalogo.get("restricciones", [])}
    if any(x not in restricciones_validas for x in restricciones):
        errores.append("La consulta contiene restricciones no reconocidas.")

    if errores:
        raise ErrorValidacion(errores)

    return Consulta(
        edad=edad,
        relacion=relacion,
        ocasion=ocasion,
        urgencia=urgencia,
        intereses=intereses,
        personalidad=personalidad,
        tipo_regalo=tipo_regalo,
        presupuesto=presupuesto,
        restricciones=restricciones,
    )
