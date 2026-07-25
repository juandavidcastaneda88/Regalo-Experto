# Gift Expert — Versión final corregida

Aplicación completa que conecta una interfaz visual moderna con un motor de inferencia real en **Python + Flask**.

## Solución al problema del `index.html` sin estilos

La versión anterior podía verse como HTML básico cuando se abría `templates/index.html` directamente, porque las rutas de CSS y JavaScript dependían de Flask.

Esta versión incluye:

- `index.html` en la raíz para vista directa con todos los estilos.
- `templates/index.html` para Flask, también con rutas compatibles.
- Detección automática de apertura mediante `file://`.
- Conexión desde el `index.html` directo al backend local en `http://127.0.0.1:5000`.
- Aviso visual claro cuando Python no está iniciado.
- Control de caché para que el navegador no conserve CSS o JavaScript antiguos.

  <img width="1055" height="1491" alt="image" src="https://github.com/user-attachments/assets/e8c14946-fa74-4882-bed9-a5243a2622c6" />


## Inicio recomendado en Windows

1. Entra a la carpeta donde esta todo el codigo llamada gift-expert-final-corregido
2. Abre la carpeta `gift-expert-final-corregido`.
3. Haz doble clic en **`EJECUTAR_GIFT_EXPERT.bat`**.
4. si no abre dirigete en la parte superior donde aparece el nombre gift-expert-final-corregido
5. powershell
6. py -3 -m venv .venv
7. .\.venv\Scripts\python.exe -m pip install -r requirements.txt
8. .\.venv\Scripts\python.exe launcher.py
9. Se abrira el sistema experto

```text
http://127.0.0.1:5000
```

Mantén abierta la ventana negra del servidor mientras utilizas la plataforma.

## Inicio manual

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Después:

```bash
python -m pip install -r requirements.txt
python launcher.py
```

## Funciones completas

- Inicio visual profesional y responsive.
- Formulario paso a paso con cinco etapas.
- Validación en vivo en navegador y validación adicional en Python.
- Preguntas de edad, relación, ocasión, urgencia, intereses, personalidad, tipo de regalo, presupuesto y restricciones.
- Motor de inferencia explicable con encadenamiento hacia adelante y reglas ponderadas.
- Filtros estrictos por presupuesto y restricciones.
- Porcentaje de afinidad y explicación de cada conclusión.
- Botones para cambiar presupuesto, ver alternativas y realizar una nueva consulta.
- Historial persistente en JSON.
- Panel administrativo con estadísticas y buscador.
- Recarga de la base de conocimiento sin modificar la lógica.
- Tema claro y oscuro.
- Interfaz adaptable a celular, tableta y computador.
- No utiliza género ni recomendaciones discriminatorias.

## Estructura

```text
gift-expert-final-corregido/
├── index.html                         # Vista directa visual
├── app.py                             # Aplicación Flask y API
├── launcher.py                        # Inicia servidor y navegador
├── motor_inferencia.py                # Motor experto
├── modelos.py                         # Validación y modelo de consulta
├── EJECUTAR_GIFT_EXPERT.bat           # Inicio recomendado para Windows
├── EJECUTAR_GIFT_EXPERT.command       # Inicio para macOS/Linux
├── requirements.txt
├── LEEME_PRIMERO.txt
├── base_conocimiento/
│   ├── configuracion.json
│   ├── regalos.json
│   ├── reglas.json
│   ├── ocasiones.json
│   ├── intereses.json
│   └── historial.json
├── servicios/
│   └── historial.py
├── templates/
│   └── index.html                     # Interfaz servida por Flask
├── static/
│   ├── css/styles.css
│   └── js/app.js
├── tests/
│   ├── test_api.py
│   ├── test_motor.py
│   └── test_frontend.py
└── docs/
    ├── ANALISIS_Y_MOTOR.md
    └── DIAGRAMAS.md
```
<img width="1491" height="1055" alt="image" src="https://github.com/user-attachments/assets/2fd6e103-95dc-4014-9bc4-68967a87b4fd" />

## Base de conocimiento editable

Los regalos y las reglas están separados de la lógica principal. Modifica los archivos JSON de `base_conocimiento/` y después pulsa **Recargar base** en el panel de historial.

## Pruebas

```bash
pytest -q
```

Las pruebas verifican el motor, las API, el historial, los recursos CSS/JS y las rutas del `index.html`.

<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/588925f4-ea49-4737-9dd5-58ba79098a13" />


