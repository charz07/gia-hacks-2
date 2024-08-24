import json
import hashlib
import os
import secrets
from typing import Dict, List, Optional
import boto3
from botocore.exceptions import ClientError

class DoctorAccount:
    _instance = None
    _is_logged_in = False
    _current_doctor = None
    s3 = None
    bucket_name = None

    @classmethod
    def _ensure_initialized(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._init_s3()

    @classmethod
    def _init_s3(cls):
        cls.s3 = boto3.client('s3')
        cls.bucket_name = os.environ.get('S3_BUCKET_NAME')
        if not cls.bucket_name:
            cls.bucket_name = "gia-hacks-2"

    @classmethod
    def register_doctor(cls, email: str, password: str, name: str, specialization: str) -> bool:
        cls._ensure_initialized()
        try:
            if cls._load_doctor_data(email):
                print(f"Doctor with email {email} already exists.")
                return False

            salt = secrets.token_hex(16)
            password_hash = cls._hash_password(password, salt)

            new_doctor = {
                "email": email,
                "password_hash": password_hash,
                "name": name,
                "specialization": specialization,
                "patients": []
            }

            json_data = json.dumps(new_doctor, indent=2)
            cls.s3.put_object(Bucket=cls.bucket_name, Key=f"doctor_{email}.json", Body=json_data)

            print(f"Doctor {email} registered successfully.")
            return True

        except Exception as e:
            print(f"Registration failed: {str(e)}")
            return False

    @classmethod
    def login(cls, email: str, password: str) -> bool:
        cls._ensure_initialized()
        if cls._is_logged_in:
            print("Another doctor is already logged in.")
            return False

        try:
            doctor_data = cls._load_doctor_data(email)
            if doctor_data and cls._verify_password(password, doctor_data['password_hash']):
                cls._current_doctor = doctor_data
                cls._is_logged_in = True
                print(f"Doctor {email} logged in successfully.")
                return True
            else:
                print("Invalid credentials.")
                return False
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False

    @classmethod
    def edit_patient_data(cls, patient_email: str, ehr_data: Dict) -> bool:
        cls._ensure_initialized()
        cls._check_login()
        if patient_email not in cls._current_doctor['patients']:
            print(f"Patient {patient_email} is not in the doctor's patient list.")
            return False
        
        try:
            patient_data = cls._load_patient_data(patient_email)
            patient_data['ehr'].update(ehr_data)
            cls._save_patient_data(patient_email, patient_data)
            print(f"Patient {patient_email}'s EHR updated successfully.")
            return True
        except Exception as e:
            print(f"Failed to update patient data: {str(e)}")
            return False

    @classmethod
    def add_consultation(cls, patient_email: str, consultation: Dict) -> bool:
        cls._ensure_initialized()
        cls._check_login()
        if patient_email not in cls._current_doctor['patients']:
            print(f"Patient {patient_email} is not in the doctor's patient list.")
            return False
        
        try:
            patient_data = cls._load_patient_data(patient_email)
            patient_data['consultation_history'].append(consultation)
            cls._save_patient_data(patient_email, patient_data)
            print(f"Consultation added to patient {patient_email}'s history.")
            return True
        except Exception as e:
            print(f"Failed to add consultation: {str(e)}")
            return False

    @classmethod
    def list_patients(cls) -> List[str]:
        cls._ensure_initialized()
        cls._check_login()
        return cls._current_doctor['patients']

    @classmethod
    def get_patient_data(cls, patient_email: str) -> Optional[Dict]:
        cls._ensure_initialized()
        cls._check_login()
        if patient_email not in cls._current_doctor['patients']:
            print(f"Patient {patient_email} is not in the doctor's patient list.")
            return None
        
        try:
            return cls._load_patient_data(patient_email)
        except Exception as e:
            print(f"Failed to retrieve patient data: {str(e)}")
            return None

    @classmethod
    def save(cls) -> None:
        cls._ensure_initialized()
        cls._check_login()
        try:
            json_data = json.dumps(cls._current_doctor, indent=2)
            cls.s3.put_object(Bucket=cls.bucket_name, Key=f"doctor_{cls._current_doctor['email']}.json", Body=json_data)
            print("Doctor data saved successfully.")
        except Exception as e:
            print(f"Failed to save doctor data: {str(e)}")

    @classmethod
    def logout(cls) -> None:
        cls._ensure_initialized()
        cls._is_logged_in = False
        cls._current_doctor = None
        print("Doctor logged out successfully.")

    @classmethod
    def _load_doctor_data(cls, email: str) -> Optional[Dict]:
        cls._ensure_initialized()
        try:
            response = cls.s3.get_object(Bucket=cls.bucket_name, Key=f"doctor_{email}.json")
            return json.loads(response['Body'].read().decode('utf-8'))
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return None
            else:
                raise

    @classmethod
    def view_appointments(cls) -> List[Dict]:
        cls._ensure_initialized()
        cls._check_login()
        appointments = []
        for patient_email in cls._current_doctor['patients']:
            patient_data = cls._load_patient_data(patient_email)
            for appointment in patient_data['scheduled_appointments']:
                appointment['patient_email'] = patient_email
                appointment['patient_name'] = patient_data['name']
                appointments.append(appointment)
        return sorted(appointments, key=lambda x: (x['date'], x['time']))

    @classmethod
    def _load_patient_data(cls, email: str) -> Dict:
        cls._ensure_initialized()
        response = cls.s3.get_object(Bucket=cls.bucket_name, Key=f"{email}.json")
        return json.loads(response['Body'].read().decode('utf-8'))

    @classmethod
    def _save_patient_data(cls, email: str, data: Dict) -> None:
        cls._ensure_initialized()
        json_data = json.dumps(data, indent=2)
        cls.s3.put_object(Bucket=cls.bucket_name, Key=f"{email}.json", Body=json_data)

    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return salt + key.hex()

    @classmethod
    def _verify_password(cls, password: str, stored_hash: str) -> bool:
        salt = stored_hash[:32]
        return cls._hash_password(password, salt) == stored_hash

    @classmethod
    def _check_login(cls) -> None:
        if not cls._is_logged_in:
            raise ValueError("Doctor is not logged in.")
