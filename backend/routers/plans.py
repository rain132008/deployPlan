from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import FileResponse
import json
import os
import glob
from core.generator import generate_document
from datetime import datetime

router = APIRouter()

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")

def get_plan_path(filename):
    return os.path.join(DATA_DIR, filename)

@router.get("/")
def list_plans():
    os.makedirs(DATA_DIR, exist_ok=True)
    files = glob.glob(os.path.join(DATA_DIR, "*.json"))
    plans = []
    for f in files:
        filename = os.path.basename(f)
        try:
            with open(f, "r", encoding="utf-8") as file:
                data = json.load(file)
                # Add basic info to listing
                plans.append({
                    "filename": filename,
                    "version": data.get("version", "N/A"),
                    "deploy_date": data.get("deploy_date", "N/A"),
                    "owner": data.get("owner", "N/A"),
                    "modified": os.path.getmtime(f)
                })
        except Exception:
            continue
    # Sort by modified time desc
    plans.sort(key=lambda x: x["modified"], reverse=True)
    return plans

@router.get("/{filename}")
def get_plan(filename: str):
    path = get_plan_path(filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Plan not found")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@router.post("/")
def save_plan(plan: dict = Body(...)):
    # If filename not provided, generate one based on version/date or timestamp
    filename = plan.get("filename")
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"plan_{timestamp}.json"
    
    # Ensure it ends with .json
    if not filename.endswith(".json"):
        filename += ".json"
        
    path = get_plan_path(filename)
    os.makedirs(DATA_DIR, exist_ok=True)
    
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        return {"message": "Plan saved", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate")
def generate_plan_document(plan: dict = Body(...)):
    # Generate the document immediately from the passed plan data
    try:
        output_path = generate_document(plan)
        return FileResponse(output_path, filename=os.path.basename(output_path), media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
