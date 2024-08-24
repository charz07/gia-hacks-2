import json
import hashlib
import os
import secrets
from typing import Dict, Optional, List
import boto3
from botocore.exceptions import ClientError

class PatientAccount:
    _instance = None
    _is_logged_in = False
    _current_user = None
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
    def register_user(cls, identifier: str, password: str, name: str, date_of_birth: str, address: str) -> bool:
        cls._ensure_initialized()
        try:
            if cls._load_user_data(identifier):
                print(f"User with identifier {identifier} already exists.")
                return False

            salt = secrets.token_hex(16)
            password_hash = cls._hash_password(password, salt)

            new_user = {
                "identifier": identifier,
                "password_hash": password_hash,
                "name": name,
                "date_of_birth": date_of_birth,
                "address": address,
                "ehr": {},
                "consultation_history": [],
                "scheduled_appointments": []
            }

            json_data = json.dumps(new_user, indent=2)
            cls.s3.put_object(Bucket=cls.bucket_name, Key=f"{identifier}.json", Body=json_data)

            print(f"User {identifier} registered successfully.")
            return True

        except Exception as e:
            print(f"Registration failed: {str(e)}")
            return False

    @classmethod
    def login(cls, identifier: str, password: str) -> bool:
        cls._ensure_initialized()
        if cls._is_logged_in:
            print("Another user is already logged in.")
            return False

        try:
            user_data = cls._load_user_data(identifier)
            if user_data and cls._verify_password(password, user_data['password_hash']):
                cls._current_user = user_data
                cls._is_logged_in = True
                print(f"User {identifier} logged in successfully.")
                return True
            else:
                print("Invalid credentials.")
                return False
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False

    @classmethod
    def update_ehr(cls, ehr_data: Dict) -> None:
        cls._ensure_initialized()
        cls._check_login()
        cls._current_user['ehr'].update(ehr_data)

    @classmethod
    def add_consultation(cls, consultation: Dict) -> None:
        cls._ensure_initialized()
        cls._check_login()
        cls._current_user['consultation_history'].append(consultation)

    @classmethod
    def schedule_appointment(cls, appointment: Dict) -> None:
        cls._ensure_initialized()
        cls._check_login()
        cls._current_user['scheduled_appointments'].append(appointment)

    @classmethod
    def save(cls) -> None:
        cls._ensure_initialized()
        cls._check_login()
        try:
            json_data = json.dumps(cls._current_user, indent=2)
            cls.s3.put_object(Bucket=cls.bucket_name, Key=f"{cls._current_user['identifier']}.json", Body=json_data)
            print("Data saved successfully.")
        except Exception as e:
            print(f"Failed to save data: {str(e)}")

    @classmethod
    def logout(cls) -> None:
        cls._ensure_initialized()
        cls._is_logged_in = False
        cls._current_user = None
        print("User logged out successfully.")

    @classmethod
    def _load_user_data(cls, identifier: str) -> Optional[Dict]:
        cls._ensure_initialized()
        try:
            response = cls.s3.get_object(Bucket=cls.bucket_name, Key=f"{identifier}.json")
            return json.loads(response['Body'].read().decode('utf-8'))
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return None
            else:
                raise

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
            raise ValueError("User is not logged in.")

    @classmethod
    def ehr(cls) -> Dict:
        cls._ensure_initialized()
        cls._check_login()
        return cls._current_user['ehr']

    @classmethod
    def consultation_history(cls) -> List[Dict]:
        cls._ensure_initialized()
        cls._check_login()
        return cls._current_user['consultation_history']

    @classmethod
    def scheduled_appointments(cls) -> List[Dict]:
        cls._ensure_initialized()
        cls._check_login()
        return cls._current_user['scheduled_appointments']

# Example usage
if __name__ == "__main__":
    # Register a new user
    PatientAccount.register_user(
        "newemail@example.com",
        "password",
        "Jane Doe",
        "1985-05-15",
        "456 Elm St, Othertown, USA"
    )

    # Login
    PatientAccount.login("newemail@example.com", "password")

    # Update EHR
    PatientAccount.update_ehr({"allergies": "None"})

    # Add consultation
    PatientAccount.add_consultation({"date": "2023-02-15", "doctor": "Dr. Smith"})

    # Schedule appointment
    PatientAccount.schedule_appointment({"date": "2023-03-01", "time": "10:00 AM"})

    # Save changes
    PatientAccount.save()

    # Access data
    print(PatientAccount.ehr())

    # Logout
    PatientAccount.logout()
