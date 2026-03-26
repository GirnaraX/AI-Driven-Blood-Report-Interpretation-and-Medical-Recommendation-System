# storage.py
import json
import pandas as pd
import os
from datetime import datetime

def append_record_to_file(filepath, record):
    """Append a record (dict) to a JSON file, creating the file if needed."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        if os.path.exists(filepath):
            with open(filepath, 'r+', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
                data.append(record)
                f.seek(0)
                json.dump(data, f, indent=2)
                f.truncate()
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump([record], f, indent=2)
    except Exception as e:
        print(f"Failed to append record to {filepath}: {e}")

def append_record_to_csv(filepath, record):
    """Append a record to a CSV file."""
    # flatten nested structures
    flat = {}

    def _flatten(prefix, value):
        if isinstance(value, dict):
            for k, v in value.items():
                _flatten(f"{prefix}{k}_", v)
        elif isinstance(value, list):
            flat[prefix[:-1]] = json.dumps(value, ensure_ascii=False)
        else:
            flat[prefix[:-1]] = value

    _flatten("", record)

    df = pd.DataFrame([flat])
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if os.path.exists(filepath):
        df.to_csv(filepath, mode="a", header=False, index=False)
    else:
        df.to_csv(filepath, index=False)

def save_analysis_record(patient_info, report_data, results):
    """Build a record from the current analysis and save to history/patients files."""
    record = {
        "patient_info": patient_info,
        "report_data": report_data,
        "analysis_results": {
            "summary": results.get("summary", ""),
            "normal_parameters": results.get("normal_parameters", []),
            "abnormal_parameters": results.get("abnormal_parameters", []),
            "critical_parameters": results.get("critical_parameters", []),
            "conditions_detected": results.get("conditions_detected", []),
            "recommendations": results.get("recommendations", [])
        },
        "timestamp": datetime.now().isoformat()
    }
    try:
        append_record_to_csv(os.path.join("data", "history.csv"), record)
        append_record_to_csv(os.path.join("data", "patients.csv"), record)
    except Exception as e:
        print(f"Error saving record: {e}")