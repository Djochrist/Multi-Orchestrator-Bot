
"""
Script de lancement pour Multi-Orchestrator-Bot
"""

import subprocess
import sys
import os

if __name__ == "__main__":
    # Définit le PYTHONPATH
    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.dirname(__file__)

    # Commande uvicorn
    cmd = [
        sys.executable, '-m', 'uvicorn',
        'src.main:app',
        '--host', '0.0.0.0',
        '--port', '8000',
        '--log-level', 'info'
    ]

    # Mode rechargement si DEBUG=true
    if os.getenv('DEBUG', 'false').lower() == 'true':
        cmd.append('--reload')

    subprocess.run(cmd, env=env)
