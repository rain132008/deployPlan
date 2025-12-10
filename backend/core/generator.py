from docxtpl import DocxTemplate
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STEPS_DIR = os.path.join(TEMPLATES_DIR, "steps")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "generated")

def generate_document(plan_data):
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Load Master Template
    master_path = os.path.join(TEMPLATES_DIR, "master.docx")
    if not os.path.exists(master_path):
        raise FileNotFoundError(f"Master template not found at {master_path}")
    
    doc = DocxTemplate(master_path)
    
    # Process Steps
    # We expect 'steps' in plan_data which is a list of dicts: {"type": "java_deploy", "data": {...}}
    # We need to map this to subdocs
    rendered_steps = []
    rendered_rollback_steps = []
    
    steps = plan_data.get("steps", [])
    
    # Load schema for template mapping
    import json
    schema_path = os.path.join(BASE_DIR, "config", "schema.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    
    step_types_config = schema.get("step_types", {})
    
    for step in steps:
        sType = step.get("type")
        sData = step.get("data", {})
        is_rollback = sData.get("is_rollback", False)
        
        if sType in step_types_config:
            template_file = step_types_config[sType].get("template_file")
            if template_file:
                sub_tpl_path = os.path.join(STEPS_DIR, template_file)
                if os.path.exists(sub_tpl_path):
                    # For rollback steps, we might want to ensure 'rollback_desc' is available. 
                    # It is already in sData if the frontend put it there.
                    
                    sub_doc = DocxTemplate(sub_tpl_path)
                    sub_doc.render(sData)
                    
                    # Workaround: Save rendered subdoc to a temp file
                    temp_name = f"temp_{datetime.now().timestamp()}_{sType}_{'rb' if is_rollback else 'dp'}_{id(step)}.docx"
                    temp_path = os.path.join(OUTPUT_DIR, temp_name)
                    sub_doc.save(temp_path)
                    
                    try:
                        sd = doc.new_subdoc(temp_path)
                        if is_rollback:
                            rendered_rollback_steps.append(sd)
                        else:
                            rendered_steps.append(sd)
                    finally:
                         if os.path.exists(temp_path):
                            os.remove(temp_path)
                            pass

    
    # Prepare Context
    context = plan_data.copy()
    context['steps'] = rendered_steps
    context['rollback_steps'] = rendered_rollback_steps
    
    # Render Master
    doc.render(context)
    
    # Save
    output_filename = f"Generated_Plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    final_path = os.path.join(OUTPUT_DIR, output_filename)
    doc.save(final_path)
    
    return final_path
