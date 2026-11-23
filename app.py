"""
Tata Power EV Analytics — Server Launcher
Starts the Flask server with PostgreSQL connectivity.
Run: python app.py
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from server import start_server

if __name__ == "__main__":
    start_server()
