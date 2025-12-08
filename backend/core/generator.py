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
    
    steps = plan_data.get("steps", [])
    config_step_types = plan_data.get("_config_step_types", {}) # Front end might pass this, or we rely on the type field to find file
    # Actually, we should look up the template file from schema.json or assume a convention.
    # For simplicity, let's load schema.json here or assume the plan_data includes the template filename if provided.
    # Better approach: Read schema.json to look up template file for the step type.
    
    # Load schema for template mapping
    import json
    schema_path = os.path.join(BASE_DIR, "config", "schema.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    
    step_types_config = schema.get("step_types", {})
    
    for step in steps:
        sType = step.get("type")
        sData = step.get("data", {})
        
        if sType in step_types_config:
            template_file = step_types_config[sType].get("template_file")
            if template_file:
                sub_tpl_path = os.path.join(STEPS_DIR, template_file)
                if os.path.exists(sub_tpl_path):
                    sd = doc.new_subdoc(sub_tpl_path)
                    # Render the subdoc with step data
                    # Note: subdoc rendering in docxtpl is a bit implicit. 
                    # Usually you create a new docxtpl from the file, render it, and then use it as subdoc? 
                    # No, new_subdoc creates a subdoc object that you can't easily 'render' with jinja beforehand unless you do it manually.
                    # Wait, docxtpl `new_subdoc` adds the whole file. If that file has tags, they must be rendered with the MAIN context?
                    # No, tags in subdoc are not automatically rendered by the main render() call unless included in a specific way.
                    # Actually, a common pattern is:
                    # sub = doc.new_subdoc(path)
                    # sub.render(sData) -> This method does not exist on Subdoc usually.
                    
                    # Correct approach for docxtpl with separate step templates having variables:
                    # You instantiate a DocxTemplate for the CHILD, render it, and then save it to a stream (or temp file),
                    # then use `doc.new_subdoc()` on that Rendered content.
                    
                    sub_doc = DocxTemplate(sub_tpl_path)
                    sub_doc.render(sData)
                    
                    # We need to keep this rendered doc in memory or temp file to insert it
                    # doc.new_subdoc() takes a path.
                    
                    # Workaround: Save rendered subdoc to a temp file
                    temp_name = f"temp_{datetime.now().timestamp()}_{sType}.docx"
                    temp_path = os.path.join(OUTPUT_DIR, temp_name)
                    sub_doc.save(temp_path)
                    
                    try:
                        sd = doc.new_subdoc(temp_path)
                        rendered_steps.append(sd)
                    finally:
                        # Cleanup temp file? Or keep for debug. 
                        # better remove it later. For now let's keep it simple or try to clean up.
                         if os.path.exists(temp_path):
                            os.remove(temp_path)
                            pass

    
    # Prepare Context
    context = plan_data.copy()
    context['steps'] = rendered_steps
    
    # Render Master
    doc.render(context)
    
    # Save
    output_filename = f"Generated_Plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    final_path = os.path.join(OUTPUT_DIR, output_filename)
    doc.save(final_path)
    
    return final_path
