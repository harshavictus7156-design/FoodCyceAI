"""Streamlit Community Cloud Entry Point for FoodCycle AI."""
import os
import sys

# Ensure current directory is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from app import main

if __name__ == "__main__":
    main()
