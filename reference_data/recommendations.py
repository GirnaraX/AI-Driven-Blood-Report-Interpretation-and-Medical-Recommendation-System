# recommendations.py

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