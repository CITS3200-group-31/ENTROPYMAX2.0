## Frontend (PyQt6) – Setup and Run

You can use either a Python virtualenv (recommended) or Conda. Both options are shown below.

### Option A: Python venv (recommended)
```bash
cd frontend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

### Option B: Conda
```bash
conda create -y -n entro python=3.11
conda activate entro
cd frontend
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

### Notes
- Requires Qt 6 (PyQt6 and PyQt6-WebEngine are installed via `requirements.txt`).
- Sample data and a simple smoke test are included under `frontend/test/`.
- If the app fails to launch due to Qt platform plugins on macOS, try launching from a real terminal session (not from an IDE) with the virtualenv activated.
