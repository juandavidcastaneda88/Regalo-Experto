from pathlib import Path

from modelos import validar_y_normalizar_consulta
from motor_inferencia import MotorInferencia

BASE = Path(__file__).resolve().parents[1] / "base_conocimiento"
MOTOR = MotorInferencia(BASE)
CATALOGO = MOTOR.catalogo_publico()

CASOS = [
    {"edad":25,"relacion":"Pareja","ocasion":"Aniversario","urgencia":"semana","intereses":["Gastronomía","Experiencias"],"personalidad":"Sentimental","tipo_regalo":"Experiencia","restricciones":[],"presupuesto":300000},
    {"edad":17,"relacion":"Hermano/a","ocasion":"Cumpleaños","urgencia":"hoy","intereses":["Tecnología","Música"],"personalidad":"Tecnológica","tipo_regalo":"Tecnología","restricciones":[],"presupuesto":200000},
    {"edad":52,"relacion":"Madre","ocasion":"Día de la Madre","urgencia":"semana","intereses":["Bienestar","Familia"],"personalidad":"Tranquila","tipo_regalo":"Bienestar","restricciones":[],"presupuesto":250000},
    {"edad":30,"relacion":"Amigo/a","ocasion":"Graduación","urgencia":"mes","intereses":["Viajes","Naturaleza"],"personalidad":"Aventurera","tipo_regalo":"Objeto útil","restricciones":[],"presupuesto":300000},
    {"edad":40,"relacion":"Compañero/a de trabajo","ocasion":"Agradecimiento","urgencia":"hoy","intereses":["Lectura","Ciencia"],"personalidad":"Práctica","tipo_regalo":"Cualquiera","restricciones":[],"presupuesto":120000},
]


def test_cinco_casos_generan_resultados_explicados():
    for datos in CASOS:
        consulta = validar_y_normalizar_consulta(datos, CATALOGO)
        resultado = MOTOR.recomendar(consulta)
        assert resultado["recomendaciones"]
        mejor = resultado["recomendaciones"][0]
        assert 0 <= mejor["porcentaje"] <= 99
        assert mejor["explicacion"]
        assert mejor["detalle_reglas"]


def test_ningun_resultado_supera_presupuesto():
    consulta = validar_y_normalizar_consulta(CASOS[0], CATALOGO)
    resultado = MOTOR.recomendar(consulta)
    assert all(x["precio"] <= consulta.presupuesto for x in resultado["recomendaciones"])


def test_restriccion_descarta_fragancias():
    datos = {**CASOS[0], "intereses":["Belleza","Moda"], "restricciones":["Sensibilidad a fragancias"], "presupuesto":500000}
    consulta = validar_y_normalizar_consulta(datos, CATALOGO)
    resultado = MOTOR.recomendar(consulta, limite=20)
    assert all(x["id"] != "perfume" for x in resultado["recomendaciones"])


def test_catalogo_no_usa_genero():
    assert "genero" not in CATALOGO
    assert all("genero" not in regalo for regalo in MOTOR.regalos)
