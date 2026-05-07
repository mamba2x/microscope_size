# Project 1: Microscope Specimen Size Calculator

This folder now contains a complete Python solution for the `project1` assignment.

## What is included

- `cli_app.py`: command-line version for phases `(a)` and `(b)`
- `desktop_gui.py`: Python GUI version for phase `(c)`
- `web_app.py`: Flask web application for phase `(d)`
- `microscope_core.py`: shared calculation, validation, unit conversion, and breakdown logic
- `database.py`: SQLite database integration
- `templates/` and `static/`: web interface files
- `uploads/`: saved specimen images
- `microscope_calculations.db`: created automatically when you run the app

## Scientific formula

`Real Size = Measured Size (mm) / Magnification Factor`

## Predefined microscope types

- Compound Microscope (40x)
- Compound Microscope (100x)
- Compound Microscope (400x)
- Stereo Microscope (20x)
- Electron Microscope (1000x)

## Supported output units

- `nm`
- `um`
- `mm`
- `cm`
- `m`

## How to run

### Command line

```bash
python cli_app.py
```

### Desktop GUI

```bash
python desktop_gui.py
```

### Web app

```bash
python web_app.py
```

Then open `http://127.0.0.1:5000`

## Hosting for phase (e)

This project is now prepared for Render deployment.

### Local production-style start command

```bash
gunicorn web_app:app
```

### Render setup

1. Push this folder to GitHub.
2. Create a new `Web Service` on Render from that GitHub repo.
3. Add a persistent disk in Render and mount it at:

```text
/var/data
```

4. Set these environment variables in Render:

```text
MICROSCOPE_DATA_DIR=/var/data
SECRET_KEY=your-random-secret-value
PYTHON_VERSION=3.14.0
```

5. Render should use:

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn web_app:app`

### Important deployment note

The app stores:

- `microscope_calculations.db`
- uploaded files in `uploads/`

Both should live on the Render persistent disk through `MICROSCOPE_DATA_DIR=/var/data`.

Without a persistent disk, saved records and uploaded images may be lost after redeploys or restarts.
