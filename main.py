#!/usr/bin/env python3
"""
Point d'entrée principal pour Multi-Orchestrator-Bot.
"""

import logging
import sys
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from orchestrator.cli import main

if __name__ == "__main__":
    # Configuration du logging global
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("orchestrator.log")
        ]
    )

    main()
