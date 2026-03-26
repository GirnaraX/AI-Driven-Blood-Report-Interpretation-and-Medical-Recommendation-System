# blood_analyzer.py

# Blood test reference ranges (same as original)
REFERENCE_RANGES = {
    "Complete Blood Count (CBC)": {
        "Hemoglobin": {"male": (13.5, 17.5), "female": (12.0, 16.0), "unit": "g/dL"},
        "RBC Count": {"male": (4.5, 5.9), "female": (4.1, 5.1), "unit": "million/μL"},
        "WBC Count": {"all": (4.0, 11.0), "unit": "thousand/μL"},
        "Platelets": {"all": (150, 450), "unit": "thousand/μL"},
        "Hematocrit": {"male": (40, 54), "female": (36, 48), "unit": "%"},
        "MCV": {"all": (80, 100), "unit": "fL"},
        "MCH": {"all": (27, 33), "unit": "pg"},
        "MCHC": {"all": (32, 36), "unit": "g/dL"},
        "RDW": {"all": (11.5, 14.5), "unit": "%"},
        "Neutrophils": {"all": (40, 75), "unit": "%"},
        "Lymphocytes": {"all": (20, 45), "unit": "%"},
        "Monocytes": {"all": (2, 10), "unit": "%"},
        "Eosinophils": {"all": (1, 6), "unit": "%"},
        "Basophils": {"all": (0, 2), "unit": "%"}
    },
    "Lipid Profile": {
        "Total Cholesterol": {"all": (125, 200), "unit": "mg/dL"},
        "HDL Cholesterol": {"male": (40, 60), "female": (50, 60), "unit": "mg/dL"},
        "LDL Cholesterol": {"all": (0, 100), "unit": "mg/dL"},
        "Triglycerides": {"all": (0, 150), "unit": "mg/dL"},
        "VLDL": {"all": (2, 30), "unit": "mg/dL"},
        "Cholesterol/HDL Ratio": {"all": (3.5, 5.0), "unit": "ratio"}
    },
    "Liver Function": {
        "ALT (SGPT)": {"all": (7, 56), "unit": "U/L"},
        "AST (SGOT)": {"all": (10, 40), "unit": "U/L"},
        "ALP": {"all": (44, 147), "unit": "U/L"},
        "Total Bilirubin": {"all": (0.1, 1.2), "unit": "mg/dL"},
        "Direct Bilirubin": {"all": (0.1, 0.4), "unit": "mg/dL"},
        "Total Protein": {"all": (6.0, 8.3), "unit": "g/dL"},
        "Albumin": {"all": (3.5, 5.0), "unit": "g/dL"},
        "Globulin": {"all": (2.0, 3.5), "unit": "g/dL"},
        "A/G Ratio": {"all": (1.0, 2.2), "unit": "ratio"}
    },
    "Kidney Function": {
        "Creatinine": {"male": (0.7, 1.3), "female": (0.6, 1.1), "unit": "mg/dL"},
        "BUN": {"all": (7, 20), "unit": "mg/dL"},
        "BUN/Creatinine Ratio": {"all": (6, 25), "unit": "ratio"},
        "Uric Acid": {"male": (3.4, 7.0), "female": (2.4, 6.0), "unit": "mg/dL"},
        "eGFR": {"all": (90, 120), "unit": "mL/min/1.73m²"}
    },
    "Thyroid Profile": {
        "TSH": {"all": (0.4, 4.0), "unit": "mIU/L"},
        "T3": {"all": (80, 200), "unit": "ng/dL"},
        "T4": {"all": (5.0, 12.0), "unit": "μg/dL"},
        "Free T3": {"all": (2.3, 4.2), "unit": "pg/mL"},
        "Free T4": {"all": (0.8, 1.8), "unit": "ng/dL"}
    },
    "Diabetes Profile": {
        "Fasting Glucose": {"all": (70, 99), "unit": "mg/dL"},
        "Post Prandial Glucose": {"all": (100, 140), "unit": "mg/dL"},
        "HbA1c": {"all": (4.0, 5.6), "unit": "%"},
        "Random Glucose": {"all": (70, 140), "unit": "mg/dL"}
    },
    "Iron Studies": {
        "Serum Iron": {"male": (65, 176), "female": (50, 170), "unit": "μg/dL"},
        "TIBC": {"all": (250, 450), "unit": "μg/dL"},
        "Ferritin": {"male": (24, 336), "female": (11, 307), "unit": "ng/mL"},
        "Transferrin Saturation": {"male": (20, 50), "female": (15, 50), "unit": "%"}
    },
    "Electrolytes": {
        "Sodium": {"all": (135, 145), "unit": "mmol/L"},
        "Potassium": {"all": (3.5, 5.0), "unit": "mmol/L"},
        "Chloride": {"all": (98, 107), "unit": "mmol/L"},
        "Calcium": {"all": (8.5, 10.2), "unit": "mg/dL"},
        "Magnesium": {"all": (1.7, 2.2), "unit": "mg/dL"},
        "Phosphorus": {"all": (2.5, 4.5), "unit": "mg/dL"}
    }
}

# Medical recommendations database
RECOMMENDATIONS = {
    "Anemia": {
        "condition": "Low hemoglobin, RBC, or hematocrit",
        "recommendations": [
            "Increase iron-rich foods (spinach, lean red meat, beans)",
            "Consider iron supplements after consulting doctor",
            "Include vitamin C for better iron absorption",
            "Avoid tea/coffee with meals"
        ],
        "severity": "moderate",
        "follow_up": "Repeat blood test in 3 months"
    },
    "High Cholesterol": {
        "condition": "Elevated total cholesterol or LDL",
        "recommendations": [
            "Reduce saturated fats and trans fats",
            "Increase soluble fiber (oats, fruits, vegetables)",
            "Regular aerobic exercise (30 mins/day)",
            "Consider plant sterols/stanols"
        ],
        "severity": "moderate",
        "follow_up": "Repeat lipid profile in 3-6 months"
    },
    "Diabetes Risk": {
        "condition": "Elevated fasting glucose or HbA1c",
        "recommendations": [
            "Monitor carbohydrate intake",
            "Regular physical activity",
            "Maintain healthy weight",
            "Limit sugary foods and beverages"
        ],
        "severity": "high",
        "follow_up": "Consult doctor for glucose tolerance test"
    },
    "Thyroid Dysfunction": {
        "condition": "Abnormal TSH levels",
        "recommendations": [
            "Consult endocrinologist",
            "Take prescribed medication regularly",
            "Avoid soy and high-iodine foods if hyperthyroid",
            "Regular thyroid function monitoring"
        ],
        "severity": "moderate",
        "follow_up": "Repeat thyroid profile in 6-8 weeks"
    },
    "Liver Stress": {
        "condition": "Elevated liver enzymes",
        "recommendations": [
            "Avoid alcohol completely",
            "Reduce fatty foods",
            "Stay hydrated",
            "Review medications with doctor"
        ],
        "severity": "high",
        "follow_up": "Repeat LFT in 4-6 weeks"
    },
    "Kidney Stress": {
        "condition": "Elevated creatinine or BUN",
        "recommendations": [
            "Stay well hydrated",
            "Limit protein intake",
            "Avoid NSAIDs",
            "Monitor blood pressure"
        ],
        "severity": "high",
        "follow_up": "Repeat kidney function test in 2-4 weeks"
    },
    "Infection": {
        "condition": "Elevated WBC count",
        "recommendations": [
            "Get adequate rest",
            "Increase fluid intake",
            "Monitor temperature",
            "Consult doctor if symptoms persist"
        ],
        "severity": "moderate",
        "follow_up": "Repeat CBC after treatment"
    },
    "Inflammation": {
        "condition": "Abnormal ESR or CRP",
        "recommendations": [
            "Anti-inflammatory diet",
            "Regular exercise",
            "Stress management",
            "Consult rheumatologist if persistent"
        ],
        "severity": "moderate",
        "follow_up": "Monitor symptoms and repeat tests"
    }
}


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