from __future__ import annotations

import json
import threading
import time
import urllib.request
import webbrowser
from urllib.error import URLError

from werkzeug.serving import make_server

from app import create_app

HOST = "127.0.0.1"
PORT = 5000
URL = f"http://{HOST}:{PORT}"


def gift_expert_activo() -> bool:
    try:
        with urllib.request.urlopen(f"{URL}/api/estado", timeout=1.5) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("ok") is True and data.get("motor") == "Python"
    except (URLError, TimeoutError, ValueError, OSError):
        return False


def abrir_navegador() -> None:
    time.sleep(0.7)
    webbrowser.open(URL, new=2)


def main() -> None:
    if gift_expert_activo():
        print(f"Gift Expert ya está activo en {URL}")
        webbrowser.open(URL, new=2)
        return

    app = create_app()
    try:
        servidor = make_server(HOST, PORT, app, threaded=True)
    except OSError as exc:
        print(f"No fue posible usar el puerto {PORT}: {exc}")
        print("Cierra la aplicación que esté usando ese puerto y vuelve a intentar.")
        raise SystemExit(1)

    threading.Thread(target=abrir_navegador, daemon=True).start()
    print("=" * 64)
    print(" GIFT EXPERT — MOTOR PYTHON + FLASK ACTIVO")
    print(f" Aplicación: {URL}")
    print(" Mantén esta ventana abierta mientras utilizas la plataforma.")
    print(" Para cerrar el servidor presiona Ctrl + C.")
    print("=" * 64)

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nCerrando Gift Expert...")
    finally:
        servidor.shutdown()


if __name__ == "__main__":
    main()
