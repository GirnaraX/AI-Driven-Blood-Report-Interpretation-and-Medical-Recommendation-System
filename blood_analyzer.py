from reference_data.cbc_reference import CBC_REFERENCE
from reference_data.lipid_reference import LIPID_REFERENCE
from reference_data.liver_reference import LIVER_REFERENCE
from reference_data.kidney_reference import KIDNEY_REFERENCE
from reference_data.thyroid_reference import THYROID_REFERENCE
from reference_data.diabetes_reference import DIABETES_REFERENCE
from reference_data.iron_reference import IRON_REFERENCE
from reference_data.electrolytes_reference import ELECTROLYTES_REFERENCE
from reference_data.recommendations import RECOMMENDATIONS

# Combine all reference ranges
REFERENCE_RANGES = {}
for ref in [CBC_REFERENCE, LIPID_REFERENCE, LIVER_REFERENCE, KIDNEY_REFERENCE,
            THYROID_REFERENCE, DIABETES_REFERENCE, IRON_REFERENCE, ELECTROLYTES_REFERENCE]:
    REFERENCE_RANGES.update(ref)


class BloodReportAnalyzer:
    def __init__(self):
        self.patient_data = {}
        self.results = {}

    def analyze_blood_report(self, report_data, gender, age):
        """Analyze blood report and generate insights"""
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
            if category in REFERENCE_RANGES:
                for param, value in parameters.items():
                    if param in REFERENCE_RANGES[category]:
                        # Get reference range
                        ref_data = REFERENCE_RANGES[category][param]
                        if "all" in ref_data:
                            low, high = ref_data["all"]
                        elif gender in ref_data:
                            low, high = ref_data[gender]
                        else:
                            continue

                        unit = ref_data["unit"]

                        # Check if value is within range
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

        # Detect conditions based on abnormal parameters
        analysis_results["conditions_detected"] = self.detect_conditions(
            analysis_results["abnormal_parameters"] + analysis_results["critical_parameters"],
            gender, age
        )

        # Generate recommendations
        analysis_results["recommendations"] = self.generate_recommendations(
            analysis_results["conditions_detected"]
        )

        # Generate summary
        analysis_results["summary"] = self.generate_summary(
            analysis_results, gender, age
        )

        return analysis_results

    def check_range(self, value, low, high):
        """Check if value is within normal range"""
        try:
            value = float(value) if value is not None else 0
            low = float(low)
            high = float(high)

            if value < low:
                if value < low * 0.7:  # 30% below low
                    return "critical"
                return "low"
            elif value > high:
                if value > high * 1.5:  # 50% above high
                    return "critical"
                return "high"
            else:
                return "normal"
        except (ValueError, TypeError):
            return "unknown"

    def detect_conditions(self, abnormal_params, gender, age):
        """Detect possible medical conditions"""
        conditions = []

        # Create dictionary of abnormal values
        abnormal_dict = {}
        for param in abnormal_params:
            abnormal_dict[param["parameter"]] = {
                "value": param["value"],
                "status": param["status"]
            }

        # Check for Anemia
        if any(param in abnormal_dict for param in ["Hemoglobin", "RBC Count", "Hematocrit"]):
            if "Hemoglobin" in abnormal_dict and abnormal_dict["Hemoglobin"]["status"] in ["low", "critical"]:
                conditions.append({
                    "condition": "Anemia",
                    "parameters": ["Hemoglobin"],
                    "severity": "high" if abnormal_dict["Hemoglobin"]["status"] == "critical" else "moderate"
                })

        # Check for Diabetes
        if "Fasting Glucose" in abnormal_dict:
            try:
                fg_value = float(abnormal_dict["Fasting Glucose"]["value"])
                if fg_value > 126:
                    conditions.append({
                        "condition": "Diabetes Risk",
                        "parameters": ["Fasting Glucose"],
                        "severity": "high"
                    })
                elif fg_value > 100:
                    conditions.append({
                        "condition": "Pre-diabetes",
                        "parameters": ["Fasting Glucose"],
                        "severity": "moderate"
                    })
            except (ValueError, TypeError):
                pass

        if "HbA1c" in abnormal_dict:
            try:
                hba1c_value = float(abnormal_dict["HbA1c"]["value"])
                if hba1c_value > 6.5:
                    conditions.append({
                        "condition": "Diabetes Risk",
                        "parameters": ["HbA1c"],
                        "severity": "high"
                    })
                elif hba1c_value > 5.7:
                    conditions.append({
                        "condition": "Pre-diabetes",
                        "parameters": ["HbA1c"],
                        "severity": "moderate"
                    })
            except (ValueError, TypeError):
                pass

        # Check for High Cholesterol
        if "Total Cholesterol" in abnormal_dict:
            try:
                tc_value = float(abnormal_dict["Total Cholesterol"]["value"])
                if tc_value > 200:
                    severity = "high" if tc_value > 240 else "moderate"
                    conditions.append({
                        "condition": "High Cholesterol",
                        "parameters": ["Total Cholesterol"],
                        "severity": severity
                    })
            except (ValueError, TypeError):
                pass

        if "LDL Cholesterol" in abnormal_dict:
            try:
                ldl_value = float(abnormal_dict["LDL Cholesterol"]["value"])
                if ldl_value > 100:
                    severity = "high" if ldl_value > 160 else "moderate"
                    conditions.append({
                        "condition": "High LDL Cholesterol",
                        "parameters": ["LDL Cholesterol"],
                        "severity": severity
                    })
            except (ValueError, TypeError):
                pass

        if "Triglycerides" in abnormal_dict:
            try:
                tg_value = float(abnormal_dict["Triglycerides"]["value"])
                if tg_value > 150:
                    conditions.append({
                        "condition": "High Triglycerides",
                        "parameters": ["Triglycerides"],
                        "severity": "moderate"
                    })
            except (ValueError, TypeError):
                pass

        # Check for Thyroid issues
        if "TSH" in abnormal_dict:
            try:
                tsh_value = float(abnormal_dict["TSH"]["value"])
                if tsh_value < 0.4:
                    conditions.append({
                        "condition": "Hyperthyroidism",
                        "parameters": ["TSH"],
                        "severity": "high"
                    })
                elif tsh_value > 4.0:
                    severity = "high" if tsh_value > 10.0 else "moderate"
                    conditions.append({
                        "condition": "Hypothyroidism",
                        "parameters": ["TSH"],
                        "severity": severity
                    })
            except (ValueError, TypeError):
                pass

        # Check for Liver issues
        liver_params = ["ALT (SGPT)", "AST (SGOT)", "ALP"]
        elevated_liver = []
        for param in liver_params:
            if param in abnormal_dict:
                elevated_liver.append(param)

        if len(elevated_liver) >= 1:
            severity = "high" if len(elevated_liver) >= 2 else "moderate"
            conditions.append({
                "condition": "Liver Stress",
                "parameters": elevated_liver,
                "severity": severity
            })

        # Check for Kidney issues
        if "Creatinine" in abnormal_dict:
            conditions.append({
                "condition": "Kidney Stress",
                "parameters": ["Creatinine"],
                "severity": "high" if abnormal_dict["Creatinine"]["status"] == "critical" else "moderate"
            })

        if "BUN" in abnormal_dict:
            conditions.append({
                "condition": "Elevated BUN",
                "parameters": ["BUN"],
                "severity": "moderate"
            })

        # Check for Infection
        if "WBC Count" in abnormal_dict:
            try:
                wbc_value = float(abnormal_dict["WBC Count"]["value"])
                if wbc_value > 11.0:
                    severity = "high" if wbc_value > 15.0 else "moderate"
                    conditions.append({
                        "condition": "Possible Infection",
                        "parameters": ["WBC Count"],
                        "severity": severity
                    })
                elif wbc_value < 4.0:
                    conditions.append({
                        "condition": "Low WBC Count",
                        "parameters": ["WBC Count"],
                        "severity": "moderate"
                    })
            except (ValueError, TypeError):
                pass

        # Check for Electrolyte Imbalance
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
        """Generate recommendations based on detected conditions"""
        recommendations = []

        for condition in conditions:
            condition_name = condition["condition"].split(" (")[0]  # Remove subtype if exists
            # Map conditions to recommendation keys
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

            mapped_name = condition_map.get(condition_name, condition_name)
            if mapped_name in RECOMMENDATIONS:
                rec_data = RECOMMENDATIONS[mapped_name]
                recommendations.append({
                    "condition": condition["condition"],
                    "severity": condition["severity"],
                    "recommendations": rec_data["recommendations"],
                    "follow_up": rec_data["follow_up"]
                })

        return recommendations

    def generate_summary(self, analysis_results, gender, age):
        """Generate a comprehensive summary"""
        total_params = (len(analysis_results["normal_parameters"]) +
                       len(analysis_results["abnormal_parameters"]) +
                       len(analysis_results["critical_parameters"]))

        summary = f"### Analysis Summary\n\n"
        summary += f"- **Patient:** {gender.capitalize()}, Age {age}\n"
        summary += f"- **Parameters Analyzed:** {total_params}\n"
        summary += f"- **Normal Parameters:** {len(analysis_results['normal_parameters'])}\n"
        summary += f"- **Abnormal Parameters:** {len(analysis_results['abnormal_parameters'])}\n"
        summary += f"- **Critical Parameters:** {len(analysis_results['critical_parameters'])}\n\n"

        if analysis_results["conditions_detected"]:
            summary += "**Potential Conditions Detected:**\n"
            for condition in analysis_results["conditions_detected"]:
                severity_emoji = "🔴" if condition['severity'] == 'high' else "🟡"
                summary += f"- {severity_emoji} {condition['condition']} (Severity: {condition['severity']})\n"
        else:
            summary += "✅ No significant abnormalities detected. Parameters are within normal range.\n"

        return summary