"""Arranque local con navegador abierto solo cuando el servidor este listo."""
import threading
import webbrowser
from pathlib import Path
import os

os.chdir(Path(__file__).resolve().parent)
from werkzeug.serving import make_server
from app import app


def main():
    server = make_server("127.0.0.1", 5000, app, threaded=True)
    timer = threading.Timer(0.5, webbrowser.open, args=("http://127.0.0.1:5000",))
    timer.daemon = True
    timer.start()
    print("THEYTHINK AI: http://127.0.0.1:5000 - Ctrl+C para detener.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
