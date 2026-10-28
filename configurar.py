"""Configuracion local del instalador; nunca imprime la credencial."""
import getpass
import secrets
from pathlib import Path
from dotenv import dotenv_values, set_key


def main():
    path = Path(__file__).resolve().parent / ".env"
    values = dotenv_values(path) if path.exists() else {}
    key = (values.get("DEEPSEEK_API_KEY") or "").strip()
    if not key or key in {"tu_api_key", "tu_clave_api_aqui_sk-..."}:
        while True:
            key = getpass.getpass("Pega tu API Key de DeepSeek (no se mostrara): ").strip()
            if key and not any(c.isspace() for c in key) and key != "tu_api_key":
                break
            print("Ingresa una credencial sin espacios; no puede quedar vacia.")
        path.touch(exist_ok=True)
        set_key(str(path), "DEEPSEEK_API_KEY", key)
        print("Credencial guardada en .env.")
    else:
        print("Se conserva la credencial existente en .env.")
    if not values.get("FLASK_SECRET_KEY"):
        set_key(str(path), "FLASK_SECRET_KEY", secrets.token_hex(32))


if __name__ == "__main__":
    main()
