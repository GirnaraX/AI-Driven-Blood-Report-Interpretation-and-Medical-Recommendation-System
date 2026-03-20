-- Create database
CREATE DATABASE IF NOT EXISTS blood_report_analyzer;
USE blood_report_analyzer;

-- 1. Patients table
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    gender VARCHAR(10) NOT NULL,
    blood_group VARCHAR(5),
    report_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_patient_name (patient_name),
    INDEX idx_report_date (report_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Blood reports table (stores individual parameters)
CREATE TABLE IF NOT EXISTS blood_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    category VARCHAR(50) NOT NULL,
    parameter VARCHAR(100) NOT NULL,
    value FLOAT,
    unit VARCHAR(20),
    status VARCHAR(20), -- 'normal', 'abnormal', 'critical'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    INDEX idx_patient_id (patient_id),
    INDEX idx_category (category),
    INDEX_idx_parameter (parameter),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Analysis results table (stores summary and recommendations)
CREATE TABLE IF NOT EXISTS analysis_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    summary TEXT,
    normal_count INT DEFAULT 0,
    abnormal_count INT DEFAULT 0,
    critical_count INT DEFAULT 0,
    conditions_detected JSON,
    recommendations JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    INDEX idx_patient_id (patient_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Optional: Create views for easier querying

-- View for complete patient history with analysis
CREATE VIEW patient_history_view AS
SELECT 
    p.id AS patient_id,
    p.patient_name,
    p.age,
    p.gender,
    p.blood_group,
    p.report_date,
    p.created_at AS patient_created_at,
    a.normal_count,
    a.abnormal_count,
    a.critical_count,
    a.summary,
    a.conditions_detected,
    a.created_at AS analysis_date
FROM patients p
LEFT JOIN analysis_results a ON p.id = a.patient_id
ORDER BY a.created_at DESC;

-- View for blood parameters summary
CREATE VIEW blood_parameters_view AS
SELECT 
    p.id AS patient_id,
    p.patient_name,
    br.category,
    br.parameter,
    br.value,
    br.unit,
    br.status,
    br.created_at AS test_date
FROM patients p
JOIN blood_reports br ON p.id = br.patient_id
ORDER BY br.created_at DESC;

-- Sample queries for reference

-- 1. Get all patients with abnormal results
SELECT DISTINCT 
    p.patient_name,
    p.age,
    p.gender,
    COUNT(br.id) as abnormal_count
FROM patients p
JOIN blood_reports br ON p.id = br.patient_id
WHERE br.status IN ('abnormal', 'critical')
GROUP BY p.id
ORDER BY abnormal_count DESC;

-- 2. Get latest analysis for a specific patient
SELECT 
    p.patient_name,
    a.summary,
    a.normal_count,
    a.abnormal_count,
    a.critical_count,
    a.conditions_detected,
    a.created_at
FROM patients p
JOIN analysis_results a ON p.id = a.patient_id
WHERE p.patient_name LIKE '%John%'
ORDER BY a.created_at DESC
LIMIT 1;

-- 3. Get all critical parameters for patients
SELECT 
    p.patient_name,
    br.category,
    br.parameter,
    br.value,
    br.unit,
    br.status
FROM patients p
JOIN blood_reports br ON p.id = br.patient_id
WHERE br.status = 'critical'
ORDER BY br.created_at DESC;

-- 4. Statistical analysis of patient data
SELECT 
    gender,
    AVG(age) as avg_age,
    COUNT(*) as patient_count,
    SUM(CASE WHEN EXISTS (
        SELECT 1 FROM blood_reports br 
        WHERE br.patient_id = p.id AND br.status = 'critical'
    ) THEN 1 ELSE 0 END) as patients_with_critical_results
FROM patients p
GROUP BY gender;

-- 5. Get patients with specific condition (e.g., Diabetes)
SELECT 
    p.patient_name,
    p.age,
    p.gender,
    a.conditions_detected,
    a.created_at
FROM patients p
JOIN analysis_results a ON p.id = a.patient_id
WHERE JSON_SEARCH(a.conditions_detected, 'all', '%Diabetes%') IS NOT NULL;

-- Create user and grant privileges (optional - if you want a dedicated user)
CREATE USER IF NOT EXISTS 'blood_analyzer_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON blood_report_analyzer.* TO 'blood_analyzer_user'@'localhost';
FLUSH PRIVILEGES;