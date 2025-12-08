from fastapi import APIRouter, HTTPException
import json
import os

router = APIRouter()

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "schema.json")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(data):
    # Ensure directory exists
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@router.get("/")
def get_config():
    try:
        return load_config()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/")
def update_config(config_data: dict):
    try:
        save_config(config_data)
        return {"message": "Config updated successfully", "config": config_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
