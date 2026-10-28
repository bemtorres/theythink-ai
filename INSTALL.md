# Instalación de THEYTHINK AI

## Windows: un solo paso

Descarga o clona el proyecto completo y, si viene en ZIP, extrae toda la carpeta. Con conexión a Internet, haz doble clic en `install.bat` y pega tu API Key de DeepSeek cuando se solicite. La entrada está oculta. No hace falta instalar Python previamente ni abrir una terminal.

El instalador realiza estos pasos automáticamente:

1. Busca Python 3.10 o superior. Si falta, descarga Python 3.12.10 desde python.org, verifica su firma digital y lo instala para el usuario actual.
2. Prepara el entorno virtual `venv`.
3. Instala las dependencias de `requirements.txt`.
4. Comprueba que todas las personas del catálogo tengan su imagen local incluida.
5. Guarda la credencial de DeepSeek en `.env` y genera una clave privada para Flask.
6. Ejecuta el único `seed.py`, que carga personas, conocimientos, conversaciones de ejemplo y rutas de sus avatares. Si un paso falla, detiene la instalación y muestra el error.

Al terminar, inicia la aplicación y abre automáticamente [http://127.0.0.1:5000](http://127.0.0.1:5000). Conserva la ventana abierta mientras la usas; Ctrl+C detiene el servidor. El registro e inicio de sesión se hacen desde el navegador.

## Qué incluye la carga inicial

Se cargan **31 personas con imágenes individuales**:

| Grupo | Personas |
|---|---:|
| Music Pro | 20 |
| Ejemplos: Benjamin, Elon Musk y Albert Einstein | 3 |
| Personajes literarios, históricos y culturales | 8 |

Los cuatro proyectos de Music Pro son **tienda en línea, sucursal física, bodega y pagos**. Cada uno incluye un jefe experto con presupuesto ficticio millonario, un trabajador agotado por el sistema, otro trabajador feliz en un puesto diferente y dos clientes entusiastas que cuentan su experiencia y proponen mejoras.

Las definiciones están en `personas.py` y las imágenes en `static/img/personas/`. Los retratos ya vienen generados: la instalación no necesita generar imágenes, descargarlas de servicios externos ni usar una API Key de OpenAI. Solo se necesita la credencial de DeepSeek para conversar.

No hay que ejecutar un seeder separado para Music Pro ni comandos adicionales para agregar las imágenes. Consulta el [resumen de personas](RESUMEN_PERSONAS.md) y la [galería completa](static/img/personas/README.md).

## Siguientes usos y reinstalación

Haz doble clic en `iniciar.bat`. Para cambiar la credencial, edita `DEEPSEEK_API_KEY` en `.env`. No compartas ese archivo.

Puedes repetir `install.bat` para reparar dependencias: conserva la credencial, los usuarios y las conversaciones. La carga agrega las personas faltantes sin duplicarlas ni sobrescribir las existentes. Las nuevas definiciones e imágenes se aplican directamente en una instalación desde cero.

## Instalación manual

Requiere Python 3.10 o superior y la carpeta completa del proyecto. Ejecuta los comandos desde su raíz.

En Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe configurar.py
.\venv\Scripts\python.exe seed.py
.\venv\Scripts\python.exe ejecutar.py
```

En Linux/macOS:

```sh
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python configurar.py
python seed.py
python ejecutar.py
```

## Si algo falla

- **Faltan imágenes o `setup.ps1`:** vuelve a descargar o copiar el proyecto completo, incluida la carpeta `static/img/personas/`. No ejecutes el instalador desde dentro del ZIP.
- **Falla una descarga o la instalación de dependencias:** revisa la conexión y vuelve a ejecutar `install.bat`.
- **El chat no responde por autenticación:** verifica la credencial y el acceso/saldo de DeepSeek. El instalador guarda la clave, pero no consume la API para comprobarla.
- **El puerto 5000 está ocupado:** cierra la otra instancia antes de iniciar.
