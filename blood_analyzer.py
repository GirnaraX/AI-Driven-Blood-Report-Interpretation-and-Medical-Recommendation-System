# blood_analyzer.py
import pandas as pd
import os
from reference_data.recommendations import RECOMMENDATIONS

# ----------------------------------------------------------------------
# Load reference ranges from CSV files (global for external use)
# ----------------------------------------------------------------------
def _load_reference_ranges_from_csv():
    """Load all reference ranges from CSV files into a nested dictionary."""
    ref_dir = os.path.join(os.path.dirname(__file__), 'reference_data')
    all_refs = {}
    csv_files = [
        'cbc_reference.csv', 'lipid_reference.csv', 'liver_reference.csv',
        'kidney_reference.csv', 'thyroid_reference.csv', 'diabetes_reference.csv',
        'iron_reference.csv', 'electrolytes_reference.csv'
    ]
    for file in csv_files:
        filepath = os.path.join(ref_dir, file)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            for _, row in df.iterrows():
                category = row['category']
                param = row['parameter']
                gender = row['gender']
                low = row['low']
                high = row['high']
                unit = row['unit']
                if category not in all_refs:
                    all_refs[category] = {}
                if param not in all_refs[category]:
                    all_refs[category][param] = {}
                if gender == 'all':
                    all_refs[category][param]['all'] = (low, high)
                else:
                    all_refs[category][param][gender] = (low, high)
                all_refs[category][param]['unit'] = unit
    return all_refs

# Global reference ranges dictionary (used by both the class and external imports)
REFERENCE_RANGES = _load_reference_ranges_from_csv()

# ----------------------------------------------------------------------
# Blood Report Analyzer Class
# ----------------------------------------------------------------------
class BloodReportAnalyzer:
    def __init__(self):
        self.patient_data = {}
        self.results = {}
        self.reference_ranges = REFERENCE_RANGES   # use the loaded data

    def analyze_blood_report(self, report_data, gender, age):
        """Analyze blood report and generate insights."""
        analysis_results = {
            "normal_parameters": [],
            "abnormal_parameters": [],
            "critical_parameters": [],
            "conditions_detected": [],
            "summary": "",
            "recommendations": []
        }

        if not report_data:
            return analysis_results

        for category, parameters in report_data.items():
            if category in self.reference_ranges:
                for param, value in parameters.items():
                    if param in self.reference_ranges[category]:
                        ref_data = self.reference_ranges[category][param]
                        if "all" in ref_data:
                            low, high = ref_data["all"]
                        elif gender in ref_data:
                            low, high = ref_data[gender]
                        else:
                            continue
                        unit = ref_data.get("unit", "")
                        status = self.check_range(value, low, high)
                        param_result = {
                            "category": category,
                            "parameter": param,
                            "value": value,
                            "unit": unit,
                            "low": low,
                            "high": high,
                            "status": status
                        }
                        if status == "normal":
                            analysis_results["normal_parameters"].append(param_result)
                        elif status in ["low", "high"]:
                            analysis_results["abnormal_parameters"].append(param_result)
                        elif status == "critical":
                            analysis_results["critical_parameters"].append(param_result)

        analysis_results["conditions_detected"] = self.detect_conditions(
            analysis_results["abnormal_parameters"] + analysis_results["critical_parameters"],
            gender, age
        )
        analysis_results["recommendations"] = self.generate_recommendations(
            analysis_results["conditions_detected"]
        )
        analysis_results["summary"] = self.generate_summary(analysis_results, gender, age)
        return analysis_results

    def check_range(self, value, low, high):
        """Check if value is within normal range, flag low/high/critical."""
        try:
            value = float(value) if value is not None else 0
            low = float(low)
            high = float(high)
            if value < low:
                if value < low * 0.7:
                    return "critical"
                return "low"
            elif value > high:
                if value > high * 1.5:
                    return "critical"
                return "high"
            else:
                return "normal"
        except (ValueError, TypeError):
            return "unknown"

    def detect_conditions(self, abnormal_params, gender, age):
        """Detect possible medical conditions from abnormal parameters."""
        conditions = []
        abnormal_dict = {}
        for param in abnormal_params:
            abnormal_dict[param["parameter"]] = {
                "value": param["value"],
                "status": param["status"]
            }

        # Anemia
        if "Hemoglobin" in abnormal_dict and abnormal_dict["Hemoglobin"]["status"] in ["low", "critical"]:
            conditions.append({
                "condition": "Anemia",
                "parameters": ["Hemoglobin"],
                "severity": "high" if abnormal_dict["Hemoglobin"]["status"] == "critical" else "moderate"
            })

        # Diabetes / Pre-diabetes
        if "Fasting Glucose" in abnormal_dict:
            fg_value = float(abnormal_dict["Fasting Glucose"]["value"])
            if fg_value > 126:
                conditions.append({"condition": "Diabetes Risk", "parameters": ["Fasting Glucose"], "severity": "high"})
            elif fg_value > 100:
                conditions.append({"condition": "Pre-diabetes", "parameters": ["Fasting Glucose"], "severity": "moderate"})

        if "HbA1c" in abnormal_dict:
            hba1c_value = float(abnormal_dict["HbA1c"]["value"])
            if hba1c_value > 6.5:
                conditions.append({"condition": "Diabetes Risk", "parameters": ["HbA1c"], "severity": "high"})
            elif hba1c_value > 5.7:
                conditions.append({"condition": "Pre-diabetes", "parameters": ["HbA1c"], "severity": "moderate"})

        # High Cholesterol
        if "Total Cholesterol" in abnormal_dict:
            tc_value = float(abnormal_dict["Total Cholesterol"]["value"])
            if tc_value > 200:
                severity = "high" if tc_value > 240 else "moderate"
                conditions.append({"condition": "High Cholesterol", "parameters": ["Total Cholesterol"], "severity": severity})

        if "LDL Cholesterol" in abnormal_dict:
            ldl_value = float(abnormal_dict["LDL Cholesterol"]["value"])
            if ldl_value > 100:
                severity = "high" if ldl_value > 160 else "moderate"
                conditions.append({"condition": "High LDL Cholesterol", "parameters": ["LDL Cholesterol"], "severity": severity})

        if "Triglycerides" in abnormal_dict:
            tg_value = float(abnormal_dict["Triglycerides"]["value"])
            if tg_value > 150:
                conditions.append({"condition": "High Triglycerides", "parameters": ["Triglycerides"], "severity": "moderate"})

        # Thyroid issues
        if "TSH" in abnormal_dict:
            tsh_value = float(abnormal_dict["TSH"]["value"])
            if tsh_value < 0.4:
                conditions.append({"condition": "Hyperthyroidism", "parameters": ["TSH"], "severity": "high"})
            elif tsh_value > 4.0:
                severity = "high" if tsh_value > 10.0 else "moderate"
                conditions.append({"condition": "Hypothyroidism", "parameters": ["TSH"], "severity": severity})

        # Liver Stress
        liver_params = ["ALT (SGPT)", "AST (SGOT)", "ALP"]
        elevated_liver = [p for p in liver_params if p in abnormal_dict]
        if elevated_liver:
            severity = "high" if len(elevated_liver) >= 2 else "moderate"
            conditions.append({"condition": "Liver Stress", "parameters": elevated_liver, "severity": severity})

        # Kidney Stress
        if "Creatinine" in abnormal_dict:
            conditions.append({
                "condition": "Kidney Stress",
                "parameters": ["Creatinine"],
                "severity": "high" if abnormal_dict["Creatinine"]["status"] == "critical" else "moderate"
            })
        if "BUN" in abnormal_dict:
            conditions.append({"condition": "Elevated BUN", "parameters": ["BUN"], "severity": "moderate"})

        # Infection / WBC issues
        if "WBC Count" in abnormal_dict:
            wbc_value = float(abnormal_dict["WBC Count"]["value"])
            if wbc_value > 11.0:
                severity = "high" if wbc_value > 15.0 else "moderate"
                conditions.append({"condition": "Possible Infection", "parameters": ["WBC Count"], "severity": severity})
            elif wbc_value < 4.0:
                conditions.append({"condition": "Low WBC Count", "parameters": ["WBC Count"], "severity": "moderate"})

        # Electrolyte Imbalance
        electrolyte_params = ["Sodium", "Potassium", "Calcium"]
        for param in electrolyte_params:
            if param in abnormal_dict:
                conditions.append({
                    "condition": f"Electrolyte Imbalance ({param})",
                    "parameters": [param],
                    "severity": "high" if abnormal_dict[param]["status"] == "critical" else "moderate"
                })

        return conditions

    def generate_recommendations(self, conditions):
        """Generate recommendations based on detected conditions."""
        recommendations = []
        condition_map = {
            "Anemia": "Anemia",
            "Diabetes Risk": "Diabetes Risk",
            "Pre-diabetes": "Diabetes Risk",
            "High Cholesterol": "High Cholesterol",
            "High LDL Cholesterol": "High Cholesterol",
            "High Triglycerides": "High Cholesterol",
            "Hyperthyroidism": "Thyroid Dysfunction",
            "Hypothyroidism": "Thyroid Dysfunction",
            "Liver Stress": "Liver Stress",
            "Kidney Stress": "Kidney Stress",
            "Elevated BUN": "Kidney Stress",
            "Possible Infection": "Infection",
            "Low WBC Count": "Infection",
            "Electrolyte Imbalance": "Inflammation"
        }
        for condition in conditions:
            condition_name = condition["condition"].split(" (")[0]
            mapped = condition_map.get(condition_name, condition_name)
            if mapped in RECOMMENDATIONS:
                rec_data = RECOMMENDATIONS[mapped]
                recommendations.append({
                    "condition": condition["condition"],
                    "severity": condition["severity"],
                    "recommendations": rec_data["recommendations"],
                    "follow_up": rec_data["follow_up"]
                })
        return recommendations

    def generate_summary(self, analysis_results, gender, age):
        """Generate a comprehensive summary."""
        total = (len(analysis_results["normal_parameters"]) +
                 len(analysis_results["abnormal_parameters"]) +
                 len(analysis_results["critical_parameters"]))
        summary = f"### Analysis Summary\n\n"
        summary += f"- **Patient:** {gender.capitalize()}, Age {age}\n"
        summary += f"- **Parameters Analyzed:** {total}\n"
        summary += f"- **Normal Parameters:** {len(analysis_results['normal_parameters'])}\n"
        summary += f"- **Abnormal Parameters:** {len(analysis_results['abnormal_parameters'])}\n"
        summary += f"- **Critical Parameters:** {len(analysis_results['critical_parameters'])}\n\n"
        if analysis_results["conditions_detected"]:
            summary += "**Potential Conditions Detected:**\n"
            for cond in analysis_results["conditions_detected"]:
                emoji = "🔴" if cond['severity'] == 'high' else "🟡"
                summary += f"- {emoji} {cond['condition']} (Severity: {cond['severity']})\n"
        else:
            summary += "✅ No significant abnormalities detected. Parameters are within normal range.\n"
        return summary