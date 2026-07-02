@echo off
REM Virtual Environment Setup Script for Windows
REM This script creates and activates a Python virtual environment

echo Creating virtual environment...
python -m venv .venv

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip setuptools wheel
pip install -r requirements-dev.txt

echo.
echo Virtual environment setup complete!
echo To activate in the future, run: .venv\Scripts\activate.bat
echo To deactivate, run: deactivate
