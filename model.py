# models.py
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import json
from typing import List, Dict, Optional, Any
import pandas as pd

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'blood_report_analyzer',
    'user': 'root',  # Change this to your MySQL username
    'password': ''  # Change this to your MySQL password
}

class DatabaseConnection:
    """Database connection manager"""
    
    @staticmethod
    def get_connection():
        """Create and return a database connection"""
        try:
            connection = mysql.connector.connect(
                host=DB_CONFIG['host'],
                database=DB_CONFIG['database'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password']
            )
            return connection
        except Error as e:
            print(f"Error connecting to MySQL database: {e}")
            return None
    
    @staticmethod
    def test_connection():
        """Test database connection"""
        try:
            connection = DatabaseConnection.get_connection()
            if connection:
                connection.close()
                return True
            return False
        except:
            return False

class Patient:
    """Patient model"""
    
    def __init__(self, id=None, patient_name=None, age=None, gender=None, 
                 blood_group=None, report_date=None, created_at=None):
        self.id = id
        self.patient_name = patient_name
        self.age = age
        self.gender = gender
        self.blood_group = blood_group
        self.report_date = report_date
        self.created_at = created_at
    
    @classmethod
    def from_dict(cls, data):
        """Create Patient object from dictionary"""
        return cls(
            id=data.get('id'),
            patient_name=data.get('patient_name'),
            age=data.get('age'),
            gender=data.get('gender'),
            blood_group=data.get('blood_group'),
            report_date=data.get('report_date'),
            created_at=data.get('created_at')
        )
    
    def to_dict(self):
        """Convert Patient object to dictionary"""
        return {
            'id': self.id,
            'patient_name': self.patient_name,
            'age': self.age,
            'gender': self.gender,
            'blood_group': self.blood_group,
            'report_date': self.report_date,
            'created_at': self.created_at
        }
    
    def save(self):
        """Save patient to database"""
        connection = DatabaseConnection.get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor()
            
            if self.id:  # Update existing patient
                query = """
                    UPDATE patients 
                    SET patient_name = %s, age = %s, gender = %s, 
                        blood_group = %s, report_date = %s
                    WHERE id = %s
                """
                values = (self.patient_name, self.age, self.gender, 
                         self.blood_group, self.report_date, self.id)
                cursor.execute(query, values)
            else:  # Insert new patient
                query = """
                    INSERT INTO patients (patient_name, age, gender, blood_group, report_date)
                    VALUES (%s, %s, %s, %s, %s)
                """
                values = (self.patient_name, self.age, self.gender, 
                         self.blood_group, self.report_date)
                cursor.execute(query, values)
                self.id = cursor.lastrowid
            
            connection.commit()
            cursor.close()
            connection.close()
            return self.id
        except Error as e:
            print(f"Error saving patient: {e}")
            return None
    
    @classmethod
    def get_by_id(cls, patient_id):
        """Get patient by ID"""
        connection = DatabaseConnection.get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM patients WHERE id = %s"
            cursor.execute(query, (patient_id,))
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if result:
                return cls.from_dict(result)
            return None
        except Error as e:
            print(f"Error getting patient: {e}")
            return None
    
    @classmethod
    def search(cls, name=None, limit=100):
        """Search patients by name"""
        connection = DatabaseConnection.get_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            if name:
                query = "SELECT * FROM patients WHERE patient_name LIKE %s ORDER BY created_at DESC LIMIT %s"
                cursor.execute(query, (f'%{name}%', limit))
            else:
                query = "SELECT * FROM patients ORDER BY created_at DESC LIMIT %s"
                cursor.execute(query, (limit,))
            
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            
            return [cls.from_dict(row) for row in results]
        except Error as e:
            print(f"Error searching patients: {e}")
            return []
    
    def delete(self):
        """Delete patient from database"""
        if not self.id:
            return False
        
        connection = DatabaseConnection.get_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            query = "DELETE FROM patients WHERE id = %s"
            cursor.execute(query, (self.id,))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Error as e:
            print(f"Error deleting patient: {e}")
            return False


class BloodReport:
    """Blood report model for individual parameters"""
    
    def __init__(self, id=None, patient_id=None, category=None, parameter=None,
                 value=None, unit=None, status=None, created_at=None):
        self.id = id
        self.patient_id = patient_id
        self.category = category
        self.parameter = parameter
        self.value = value
        self.unit = unit
        self.status = status
        self.created_at = created_at
    
    @classmethod
    def from_dict(cls, data):
        """Create BloodReport object from dictionary"""
        return cls(
            id=data.get('id'),
            patient_id=data.get('patient_id'),
            category=data.get('category'),
            parameter=data.get('parameter'),
            value=data.get('value'),
            unit=data.get('unit'),
            status=data.get('status'),
            created_at=data.get('created_at')
        )
    
    def to_dict(self):
        """Convert BloodReport object to dictionary"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'category': self.category,
            'parameter': self.parameter,
            'value': self.value,
            'unit': self.unit,
            'status': self.status,
            'created_at': self.created_at
        }
    
    def save(self):
        """Save blood report parameter to database"""
        connection = DatabaseConnection.get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor()
            
            query = """
                INSERT INTO blood_reports (patient_id, category, parameter, value, unit, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (self.patient_id, self.category, self.parameter, 
                     self.value, self.unit, self.status)
            cursor.execute(query, values)
            self.id = cursor.lastrowid
            
            connection.commit()
            cursor.close()
            connection.close()
            return self.id
        except Error as e:
            print(f"Error saving blood report: {e}")
            return None
    
    @classmethod
    def get_by_patient(cls, patient_id):
        """Get all blood reports for a patient"""
        connection = DatabaseConnection.get_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM blood_reports WHERE patient_id = %s ORDER BY category, parameter"
            cursor.execute(query, (patient_id,))
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            
            return [cls.from_dict(row) for row in results]
        except Error as e:
            print(f"Error getting blood reports: {e}")
            return []
    
    @classmethod
    def get_critical_by_patient(cls, patient_id):
        """Get critical blood reports for a patient"""
        connection = DatabaseConnection.get_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM blood_reports WHERE patient_id = %s AND status = 'critical'"
            cursor.execute(query, (patient_id,))
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            
            return [cls.from_dict(row) for row in results]
        except Error as e:
            print(f"Error getting critical reports: {e}")
            return []
    
    @classmethod
    def get_by_category(cls, patient_id, category):
        """Get blood reports by category for a patient"""
        connection = DatabaseConnection.get_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM blood_reports WHERE patient_id = %s AND category = %s"
            cursor.execute(query, (patient_id, category))
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            
            return [cls.from_dict(row) for row in results]
        except Error as e:
            print(f"Error getting reports by category: {e}")
            return []


class AnalysisResult:
    """Analysis results model"""
    
    def __init__(self, id=None, patient_id=None, summary=None, normal_count=0,
                 abnormal_count=0, critical_count=0, conditions_detected=None,
                 recommendations=None, created_at=None):
        self.id = id
        self.patient_id = patient_id
        self.summary = summary
        self.normal_count = normal_count
        self.abnormal_count = abnormal_count
        self.critical_count = critical_count
        self.conditions_detected = conditions_detected or []
        self.recommendations = recommendations or []
        self.created_at = created_at
    
    @classmethod
    def from_dict(cls, data):
        """Create AnalysisResult object from dictionary"""
        conditions = data.get('conditions_detected')
        if isinstance(conditions, str):
            conditions = json.loads(conditions)
        
        recommendations = data.get('recommendations')
        if isinstance(recommendations, str):
            recommendations = json.loads(recommendations)
        
        return cls(
            id=data.get('id'),
            patient_id=data.get('patient_id'),
            summary=data.get('summary'),
            normal_count=data.get('normal_count', 0),
            abnormal_count=data.get('abnormal_count', 0),
            critical_count=data.get('critical_count', 0),
            conditions_detected=conditions,
            recommendations=recommendations,
            created_at=data.get('created_at')
        )
    
    def to_dict(self):
        """Convert AnalysisResult object to dictionary"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'summary': self.summary,
            'normal_count': self.normal_count,
            'abnormal_count': self.abnormal_count,
            'critical_count': self.critical_count,
            'conditions_detected': json.dumps(self.conditions_detected),
            'recommendations': json.dumps(self.recommendations),
            'created_at': self.created_at
        }
    
    def save(self):
        """Save analysis result to database"""
        connection = DatabaseConnection.get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor()
            
            query = """
                INSERT INTO analysis_results 
                (patient_id, summary, normal_count, abnormal_count, critical_count, 
                 conditions_detected, recommendations)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (self.patient_id, self.summary, self.normal_count, 
                     self.abnormal_count, self.critical_count,
                     json.dumps(self.conditions_detected), 
                     json.dumps(self.recommendations))
            cursor.execute(query, values)
            self.id = cursor.lastrowid
            
            connection.commit()
            cursor.close()
            connection.close()
            return self.id
        except Error as e:
            print(f"Error saving analysis result: {e}")
            return None
    
    @classmethod
    def get_by_patient(cls, patient_id, limit=10):
        """Get analysis results for a patient"""
        connection = DatabaseConnection.get_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT * FROM analysis_results 
                WHERE patient_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            """
            cursor.execute(query, (patient_id, limit))
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            
            return [cls.from_dict(row) for row in results]
        except Error as e:
            print(f"Error getting analysis results: {e}")
            return []
    
    @classmethod
    def get_latest_by_patient(cls, patient_id):
        """Get latest analysis result for a patient"""
        connection = DatabaseConnection.get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT * FROM analysis_results 
                WHERE patient_id = %s 
                ORDER BY created_at DESC 
                LIMIT 1
            """
            cursor.execute(query, (patient_id,))
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if result:
                return cls.from_dict(result)
            return None
        except Error as e:
            print(f"Error getting latest analysis: {e}")
            return None


class PatientHistory:
    """View model for patient history"""
    
    @staticmethod
    def get_patient_history(patient_name=None, limit=100):
        """Get patient history with analysis results"""
        connection = DatabaseConnection.get_connection()
        if not connection:
            return pd.DataFrame()
        
        try:
            if patient_name:
                query = """
                    SELECT 
                        p.id,
                        p.patient_name,
                        p.age,
                        p.gender,
                        p.blood_group,
                        p.report_date,
                        a.normal_count,
                        a.abnormal_count,
                        a.critical_count,
                        a.summary,
                        a.conditions_detected,
                        a.created_at as analysis_date
                    FROM patients p
                    LEFT JOIN analysis_results a ON p.id = a.patient_id
                    WHERE p.patient_name LIKE %s
                    ORDER BY a.created_at DESC
                    LIMIT %s
                """
                df = pd.read_sql(query, connection, params=(f'%{patient_name}%', limit))
            else:
                query = """
                    SELECT 
                        p.id,
                        p.patient_name,
                        p.age,
                        p.gender,
                        p.blood_group,
                        p.report_date,
                        a.normal_count,
                        a.abnormal_count,
                        a.critical_count,
                        a.summary,
                        a.conditions_detected,
                        a.created_at as analysis_date
                    FROM patients p
                    LEFT JOIN analysis_results a ON p.id = a.patient_id
                    ORDER BY a.created_at DESC
                    LIMIT %s
                """
                df = pd.read_sql(query, connection, params=(limit,))
            
            connection.close()
            return df
        except Error as e:
            print(f"Error getting patient history: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_patients_with_conditions(condition_keyword=None):
        """Get patients with specific conditions"""
        connection = DatabaseConnection.get_connection()
        if not connection:
            return pd.DataFrame()
        
        try:
            if condition_keyword:
                query = """
                    SELECT 
                        p.id,
                        p.patient_name,
                        p.age,
                        p.gender,
                        a.conditions_detected,
                        a.created_at
                    FROM patients p
                    JOIN analysis_results a ON p.id = a.patient_id
                    WHERE a.conditions_detected LIKE %s
                    ORDER BY a.created_at DESC
                """
                df = pd.read_sql(query, connection, params=(f'%{condition_keyword}%',))
            else:
                query = """
                    SELECT 
                        p.id,
                        p.patient_name,
                        p.age,
                        p.gender,
                        a.conditions_detected,
                        a.created_at
                    FROM patients p
                    JOIN analysis_results a ON p.id = a.patient_id
                    WHERE a.conditions_detected != '[]'
                    ORDER BY a.created_at DESC
                    LIMIT 50
                """
                df = pd.read_sql(query, connection)
            
            connection.close()
            return df
        except Error as e:
            print(f"Error getting patients with conditions: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_statistics():
        """Get overall statistics"""
        connection = DatabaseConnection.get_connection()
        if not connection:
            return {}
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Total patients
            cursor.execute("SELECT COUNT(*) as total_patients FROM patients")
            total_patients = cursor.fetchone()['total_patients']
            
            # Total analyses
            cursor.execute("SELECT COUNT(*) as total_analyses FROM analysis_results")
            total_analyses = cursor.fetchone()['total_analyses']
            
            # Patients with critical results
            cursor.execute("""
                SELECT COUNT(DISTINCT patient_id) as critical_patients 
                FROM analysis_results 
                WHERE critical_count > 0
            """)
            critical_patients = cursor.fetchone()['critical_patients']
            
            # Average age
            cursor.execute("SELECT AVG(age) as avg_age FROM patients")
            avg_age = cursor.fetchone()['avg_age']
            
            # Gender distribution
            cursor.execute("""
                SELECT gender, COUNT(*) as count 
                FROM patients 
                GROUP BY gender
            """)
            gender_dist = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return {
                'total_patients': total_patients,
                'total_analyses': total_analyses,
                'critical_patients': critical_patients,
                'avg_age': round(avg_age, 1) if avg_age else 0,
                'gender_distribution': gender_dist
            }
        except Error as e:
            print(f"Error getting statistics: {e}")
            return {}


class BloodReportAnalyzer:
    """Main analyzer class that uses the models"""
    
    def __init__(self):
        self.patient = None
        self.blood_reports = []
        self.analysis_result = None
    
    def save_complete_analysis(self, patient_info, report_data, results):
        """Save complete analysis to database using models"""
        
        # Save patient
        patient = Patient(
            patient_name=patient_info.get('name'),
            age=patient_info.get('age'),
            gender=patient_info.get('gender'),
            blood_group=patient_info.get('blood_group'),
            report_date=patient_info.get('report_date')
        )
        patient_id = patient.save()
        
        if not patient_id:
            return False
        
        # Save blood reports
        for category, parameters in report_data.items():
            for param, value in parameters.items():
                # Find status from results
                status = 'normal'
                for p in results.get('normal_parameters', []):
                    if p.get('parameter') == param:
                        status = 'normal'
                        break
                for p in results.get('abnormal_parameters', []):
                    if p.get('parameter') == param:
                        status = 'abnormal'
                        break
                for p in results.get('critical_parameters', []):
                    if p.get('parameter') == param:
                        status = 'critical'
                        break
                
                # Find unit from reference ranges (you'll need to pass this)
                unit = ''
                for cat, ref_params in REFERENCE_RANGES.items():
                    if param in ref_params:
                        unit = ref_params[param].get('unit', '')
                        break
                
                blood_report = BloodReport(
                    patient_id=patient_id,
                    category=category,
                    parameter=param,
                    value=float(value) if value else None,
                    unit=unit,
                    status=status
                )
                blood_report.save()
        
        # Save analysis results
        analysis = AnalysisResult(
            patient_id=patient_id,
            summary=results.get('summary'),
            normal_count=len(results.get('normal_parameters', [])),
            abnormal_count=len(results.get('abnormal_parameters', [])),
            critical_count=len(results.get('critical_parameters', [])),
            conditions_detected=results.get('conditions_detected', []),
            recommendations=results.get('recommendations', [])
        )
        analysis.save()
        
        return True
    
    def get_patient_full_history(self, patient_id):
        """Get complete patient history with all details"""
        
        patient = Patient.get_by_id(patient_id)
        if not patient:
            return None
        
        blood_reports = BloodReport.get_by_patient(patient_id)
        analyses = AnalysisResult.get_by_patient(patient_id)
        
        return {
            'patient': patient.to_dict() if patient else None,
            'blood_reports': [br.to_dict() for br in blood_reports],
            'analyses': [a.to_dict() for a in analyses]
        }
    
    def get_patients_by_condition(self, condition):
        """Get patients with specific condition"""
        return PatientHistory.get_patients_with_conditions(condition)


# Reference ranges (keep as is from original)
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

# Recommendations (keep as is from original)
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