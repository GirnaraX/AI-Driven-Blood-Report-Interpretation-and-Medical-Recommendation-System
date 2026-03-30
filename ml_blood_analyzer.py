import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.multioutput import MultiOutputClassifier
from sklearn.pipeline import Pipeline
import warnings
warnings.filterwarnings('ignore')
from blood_analyzer import BloodReportAnalyzer, REFERENCE_RANGES


class MLBloodAnalyzer(BloodReportAnalyzer):
    """
    Machine Learning enhanced blood report analyzer.
    Uses both rule-based checks and ML predictions for more robust analysis.
    """
    
    def __init__(self):
        super().__init__()
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.condition_labels = [
            'Anemia', 'Diabetes Risk', 'High Cholesterol', 
            'Thyroid Dysfunction', 'Liver Stress', 'Kidney Stress'
        ]
    
    def generate_synthetic_data(self, n_samples=1000):
        """
        Generate synthetic blood test data with known condition labels.
        This is for demonstration only. In practice, use real de-identified data.
        """
        np.random.seed(42)
        data = []
        labels = []
        
        # Define normal ranges (approximate from REFERENCE_RANGES)
        ranges = {
            'Hemoglobin': (12.0, 16.0),      
            'RBC Count': (4.1, 5.1),
            'WBC Count': (4.0, 11.0),
            'Platelets': (150, 450),
            'Hematocrit': (36, 48),
            'MCV': (80, 100),
            'MCH': (27, 33),
            'MCHC': (32, 36),
            'Total Cholesterol': (125, 200),
            'HDL': (40, 60),
            'LDL': (0, 100),
            'Triglycerides': (0, 150),
            'ALT': (7, 56),
            'AST': (10, 40),
            'ALP': (44, 147),
            'Total Bilirubin': (0.1, 1.2),
            'Creatinine': (0.6, 1.1),
            'BUN': (7, 20),
            'Uric Acid': (2.4, 6.0),
            'TSH': (0.4, 4.0),
            'Fasting Glucose': (70, 99),
            'HbA1c': (4.0, 5.6),
            'Sodium': (135, 145),
            'Potassium': (3.5, 5.0)
        }
        
        feature_names = list(ranges.keys())
        
        for _ in range(n_samples):
            # Generate random values within normal ranges
            row = {}
            for param, (low, high) in ranges.items():
                row[param] = np.random.uniform(low, high)
            
            # Introduce abnormalities with certain probabilities
            # Anemia: low hemoglobin, RBC, or hematocrit
            anemia = False
            if np.random.random() < 0.2:
                row['Hemoglobin'] = np.random.uniform(8.0, 11.9)
                anemia = True
            
            # Diabetes Risk: high fasting glucose or HbA1c
            diabetes = False
            if np.random.random() < 0.15:
                if np.random.random() < 0.5:
                    row['Fasting Glucose'] = np.random.uniform(100, 140)
                else:
                    row['HbA1c'] = np.random.uniform(5.7, 8.0)
                diabetes = True
            
            # High Cholesterol: high total cholesterol or LDL
            high_chol = False
            if np.random.random() < 0.25:
                row['Total Cholesterol'] = np.random.uniform(200, 280)
                high_chol = True
            
            # Thyroid Dysfunction: abnormal TSH
            thyroid = False
            if np.random.random() < 0.1:
                if np.random.random() < 0.5:
                    row['TSH'] = np.random.uniform(0.1, 0.39)  # hyper
                else:
                    row['TSH'] = np.random.uniform(4.1, 12.0)  # hypo
                thyroid = True
            
            # Liver Stress: elevated ALT, AST, or ALP
            liver = False
            if np.random.random() < 0.15:
                row['ALT'] = np.random.uniform(60, 150)
                liver = True
            
            # Kidney Stress: elevated creatinine or BUN
            kidney = False
            if np.random.random() < 0.1:
                row['Creatinine'] = np.random.uniform(1.2, 2.5)
                kidney = True
            
            # Build label vector
            label_vec = [anemia, diabetes, high_chol, thyroid, liver, kidney]
            data.append(row)
            labels.append(label_vec)
        
        df = pd.DataFrame(data)
        return df, np.array(labels), feature_names
    
    def train_model(self, X, y):
        """
        Train a multi-output Random Forest classifier.
        X: DataFrame or numpy array of features
        y: numpy array of shape (n_samples, n_labels) binary labels
        """
        # Store feature columns for later use
        self.feature_columns = X.columns.tolist() if isinstance(X, pd.DataFrame) else list(range(X.shape[1]))
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Create pipeline with scaling and classifier
        self.model = Pipeline([
            ('scaler', StandardScaler()),
            ('clf', MultiOutputClassifier(RandomForestClassifier(n_estimators=100, random_state=42)))
        ])
        
        # Train
        self.model.fit(X_train, y_train)
        
        # Evaluate
        accuracy = self.model.score(X_test, y_test)
        print(f"Model training complete. Test accuracy: {accuracy:.3f}")
        
        return self.model
    
    def predict_conditions(self, report_data, gender='female', age=30):
        """
        Predict conditions from blood report using ML model.
        report_data: dict with categories and parameters (same as input to analyze_blood_report)
        gender, age: for feature selection (currently not used in features but kept for consistency)
        Returns list of predicted conditions.
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train_model() first with synthetic or real data.")
        
        # Extract feature vector from report_data
        features = {}
        # Map parameter names to features used in training
        param_mapping = {
            'Hemoglobin': 'Hemoglobin',
            'RBC Count': 'RBC Count',
            'WBC Count': 'WBC Count',
            'Platelets': 'Platelets',
            'Hematocrit': 'Hematocrit',
            'MCV': 'MCV',
            'MCH': 'MCH',
            'MCHC': 'MCHC',
            'Total Cholesterol': 'Total Cholesterol',
            'HDL Cholesterol': 'HDL',
            'LDL Cholesterol': 'LDL',
            'Triglycerides': 'Triglycerides',
            'ALT (SGPT)': 'ALT',
            'AST (SGOT)': 'AST',
            'ALP': 'ALP',
            'Total Bilirubin': 'Total Bilirubin',
            'Creatinine': 'Creatinine',
            'BUN': 'BUN',
            'Uric Acid': 'Uric Acid',
            'TSH': 'TSH',
            'Fasting Glucose': 'Fasting Glucose',
            'HbA1c': 'HbA1c',
            'Sodium': 'Sodium',
            'Potassium': 'Potassium'
        }
        
        # Collect values from report_data
        for category, params in report_data.items():
            for param, value in params.items():
                if param in param_mapping:
                    features[param_mapping[param]] = value
        
        # Ensure all required features are present; fill missing with median from training (simplified)
        # For demo, we'll fill with 0 if missing, but better would be to use a default normal value
        feature_vector = []
        for col in self.feature_columns:
            if col in features:
                feature_vector.append(features[col])
            else:
                # Use a reasonable default (e.g., mean of normal range)
                # This is simplified; in production use imputation
                feature_vector.append(0.0)
        
        # Reshape and predict
        X = np.array(feature_vector).reshape(1, -1)
        pred_proba = self.model.predict_proba(X)
        # For multi-output, predict_proba returns list of arrays, one per output
        # We'll take the probability of class 1 (condition present)
        predicted_conditions = []
        for i, proba in enumerate(pred_proba):
            if proba[0][1] > 0.5:  # threshold 0.5
                predicted_conditions.append(self.condition_labels[i])
        
        return predicted_conditions
    
    def analyze_with_ml(self, report_data, gender, age):
        """
        Perform combined analysis: rule-based + ML predictions.
        Returns dict with both results.
        """
        # Rule-based analysis from parent
        rule_results = super().analyze_blood_report(report_data, gender, age)
        
        # ML predictions
        try:
            ml_conditions = self.predict_conditions(report_data, gender, age)
            rule_results['ml_predicted_conditions'] = ml_conditions
        except ValueError:
            rule_results['ml_predicted_conditions'] = ["Model not trained"]
        
        # Add a combined recommendation if ML adds new conditions not caught by rules
        rule_conditions = [c['condition'] for c in rule_results['conditions_detected']]
        combined_conditions = list(set(rule_conditions + ml_conditions))
        rule_results['combined_conditions'] = combined_conditions
        
        return rule_results


# Example usage:
if __name__ == "__main__":
    # Initialize ML analyzer
    ml_analyzer = MLBloodAnalyzer()
    
    # Generate synthetic training data
    X, y, feature_names = ml_analyzer.generate_synthetic_data(n_samples=2000)
    ml_analyzer.train_model(X, y)
    
    # Example blood report (simulated)
    sample_report = {
        "Complete Blood Count (CBC)": {
            "Hemoglobin": 10.5,      # low -> anemia
            "RBC Count": 3.8,
            "WBC Count": 7.2,
            "Platelets": 250,
            "Hematocrit": 32,
            "MCV": 85,
            "MCH": 28,
            "MCHC": 33
        },
        "Lipid Profile": {
            "Total Cholesterol": 210,
            "HDL Cholesterol": 45,
            "LDL Cholesterol": 130,
            "Triglycerides": 160
        },
        "Liver Function": {
            "ALT (SGPT)": 45,
            "AST (SGOT)": 38,
            "ALP": 80
        },
        "Diabetes Profile": {
            "Fasting Glucose": 105,
            "HbA1c": 5.8
        }
    }
    
    # Run analysis with ML
    result = ml_analyzer.analyze_with_ml(sample_report, gender="female", age=35)
    
    print("Rule-based conditions:", [c['condition'] for c in result['conditions_detected']])
    print("ML predicted conditions:", result['ml_predicted_conditions'])
    print("Combined conditions:", result['combined_conditions'])
    print("\nSummary:")
    print(result['summary'])
    print("\nRecommendations:")
    for rec in result['recommendations']:
        print(f"- {rec['condition']}: {rec['recommendations'][0]}")