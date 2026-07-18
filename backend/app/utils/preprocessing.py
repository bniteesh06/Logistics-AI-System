import os
from app.utils.data_generator import generate_data, DATA_PATH


def ensure_data():
    """Called once on startup so every route can assume data/*.csv exists."""
    if not os.path.exists(f"{DATA_PATH}/demand_history.csv"):
        generate_data()
