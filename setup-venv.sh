#!/bin/bash
# Virtual Environment Setup Script for macOS/Linux
# This script creates and activates a Python virtual environment

echo "Creating virtual environment..."
python3 -m venv .venv

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements-dev.txt

echo ""
echo "Virtual environment setup complete!"
echo "To activate in the future, run: source .venv/bin/activate"
echo "To deactivate, run: deactivate"
