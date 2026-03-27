# app.py
import streamlit as st
import pandas as pd
import numpy as np

import plotly.express as px
from datetime import datetime
import json
import os
import base64
from io import BytesIO

# Import backend modules
from blood_analyzer import BloodReportAnalyzer, REFERENCE_RANGES
from storage import save_analysis_record


# Page configuration
st.set_page_config(
    page_title="AI Blood Report Analyzer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize analyzer
analyzer = BloodReportAnalyzer()

# Initialize session state
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'report_data' not in st.session_state:
    st.session_state.report_data = None
if 'patient_info' not in st.session_state:
    st.session_state.patient_info = None
if 'analyze_clicked' not in st.session_state:
    st.session_state.analyze_clicked = False
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Load custom CSS
with open('styles.css', 'r') as f:
    css = f.read()
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

def get_table_download_link(df, filename, text):
    """Generate a download link for dataframe"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def generate_html_report(patient_info, report_data, results):
    """Generate HTML report for printing"""
    patient_name = patient_info.get('name', 'Unknown') if patient_info else 'Unknown'
    patient_age = patient_info.get('age', 'Unknown') if patient_info else 'Unknown'
    patient_gender = patient_info.get('gender', 'Unknown') if patient_info else 'Unknown'
    patient_blood_group = patient_info.get('blood_group', 'Unknown') if patient_info else 'Unknown'
    patient_report_date = patient_info.get('report_date', 'Unknown') if patient_info else 'Unknown'

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Blood Report Analysis - {patient_name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
            h1 {{ color: #2c3e50; text-align: center; }}
            h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
            .patient-info {{ background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; }}
            .normal {{ color: #27ae60; }}
            .abnormal {{ color: #e67e22; }}
            .critical {{ color: #e74c3c; font-weight: bold; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #3498db; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .recommendation {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #3498db; }}
            .footer {{ text-align: center; margin-top: 40px; font-size: 0.9em; color: #7f8c8d; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🩺 AI-Driven Blood Report Analysis</h1>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="patient-info">
            <h2>Patient Information</h2>
            <p><strong>Name:</strong> {patient_name}</p>
            <p><strong>Age:</strong> {patient_age}</p>
            <p><strong>Gender:</strong> {patient_gender}</p>
            <p><strong>Blood Group:</strong> {patient_blood_group}</p>
            <p><strong>Report Date:</strong> {patient_report_date}</p>
        </div>

        <h2>Analysis Summary</h2>
        {results.get('summary', 'No summary available')}

        <h2>Detailed Results</h2>
        <table>
            <tr>
                <th>Category</th>
                <th>Parameter</th>
                <th>Value</th>
                <th>Normal Range</th>
                <th>Unit</th>
                <th>Status</th>
            </tr>
    """

    # Add normal parameters
    for param in results.get("normal_parameters", []):
        html_content += f"""
            <tr class="normal">
                <td>{param.get('category', '')}</td>
                <td>{param.get('parameter', '')}</td>
                <td>{param.get('value', '')}</td>
                <td>{param.get('low', '')} - {param.get('high', '')}</td>
                <td>{param.get('unit', '')}</td>
                <td>Normal</td>
            </tr>
        """

    # Add abnormal parameters
    for param in results.get("abnormal_parameters", []):
        html_content += f"""
            <tr class="abnormal">
                <td>{param.get('category', '')}</td>
                <td>{param.get('parameter', '')}</td>
                <td>{param.get('value', '')}</td>
                <td>{param.get('low', '')} - {param.get('high', '')}</td>
                <td>{param.get('unit', '')}</td>
                <td>{param.get('status', '').upper()}</td>
            </tr>
        """

    # Add critical parameters
    for param in results.get("critical_parameters", []):
        html_content += f"""
            <tr class="critical">
                <td>{param.get('category', '')}</td>
                <td>{param.get('parameter', '')}</td>
                <td>{param.get('value', '')}</td>
                <td>{param.get('low', '')} - {param.get('high', '')}</td>
                <td>{param.get('unit', '')}</td>
                <td>CRITICAL</td>
            </tr>
        """

    html_content += """
        </table>

        <h2>Recommendations</h2>
    """

    if results.get("recommendations"):
        for rec in results["recommendations"]:
            severity_color = "#dc3545" if rec.get('severity') == 'high' else "#ffc107"
            html_content += f"""
                <div class="recommendation">
                    <h3 style="color: {severity_color};">{rec.get('condition', '')}</h3>
                    <p><strong>Severity:</strong> {rec.get('severity', '').upper()}</p>
                    <ul>
            """
            for recommendation in rec.get("recommendations", []):
                html_content += f"<li>{recommendation}</li>"
            html_content += f"""
                    </ul>
                    <p><strong>Follow-up:</strong> {rec.get('follow_up', '')}</p>
                </div>
            """
    else:
        html_content += """
            <div class="recommendation">
                <p>No specific recommendations. Maintain your healthy lifestyle!</p>
            </div>
        """

    html_content += """
        <div class="footer">
            <p>This report is generated by AI and should be reviewed by a healthcare professional.</p>
            <p>© 2024 AI Blood Report Analyzer</p>
        </div>
    </body>
    </html>
    """

    return html_content

def update_chat_context():
    """Update the AI chat context with the latest analysis results."""
    if (st.session_state.get('analysis_results') and 
        st.session_state.get('patient_info') and 
        st.session_state.get('report_data') and 
        st.session_state.get('chat')):
        st.session_state.chat.set_context(
            st.session_state.patient_info,
            st.session_state.report_data,
            st.session_state.analysis_results
        )

def main():
    st.markdown('<h1 class="main-header">🩺 AI-Driven Blood Report Interpretation System</h1>',
                unsafe_allow_html=True)

    # Initialize analyzer
    analyzer = BloodReportAnalyzer()

    # Sidebar for patient information and API key
    with st.sidebar:
        st.markdown("## 👤 Patient Information")
        patient_name = st.text_input("Patient Name", key="patient_name")
        age = st.number_input("Age", min_value=0, max_value=120, key="age")
        gender = st.selectbox("Gender", ["male", "female"], key="gender")
        blood_group = st.selectbox("Blood Group",
                                   ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                                   key="blood_group")

        st.markdown("---")
        st.markdown("## 📋 Report Date")
        report_date = st.date_input("Test Date", datetime.now(), key="report_date")

        st.markdown("---")
        st.markdown("## ℹ️ About")
        st.info(
            "This AI-powered system analyzes blood test reports and provides "
            "personalized medical recommendations. Always consult with a "
            "healthcare professional for proper diagnosis."
        )

    # Main content area: 5 tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Input Report", "🔍 Analysis Results", "📈 Visualizations", "📥 Export Report", "💬 AI Assistant"
    ])

    with tab1:
        st.markdown('<h2 class="sub-header">Enter Blood Test Parameters</h2>',
                    unsafe_allow_html=True)

        input_tabs = st.tabs([
            "Complete Blood Count (CBC)",
            "Lipid Profile",
            "Liver Function",
            "Kidney Function",
            "Thyroid Profile",
            "Diabetes Profile",
            "Iron Studies",
            "Electrolytes"
        ])

        # CBC Tab
        with input_tabs[0]:
            st.markdown("### 🩸 Complete Blood Count")
            cbc_data = {}
            cbc_data["Hemoglobin"] = st.number_input("Hemoglobin (g/dL)", min_value=0.0, max_value=25.0, value=14.0, step=0.1, key="hb")
            cbc_data["RBC Count"] = st.number_input("RBC Count (million/μL)", min_value=0.0, max_value=8.0, value=4.8, step=0.1, key="rbc")
            cbc_data["WBC Count"] = st.number_input("WBC Count (thousand/μL)", min_value=0.0, max_value=30.0, value=7.5, step=0.1, key="wbc")
            cbc_data["Platelets"] = st.number_input("Platelets (thousand/μL)", min_value=0, max_value=800, value=250, step=5, key="plt")
            cbc_data["Hematocrit"] = st.number_input("Hematocrit (%)", min_value=0.0, max_value=70.0, value=42.0, step=0.1, key="hct")
            cbc_data["MCV"] = st.number_input("MCV (fL)", min_value=50.0, max_value=120.0, value=90.0, step=0.1, key="mcv")
            cbc_data["MCH"] = st.number_input("MCH (pg)", min_value=20.0, max_value=40.0, value=30.0, step=0.1, key="mch")
            cbc_data["MCHC"] = st.number_input("MCHC (g/dL)", min_value=25.0, max_value=40.0, value=33.0, step=0.1, key="mchc")
            cbc_data["RDW"] = st.number_input("RDW (%)", min_value=10.0, max_value=20.0, value=13.0, step=0.1, key="rdw")
            cbc_data["Neutrophils"] = st.number_input("Neutrophils (%)", min_value=0, max_value=100, value=60, step=1, key="neut")
            cbc_data["Lymphocytes"] = st.number_input("Lymphocytes (%)", min_value=0, max_value=100, value=30, step=1, key="lymp")
            cbc_data["Monocytes"] = st.number_input("Monocytes (%)", min_value=0, max_value=20, value=5, step=1, key="mono")
            cbc_data["Eosinophils"] = st.number_input("Eosinophils (%)", min_value=0, max_value=10, value=2, step=1, key="eos")
            cbc_data["Basophils"] = st.number_input("Basophils (%)", min_value=0, max_value=5, value=1, step=1, key="baso")

            if st.button("🔬 Analyze CBC Report", key="analyze_cbc"):
                category_data = {"Complete Blood Count (CBC)": cbc_data}
                if 'accumulated_report_data' not in st.session_state:
                    st.session_state.accumulated_report_data = {}
                st.session_state.accumulated_report_data.update(category_data)
                st.session_state.report_data = st.session_state.accumulated_report_data
                st.session_state.patient_info = {
                    "name": patient_name,
                    "age": age,
                    "gender": gender,
                    "blood_group": blood_group,
                    "report_date": str(report_date)
                }
                with st.spinner("Analyzing accumulated blood report..."):
                    results = analyzer.analyze_blood_report(st.session_state.report_data, gender, age)
                    st.session_state.analysis_results = results
                    st.session_state.analyze_clicked = True
                    st.session_state.analysis_done = True
                    save_analysis_record(st.session_state.patient_info, st.session_state.report_data, results)
                    update_chat_context()
                st.success("✅ CBC data added! Analysis updated with all accumulated categories.")

        # Lipid Profile Tab
        with input_tabs[1]:
            st.markdown("### 💊 Lipid Profile")
            lipid_data = {}
            lipid_data["Total Cholesterol"] = st.number_input("Total Cholesterol (mg/dL)", min_value=0, max_value=400, value=180, step=5, key="tc")
            lipid_data["HDL Cholesterol"] = st.number_input("HDL Cholesterol (mg/dL)", min_value=0, max_value=100, value=50, step=1, key="hdl")
            lipid_data["LDL Cholesterol"] = st.number_input("LDL Cholesterol (mg/dL)", min_value=0, max_value=300, value=100, step=5, key="ldl")
            lipid_data["Triglycerides"] = st.number_input("Triglycerides (mg/dL)", min_value=0, max_value=500, value=120, step=5, key="tg")
            lipid_data["VLDL"] = st.number_input("VLDL (mg/dL)", min_value=0, max_value=50, value=20, step=1, key="vldl")
            lipid_data["Cholesterol/HDL Ratio"] = st.number_input("Cholesterol/HDL Ratio", min_value=0.0, max_value=10.0, value=3.6, step=0.1, key="chol_ratio")

            if st.button("🔬 Analyze Lipid Profile Report", key="analyze_lipid"):
                category_data = {"Lipid Profile": lipid_data}
                if 'accumulated_report_data' not in st.session_state:
                    st.session_state.accumulated_report_data = {}
                st.session_state.accumulated_report_data.update(category_data)
                st.session_state.report_data = st.session_state.accumulated_report_data
                st.session_state.patient_info = {
                    "name": patient_name,
                    "age": age,
                    "gender": gender,
                    "blood_group": blood_group,
                    "report_date": str(report_date)
                }
                with st.spinner("Analyzing accumulated blood report..."):
                    results = analyzer.analyze_blood_report(st.session_state.report_data, gender, age)
                    st.session_state.analysis_results = results
                    st.session_state.analyze_clicked = True
                    st.session_state.analysis_done = True
                    save_analysis_record(st.session_state.patient_info, st.session_state.report_data, results)
                    update_chat_context()
                st.success("✅ Lipid Profile data added! Analysis updated with all accumulated categories.")

        # Liver Function Tab
        with input_tabs[2]:
            st.markdown("### 🫁 Liver Function")
            liver_data = {}
            liver_data["ALT (SGPT)"] = st.number_input("ALT (SGPT) (U/L)", min_value=0, max_value=500, value=30, step=1, key="alt")
            liver_data["AST (SGOT)"] = st.number_input("AST (SGOT) (U/L)", min_value=0, max_value=500, value=28, step=1, key="ast")
            liver_data["ALP"] = st.number_input("ALP (U/L)", min_value=0, max_value=500, value=85, step=5, key="alp")
            liver_data["Total Bilirubin"] = st.number_input("Total Bilirubin (mg/dL)", min_value=0.0, max_value=10.0, value=0.8, step=0.1, key="bili")
            liver_data["Direct Bilirubin"] = st.number_input("Direct Bilirubin (mg/dL)", min_value=0.0, max_value=5.0, value=0.2, step=0.1, key="dir_bili")
            liver_data["Total Protein"] = st.number_input("Total Protein (g/dL)", min_value=0.0, max_value=10.0, value=7.0, step=0.1, key="tprot")
            liver_data["Albumin"] = st.number_input("Albumin (g/dL)", min_value=0.0, max_value=6.0, value=4.0, step=0.1, key="alb")
            liver_data["Globulin"] = st.number_input("Globulin (g/dL)", min_value=0.0, max_value=5.0, value=2.5, step=0.1, key="glob")
            liver_data["A/G Ratio"] = st.number_input("A/G Ratio", min_value=0.0, max_value=3.0, value=1.6, step=0.1, key="ag_ratio")

            if st.button("🔬 Analyze Liver Function Report", key="analyze_liver"):
                category_data = {"Liver Function": liver_data}
                if 'accumulated_report_data' not in st.session_state:
                    st.session_state.accumulated_report_data = {}
                st.session_state.accumulated_report_data.update(category_data)
                st.session_state.report_data = st.session_state.accumulated_report_data
                st.session_state.patient_info = {
                    "name": patient_name,
                    "age": age,
                    "gender": gender,
                    "blood_group": blood_group,
                    "report_date": str(report_date)
                }
                with st.spinner("Analyzing accumulated blood report..."):
                    results = analyzer.analyze_blood_report(st.session_state.report_data, gender, age)
                    st.session_state.analysis_results = results
                    st.session_state.analyze_clicked = True
                    st.session_state.analysis_done = True
                    save_analysis_record(st.session_state.patient_info, st.session_state.report_data, results)
                    update_chat_context()
                st.success("✅ Liver Function data added! Analysis updated with all accumulated categories.")

        # Kidney Function Tab
        with input_tabs[3]:
            st.markdown("### 🫀 Kidney Function")
            kidney_data = {}
            kidney_data["Creatinine"] = st.number_input("Creatinine (mg/dL)", min_value=0.0, max_value=10.0, value=0.9, step=0.1, key="creat")
            kidney_data["BUN"] = st.number_input("BUN (mg/dL)", min_value=0, max_value=100, value=15, step=1, key="bun")
            kidney_data["BUN/Creatinine Ratio"] = st.number_input("BUN/Creatinine Ratio", min_value=0, max_value=50, value=17, step=1, key="bun_creat")
            kidney_data["Uric Acid"] = st.number_input("Uric Acid (mg/dL)", min_value=0.0, max_value=15.0, value=5.0, step=0.1, key="uric")
            kidney_data["eGFR"] = st.number_input("eGFR (mL/min/1.73m²)", min_value=0, max_value=150, value=100, step=1, key="egfr")

            if st.button("🔬 Analyze Kidney Function Report", key="analyze_kidney"):
                category_data = {"Kidney Function": kidney_data}
                if 'accumulated_report_data' not in st.session_state:
                    st.session_state.accumulated_report_data = {}
                st.session_state.accumulated_report_data.update(category_data)
                st.session_state.report_data = st.session_state.accumulated_report_data
                st.session_state.patient_info = {
                    "name": patient_name,
                    "age": age,
                    "gender": gender,
                    "blood_group": blood_group,
                    "report_date": str(report_date)
                }
                with st.spinner("Analyzing accumulated blood report..."):
                    results = analyzer.analyze_blood_report(st.session_state.report_data, gender, age)
                    st.session_state.analysis_results = results
                    st.session_state.analyze_clicked = True
                    st.session_state.analysis_done = True
                    save_analysis_record(st.session_state.patient_info, st.session_state.report_data, results)
                    update_chat_context()
                st.success("✅ Kidney Function data added! Analysis updated with all accumulated categories.")

        # Thyroid Profile Tab
        with input_tabs[4]:
            st.markdown("### ⚡ Thyroid Profile")
            thyroid_data = {}
            thyroid_data["TSH"] = st.number_input("TSH (mIU/L)", min_value=0.0, max_value=20.0, value=2.5, step=0.1, key="tsh")
            thyroid_data["T3"] = st.number_input("T3 (ng/dL)", min_value=0, max_value=500, value=120, step=5, key="t3")
            thyroid_data["T4"] = st.number_input("T4 (μg/dL)", min_value=0.0, max_value=20.0, value=8.0, step=0.1, key="t4")
            thyroid_data["Free T3"] = st.number_input("Free T3 (pg/mL)", min_value=0.0, max_value=10.0, value=3.0, step=0.1, key="ft3")
            thyroid_data["Free T4"] = st.number_input("Free T4 (ng/dL)", min_value=0.0, max_value=3.0, value=1.2, step=0.1, key="ft4")

            if st.button("🔬 Analyze Thyroid Profile Report", key="analyze_thyroid"):
                category_data = {"Thyroid Profile": thyroid_data}
                if 'accumulated_report_data' not in st.session_state:
                    st.session_state.accumulated_report_data = {}
                st.session_state.accumulated_report_data.update(category_data)
                st.session_state.report_data = st.session_state.accumulated_report_data
                st.session_state.patient_info = {
                    "name": patient_name,
                    "age": age,
                    "gender": gender,
                    "blood_group": blood_group,
                    "report_date": str(report_date)
                }
                with st.spinner("Analyzing accumulated blood report..."):
                    results = analyzer.analyze_blood_report(st.session_state.report_data, gender, age)
                    st.session_state.analysis_results = results
                    st.session_state.analyze_clicked = True
                    st.session_state.analysis_done = True
                    save_analysis_record(st.session_state.patient_info, st.session_state.report_data, results)
                    update_chat_context()
                st.success("✅ Thyroid Profile data added! Analysis updated with all accumulated categories.")

        # Diabetes Profile Tab
        with input_tabs[5]:
            st.markdown("### 🍬 Diabetes Profile")
            diabetes_data = {}
            diabetes_data["Fasting Glucose"] = st.number_input("Fasting Glucose (mg/dL)", min_value=0, max_value=400, value=95, step=5, key="glu")
            diabetes_data["Post Prandial Glucose"] = st.number_input("Post Prandial Glucose (mg/dL)", min_value=0, max_value=400, value=120, step=5, key="pp_glu")
            diabetes_data["HbA1c"] = st.number_input("HbA1c (%)", min_value=0.0, max_value=15.0, value=5.2, step=0.1, key="a1c")
            diabetes_data["Random Glucose"] = st.number_input("Random Glucose (mg/dL)", min_value=0, max_value=400, value=100, step=5, key="rand_glu")

            if st.button("🔬 Analyze Diabetes Profile Report", key="analyze_diabetes"):
                category_data = {"Diabetes Profile": diabetes_data}
                if 'accumulated_report_data' not in st.session_state:
                    st.session_state.accumulated_report_data = {}
                st.session_state.accumulated_report_data.update(category_data)
                st.session_state.report_data = st.session_state.accumulated_report_data
                st.session_state.patient_info = {
                    "name": patient_name,
                    "age": age,
                    "gender": gender,
                    "blood_group": blood_group,
                    "report_date": str(report_date)
                }
                with st.spinner("Analyzing accumulated blood report..."):
                    results = analyzer.analyze_blood_report(st.session_state.report_data, gender, age)
                    st.session_state.analysis_results = results
                    st.session_state.analyze_clicked = True
                    st.session_state.analysis_done = True
                    save_analysis_record(st.session_state.patient_info, st.session_state.report_data, results)
                    update_chat_context()
                st.success("✅ Diabetes Profile data added! Analysis updated with all accumulated categories.")

        # Iron Studies Tab
        with input_tabs[6]:
            st.markdown("### 🩸 Iron Studies")
            iron_data = {}
            iron_data["Serum Iron"] = st.number_input("Serum Iron (μg/dL)", min_value=0, max_value=200, value=100, step=5, key="serum_iron")
            iron_data["TIBC"] = st.number_input("TIBC (μg/dL)", min_value=200, max_value=500, value=300, step=5, key="tibc")
            iron_data["Ferritin"] = st.number_input("Ferritin (ng/mL)", min_value=0, max_value=500, value=100, step=5, key="ferritin")
            iron_data["Transferrin Saturation"] = st.number_input("Transferrin Saturation (%)", min_value=0, max_value=100, value=30, step=1, key="tsat")

            if st.button("🔬 Analyze Iron Studies Report", key="analyze_iron"):
                category_data = {"Iron Studies": iron_data}
                if 'accumulated_report_data' not in st.session_state:
                    st.session_state.accumulated_report_data = {}
                st.session_state.accumulated_report_data.update(category_data)
                st.session_state.report_data = st.session_state.accumulated_report_data
                st.session_state.patient_info = {
                    "name": patient_name,
                    "age": age,
                    "gender": gender,
                    "blood_group": blood_group,
                    "report_date": str(report_date)
                }
                with st.spinner("Analyzing accumulated blood report..."):
                    results = analyzer.analyze_blood_report(st.session_state.report_data, gender, age)
                    st.session_state.analysis_results = results
                    st.session_state.analyze_clicked = True
                    st.session_state.analysis_done = True
                    save_analysis_record(st.session_state.patient_info, st.session_state.report_data, results)
                    update_chat_context()
                st.success("✅ Iron Studies data added! Analysis updated with all accumulated categories.")

        # Electrolytes Tab
        with input_tabs[7]:
            st.markdown("### 💧 Electrolytes")
            electrolyte_data = {}
            electrolyte_data["Sodium"] = st.number_input("Sodium (mmol/L)", min_value=100, max_value=160, value=140, step=1, key="na")
            electrolyte_data["Potassium"] = st.number_input("Potassium (mmol/L)", min_value=2.0, max_value=8.0, value=4.2, step=0.1, key="k")
            electrolyte_data["Chloride"] = st.number_input("Chloride (mmol/L)", min_value=80, max_value=120, value=100, step=1, key="cl")
            electrolyte_data["Calcium"] = st.number_input("Calcium (mg/dL)", min_value=5.0, max_value=15.0, value=9.2, step=0.1, key="ca")
            electrolyte_data["Magnesium"] = st.number_input("Magnesium (mg/dL)", min_value=1.0, max_value=3.0, value=2.0, step=0.1, key="mg")
            electrolyte_data["Phosphorus"] = st.number_input("Phosphorus (mg/dL)", min_value=1.0, max_value=6.0, value=3.5, step=0.1, key="phos")

            if st.button("🔬 Analyze Electrolytes Report", key="analyze_electrolytes"):
                category_data = {"Electrolytes": electrolyte_data}
                if 'accumulated_report_data' not in st.session_state:
                    st.session_state.accumulated_report_data = {}
                st.session_state.accumulated_report_data.update(category_data)
                st.session_state.report_data = st.session_state.accumulated_report_data
                st.session_state.patient_info = {
                    "name": patient_name,
                    "age": age,
                    "gender": gender,
                    "blood_group": blood_group,
                    "report_date": str(report_date)
                }
                with st.spinner("Analyzing accumulated blood report..."):
                    results = analyzer.analyze_blood_report(st.session_state.report_data, gender, age)
                    st.session_state.analysis_results = results
                    st.session_state.analyze_clicked = True
                    st.session_state.analysis_done = True
                    save_analysis_record(st.session_state.patient_info, st.session_state.report_data, results)
                    update_chat_context()
                st.success("✅ Electrolytes data added! Analysis updated with all accumulated categories.")

        # Display accumulated categories
        if 'accumulated_report_data' in st.session_state and st.session_state.accumulated_report_data:
            st.markdown("### 📋 Accumulated Categories for Analysis:")
            accumulated_cats = list(st.session_state.accumulated_report_data.keys())
            st.write("Currently analyzing: " + ", ".join(accumulated_cats))

        # Reset button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Reset Analysis", use_container_width=True, key="reset_analysis"):
                if 'accumulated_report_data' in st.session_state:
                    del st.session_state.accumulated_report_data
                if 'report_data' in st.session_state:
                    del st.session_state.report_data
                if 'analysis_results' in st.session_state:
                    del st.session_state.analysis_results
                if 'patient_info' in st.session_state:
                    del st.session_state.patient_info
                st.session_state.analyze_clicked = False
                st.session_state.analysis_done = False
                st.session_state.chat_history = []  # Clear chat history on reset
                st.success("✅ Analysis reset! You can start fresh.")

    with tab2:
        if st.session_state.get('analysis_results') and st.session_state.get('analyze_clicked', False):
            results = st.session_state.get('analysis_results')
            st.markdown(results["summary"])
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Normal Parameters", len(results["normal_parameters"]))
            with col2:
                st.metric("Abnormal Parameters", len(results["abnormal_parameters"]))
            with col3:
                st.metric("Critical Parameters", len(results["critical_parameters"]))
            if results["normal_parameters"]:
                with st.expander("✅ Normal Parameters", expanded=False):
                    for param in results["normal_parameters"]:
                        st.markdown(f"""
                        <div style='padding:10px;margin:5px 0;background:#d4edda;border-radius:5px;'>
                            <strong>{param['parameter']}:</strong> {param['value']} {param['unit']} (Range: {param['low']}-{param['high']})
                        </div>
                        """, unsafe_allow_html=True)
            if results["abnormal_parameters"]:
                with st.expander("⚠️ Abnormal Parameters", expanded=True):
                    for param in results["abnormal_parameters"]:
                        st.markdown(f"""
                        <div style='padding:10px;margin:5px 0;background:#fff3cd;border-radius:5px;'>
                            <strong>{param['parameter']}:</strong> {param['value']} {param['unit']} (Normal: {param['low']}-{param['high']}) - {param['status'].upper()}
                        </div>
                        """, unsafe_allow_html=True)
            if results["critical_parameters"]:
                with st.expander("🚨 Critical Parameters", expanded=True):
                    for param in results["critical_parameters"]:
                        st.markdown(f"""
                        <div style='padding:10px;margin:5px 0;background:#f8d7da;border-radius:5px;'>
                            <strong>{param['parameter']}:</strong> {param['value']} {param['unit']} (Normal: {param['low']}-{param['high']}) - CRITICAL
                        </div>
                        """, unsafe_allow_html=True)
            if results["conditions_detected"]:
                st.markdown("### 🏥 Potential Conditions & Recommendations")
                for condition in results["conditions_detected"]:
                    box_class = "danger-box" if condition['severity'] == 'high' else "warning-box"
                    severity_emoji = "🔴" if condition['severity'] == 'high' else "🟡"
                    st.markdown(f"""
                    <div class="{box_class}">
                        <h4>{severity_emoji} {condition['condition']}</h4>
                        <p><strong>Severity:</strong> {condition['severity'].upper()}</p>
                        <p><strong>Affected Parameters:</strong> {', '.join(condition['parameters'])}</p>
                    </div>
                    """, unsafe_allow_html=True)
                for rec in results["recommendations"]:
                    st.markdown(f"#### Recommendations for {rec['condition']}:")
                    for i, rec_text in enumerate(rec["recommendations"], 1):
                        st.markdown(f"{i}. {rec_text}")
                    st.markdown(f"**Follow-up:** {rec['follow_up']}")
                    st.markdown("---")
            else:
                st.markdown("""
                <div class="success-box">
                    <h4>✅ No significant health issues detected!</h4>
                    <p>Maintain your healthy lifestyle and continue regular check-ups.</p>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("### 💪 General Health Tips")
            tips_col1, tips_col2, tips_col3 = st.columns(3)
            with tips_col1:
                st.info("🥗 **Diet**\n- Eat balanced meals\n- Include fruits & vegetables\n- Stay hydrated")
            with tips_col2:
                st.info("🏃 **Exercise**\n- 30 mins daily activity\n- Mix cardio & strength\n- Stay active")
            with tips_col3:
                st.info("😴 **Lifestyle**\n- 7-8 hours sleep\n- Stress management\n- Regular check-ups")
        else:
            st.info("👈 Please enter blood report parameters and click 'Analyze Blood Report' in the Input Report tab")

    with tab3:
        if st.session_state.get('analysis_results') and st.session_state.get('analyze_clicked', False) and st.session_state.get('report_data'):
            results = st.session_state.get('analysis_results')
            report_data = st.session_state.get('report_data')
            gender = st.session_state.get('patient_info', {}).get('gender', 'male')
            st.markdown('<h2 class="sub-header">📊 Visual Analysis</h2>', unsafe_allow_html=True)
            categories = list(report_data.keys())
            for category in categories:
                if category in REFERENCE_RANGES:
                    st.markdown(f"### {category}")
                    params = []
                    values = []
                    ranges_low = []
                    ranges_high = []
                    colors = []
                    for param, value in report_data[category].items():
                        if param in REFERENCE_RANGES[category]:
                            ref_data = REFERENCE_RANGES[category][param]
                            if "all" in ref_data:
                                low, high = ref_data["all"]
                            elif gender in ref_data:
                                low, high = ref_data[gender]
                            else:
                                continue
                            params.append(param)
                            values.append(value)
                            ranges_low.append(low)
                            ranges_high.append(high)
                            try:
                                val = float(value)
                                if val < low or val > high:
                                    colors.append('orange')
                                else:
                                    colors.append('green')
                            except:
                                colors.append('gray')
                    if params:
                        fig = go.Figure()
                        fig.add_trace(go.Bar(
                            name='Your Value',
                            x=params,
                            y=values,
                            marker_color=colors,
                            text=[f"{v:.1f}" if isinstance(v, (int, float)) else str(v) for v in values],
                            textposition='outside',
                        ))
                        for i, param in enumerate(params):
                            fig.add_shape(type="line", x0=i-0.4, y0=ranges_low[i], x1=i+0.4, y1=ranges_low[i],
                                          line=dict(color="blue", width=2, dash="dash"))
                            fig.add_shape(type="line", x0=i-0.4, y0=ranges_high[i], x1=i+0.4, y1=ranges_high[i],
                                          line=dict(color="blue", width=2, dash="dash"))
                        fig.update_layout(title=f"{category} Analysis", xaxis_title="Parameters", yaxis_title="Value",
                                          showlegend=False, height=400, bargap=0.2)
                        st.plotly_chart(fig, use_container_width=True)
            # Radar chart
            st.markdown("### 🎯 Overall Health Assessment")
            key_params = {
                "Hemoglobin": "CBC",
                "WBC Count": "CBC",
                "Platelets": "CBC",
                "Total Cholesterol": "Lipid",
                "HDL Cholesterol": "Lipid",
                "ALT (SGPT)": "Liver",
                "Creatinine": "Kidney",
                "TSH": "Thyroid",
                "Fasting Glucose": "Diabetes",
                "Sodium": "Electrolytes"
            }
            radar_values = []
            radar_categories = []
            for param, cat in key_params.items():
                for cat_name, cat_data in report_data.items():
                    if param in cat_data:
                        try:
                            value = float(cat_data[param])
                            for ref_cat, ref_params in REFERENCE_RANGES.items():
                                if param in ref_params:
                                    ref_data = ref_params[param]
                                    if "all" in ref_data:
                                        low, high = ref_data["all"]
                                    elif gender in ref_data:
                                        low, high = ref_data[gender]
                                    else:
                                        continue
                                    if low <= value <= high:
                                        health_score = 100
                                    elif value < low:
                                        health_score = max(0, 100 * (value / low))
                                    else:
                                        health_score = max(0, 100 * (high / value))
                                    radar_values.append(health_score)
                                    radar_categories.append(param)
                                    break
                        except:
                            pass
            if radar_values:
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=radar_values, theta=radar_categories, fill='toself',
                                              name='Health Score', line_color='rgba(52,152,219,0.8)',
                                              fillcolor='rgba(52,152,219,0.3)'))
                fig.add_trace(go.Scatterpolar(r=[100]*len(radar_categories), theta=radar_categories, fill='none',
                                              name='Ideal', line=dict(color='green', dash='dash')))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,100],
                                                             tickmode='array', tickvals=[20,40,60,80,100],
                                                             ticktext=['Poor','Fair','Good','Very Good','Excellent'])),
                                  showlegend=True, height=500, title="Health Score Radar Chart")
                st.plotly_chart(fig, use_container_width=True)
                avg_score = np.mean(radar_values)
                if avg_score >= 90:
                    st.success(f"🌟 **Overall Health Score: {avg_score:.1f}/100 - Excellent!**")
                elif avg_score >= 70:
                    st.info(f"👍 **Overall Health Score: {avg_score:.1f}/100 - Good**")
                elif avg_score >= 50:
                    st.warning(f"⚠️ **Overall Health Score: {avg_score:.1f}/100 - Fair**")
                else:
                    st.error(f"🚨 **Overall Health Score: {avg_score:.1f}/100 - Needs Attention**")
        else:
            st.info("👈 Please analyze a report first to see visualizations")

    with tab4:
        if st.session_state.get('analysis_results') and st.session_state.get('analyze_clicked', False) and st.session_state.get('patient_info'):
            results = st.session_state.get('analysis_results')
            patient_info = st.session_state.get('patient_info')
            report_data = st.session_state.get('report_data')
            st.markdown('<h2 class="sub-header">📥 Export Report</h2>', unsafe_allow_html=True)
            export_data = {
                "patient_info": patient_info,
                "blood_report": report_data,
                "analysis_results": {
                    "summary": results.get("summary", ""),
                    "normal_parameters": [{k:v for k,v in p.items() if k != 'category'} for p in results.get("normal_parameters", [])],
                    "abnormal_parameters": [{k:v for k,v in p.items() if k != 'category'} for p in results.get("abnormal_parameters", [])],
                    "critical_parameters": [{k:v for k,v in p.items() if k != 'category'} for p in results.get("critical_parameters", [])],
                    "conditions_detected": results.get("conditions_detected", []),
                    "recommendations": results.get("recommendations", [])
                },
                "generated_date": str(datetime.now())
            }
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Patient Details:**")
                st.json(export_data["patient_info"])
            with col2:
                st.markdown("**Analysis Summary:**")
                st.markdown(results.get("summary", "No summary available"))
            st.markdown("### ⬇️ Download Options")
            col1, col2 = st.columns(2)
            with col1:
                json_str = json.dumps(export_data, indent=2)
                st.download_button(label="📥 Download as JSON", data=json_str,
                                   file_name=f"blood_report_{patient_info['name']}_{patient_info['report_date']}.json",
                                   mime="application/json", use_container_width=True)
            with col2:
                csv_data = []
                for category, params in report_data.items():
                    for param, value in params.items():
                        status = "Normal"
                        for p in results.get("normal_parameters", []):
                            if p.get("parameter") == param:
                                status = "Normal"
                                break
                        for p in results.get("abnormal_parameters", []):
                            if p.get("parameter") == param:
                                status = p.get("status", "").upper()
                                break
                        for p in results.get("critical_parameters", []):
                            if p.get("parameter") == param:
                                status = "CRITICAL"
                                break
                        csv_data.append({"Category": category, "Parameter": param, "Value": value, "Status": status})
                df = pd.DataFrame(csv_data)
                csv = df.to_csv(index=False)
                st.download_button(label="📥 Download as CSV", data=csv,
                                   file_name=f"blood_params_{patient_info['name']}_{patient_info['report_date']}.csv",
                                   mime="text/csv", use_container_width=True)
            st.markdown("### 🖨️ Print Report")
            html_report = generate_html_report(patient_info, report_data, results)
            st.download_button(label="📥 Download HTML Report (Printable)", data=html_report,
                               file_name=f"blood_report_{patient_info['name']}_{patient_info['report_date']}.html",
                               mime="text/html", use_container_width=True)
            st.info("""
            **How to print:**
            1. Download the HTML report
            2. Open the downloaded file in your browser
            3. Use browser's print function (Ctrl+P or Cmd+P)
            4. Select your printer or "Save as PDF"
            """)
            st.markdown("### 📤 Share Report")
            report_summary = f"""
Blood Report Analysis for {patient_info['name']}
Date: {patient_info['report_date']}
Summary: {len(results.get('normal_parameters', []))} normal, {len(results.get('abnormal_parameters', []))} abnormal, {len(results.get('critical_parameters', []))} critical parameters
Conditions detected: {len(results.get('conditions_detected', []))}
            """
            st.text_area("Report Summary (Copy to share)", report_summary, height=100)
        else:
            st.info("👈 Please analyze a report first to export results")

if __name__ == "__main__":
    main()