def test_recursos_visuales_se_entregan(client):
    pagina = client.get("/")
    assert pagina.status_code == 200
    html = pagina.get_data(as_text=True)
    assert "../static/css/styles.css" in html
    assert "../static/js/app.js" in html
    assert "backendStatus" in html
    assert client.get("/static/css/styles.css").status_code == 200
    assert client.get("/static/js/app.js").status_code == 200


def test_index_html_tambien_funciona_como_ruta(client):
    respuesta = client.get("/index.html")
    assert respuesta.status_code == 200
    assert "Gift Expert" in respuesta.get_data(as_text=True)


def test_cors_permita_index_directo(client):
    respuesta = client.get("/api/estado", headers={"Origin": "null"})
    assert respuesta.headers["Access-Control-Allow-Origin"] == "*"
