@echo off
echo Starting Gold Intelligence MVP V10...
echo.
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
python -m streamlit run app.py
pause
