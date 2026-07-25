import shutil
from pathlib import Path

import pytest

from app import create_app


@pytest.fixture()
def client(tmp_path):
    original = Path(__file__).resolve().parents[1] / "base_conocimiento"
    copia = tmp_path / "base_conocimiento"
    shutil.copytree(original, copia)
    app = create_app({"TESTING": True, "BASE_CONOCIMIENTO": str(copia)})
    return app.test_client()


def consulta_valida():
    return {"edad":27,"relacion":"Amigo/a","ocasion":"Cumpleaños","urgencia":"semana","intereses":["Tecnología","Música"],"personalidad":"Tecnológica","tipo_regalo":"Tecnología","restricciones":[],"presupuesto":350000}


def test_index_y_estado(client):
    assert client.get("/").status_code == 200
    estado = client.get("/api/estado").get_json()
    assert estado["ok"] is True
    assert estado["motor"] == "Python"


def test_recomendacion_guarda_historial(client):
    respuesta = client.post("/api/recomendar", json=consulta_valida())
    assert respuesta.status_code == 200
    datos = respuesta.get_json()
    assert datos["recomendaciones"]
    historial = client.get("/api/historial").get_json()
    assert historial["estadisticas"]["consultas"] == 1


def test_validacion_api(client):
    respuesta = client.post("/api/recomendar", json={"edad": 0})
    assert respuesta.status_code == 400
    assert respuesta.get_json()["errores"]


def test_limpiar_historial(client):
    client.post("/api/recomendar", json=consulta_valida())
    respuesta = client.delete("/api/historial")
    assert respuesta.status_code == 200
    assert client.get("/api/historial").get_json()["historial"] == []
