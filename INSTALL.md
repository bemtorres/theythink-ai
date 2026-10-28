# Instalacion de THEYTHINK AI

## Windows: un solo paso

Con conexion a Internet, haz doble clic en `install.bat` y pega tu API Key de DeepSeek cuando se solicite. La entrada esta oculta. No hace falta instalar Python previamente ni abrir una terminal.

El instalador busca Python 3.10 o superior; si falta, descarga Python 3.12.10 desde python.org, verifica su firma digital y lo instala para el usuario actual. Luego prepara `venv`, instala `requirements.txt`, guarda la credencial en `.env`, genera una clave privada para Flask y ejecuta `seed.py` sin borrar datos existentes.

Al terminar, abre automaticamente http://127.0.0.1:5000. Conserva la ventana abierta mientras usas la aplicacion; Ctrl+C detiene el servidor. El registro e inicio de sesion de la plataforma se hacen desde el navegador.

Para los siguientes usos, haz doble clic en `iniciar.bat`. Para cambiar la credencial, edita `DEEPSEEK_API_KEY` en `.env`. No compartas ese archivo.

Puedes repetir `install.bat` para reparar dependencias: conserva la credencial, los usuarios y las conversaciones. Si falla una descarga, revisa la conexion y vuelve a ejecutarlo. Si el puerto 5000 esta ocupado, cierra la otra instancia antes de iniciar. Una credencial aceptada por el instalador debe ser valida y tener acceso/saldo en DeepSeek para que el chat responda; el instalador no consume la API para comprobarla.

## Instalacion manual (Linux/macOS)

Requiere Python 3.10 o superior:

```sh
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python configurar.py
python seed.py
python ejecutar.py
```
