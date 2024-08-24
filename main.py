import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from patient import PatientAccount
from doctor import DoctorAccount

def main():
    st.set_page_config(page_title="Telehealth App", page_icon="🏥", layout="wide")

    # # Set light white-blue theme
    # st.markdown(
    #     """
    #     <style>
    #     .stApp {
    #         background-color: #f0f8ff;
    #     }
    #     </style>
    #     """,
    #     unsafe_allow_html=True
    # )

    if "user" not in st.session_state:
        st.session_state.user = None
        st.session_state.user_type = None

    if st.session_state.user is None:
        login_page()
    else:
        if st.session_state.user_type == "patient":
            patient_flow()
        else:
            doctor_flow()

def login_page():
    st.header("Login")
    user_type = st.radio("Select user type", ["Patient", "Doctor"])
    identifier = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Login"):
            if user_type == "Patient" and PatientAccount.login(identifier, password):
                st.session_state.user = PatientAccount._current_user
                st.session_state.user_type = "patient"
                st.success("Logged in successfully!")
                st.rerun()
            elif user_type == "Doctor" and DoctorAccount.login(identifier, password):
                st.session_state.user = DoctorAccount._current_doctor
                st.session_state.user_type = "doctor"
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid email or password")
    
    with col2:
        if st.button("Register"):
            st.session_state.register = True
            st.session_state.register_type = user_type
            st.rerun()

    if st.session_state.get('register', False):
        if st.session_state.register_type == "Patient":
            register_patient()
        else:
            register_doctor()

def register_patient():
    st.subheader("Register New Patient")
    identifier = st.text_input("Email or Phone Number")
    password = st.text_input("New Password", type="password")
    name = st.text_input("Full Name")
    dob = st.date_input("Date of Birth")
    address = st.text_area("Address")

    if st.button("Submit Registration"):
        if identifier and password and name and dob and address:
            if PatientAccount.register_user(identifier, password, name, str(dob), address):
                st.success("Registered successfully! Please log in.")
                st.session_state.register = False
            else:
                st.error("Registration failed. Email may already be in use.")
        else:
            st.error("Please fill in all fields")

def register_doctor():
    st.subheader("Register New Doctor")
    email = st.text_input("Email")
    password = st.text_input("New Password", type="password")
    name = st.text_input("Full Name")
    specialization = st.text_input("Specialization")

    if st.button("Submit Registration"):
        if email and password and name and specialization:
            if DoctorAccount.register_doctor(email, password, name, specialization):
                st.success("Registered successfully! Please log in.")
                st.session_state.register = False
            else:
                st.error("Registration failed. Email may already be in use.")
        else:
            st.error("Please fill in all fields")

def patient_flow():
    if not st.session_state.user.get('ehr'):
        patient_onboarding()
    else:
        patient_dashboard()

def patient_onboarding():
    st.header("Complete Your Profile")
    st.write("Please provide some additional health information.")
    
    allergies = st.text_area("Allergies (if any)")
    medical_conditions = st.text_area("Existing Medical Conditions")
    medications = st.text_area("Current Medications")
    previous_providers = st.text_area("Previous Health Providers")
    
    if st.button("Submit"):
        ehr_data = {
            "allergies": allergies,
            "medical_conditions": medical_conditions,
            "medications": medications,
            "previous_providers": previous_providers
        }
        PatientAccount.update_ehr(ehr_data)
        PatientAccount.save()
        st.success("Profile updated successfully!")
        st.rerun()

def patient_dashboard():
    st.header(f"Welcome, {st.session_state.user['name']}!")
    
    menu = ["View Past Consultations", "Book Consultation", "View Scheduled Appointments"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "View Past Consultations":
        view_past_consultations()
    elif choice == "Book Consultation":
        book_consultation()
    elif choice == "View Scheduled Appointments":
        view_scheduled_appointments()

    if st.sidebar.button("Logout"):
        PatientAccount.logout()
        st.session_state.user = None
        st.session_state.user_type = None
        st.rerun()

def view_past_consultations():
    st.subheader("Past Consultations")
    consultations = PatientAccount.consultation_history()
    
    if consultations:
        df = pd.DataFrame(consultations)
        st.table(df)
    else:
        st.info("No past consultations found")

def book_consultation():
    st.subheader("Book a Consultation")
    
    symptoms = st.text_area("Symptoms")
    reason = st.text_area("Reason for Consultation")
    date = st.date_input("Preferred Date", min_value=datetime.now().date())
    time = st.time_input("Preferred Time")
    
    if st.button("Book Consultation"):
        if symptoms and reason and date and time:
            consultation = {
                "date": str(date),
                "time": time.strftime("%H:%M"),
                "symptoms": symptoms,
                "reason": reason
            }
            PatientAccount.schedule_appointment(consultation)
            PatientAccount.save()
            st.success("Consultation booked successfully!")
        else:
            st.error("Please fill in all fields")

def view_scheduled_appointments():
    st.subheader("Scheduled Appointments")
    appointments = PatientAccount.scheduled_appointments()
    
    if appointments:
        df = pd.DataFrame(appointments)
        st.table(df)
    else:
        st.info("No scheduled appointments found")

def doctor_flow():
    if not st.session_state.user.get('onboarded'):
        doctor_onboarding()
    else:
        doctor_dashboard()

def doctor_onboarding():
    st.header("Complete Your Profile")
    st.write("Please provide some additional information.")
    
    years_of_experience = st.number_input("Years of Experience", min_value=0, max_value=100)
    certifications = st.text_area("Certifications")
    languages = st.text_input("Languages Spoken")
    
    if st.button("Submit"):
        onboarding_data = {
            "years_of_experience": years_of_experience,
            "certifications": certifications,
            "languages": languages,
            "onboarded": True
        }
        st.session_state.user.update(onboarding_data)
        DoctorAccount.save()
        st.success("Profile updated successfully!")
        st.rerun()

def doctor_dashboard():
    st.header(f"Welcome, Dr. {st.session_state.user['name']}!")
    
    menu = ["View Patients", "View Appointments", "Consultation"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "View Patients":
        view_patients()
    elif choice == "View Appointments":
        view_doctor_appointments()
    elif choice == "Consultation":
        consultation_page()

    if st.sidebar.button("Logout"):
        DoctorAccount.logout()
        st.session_state.user = None
        st.session_state.user_type = None
        st.rerun()

def view_patients():
    st.subheader("Your Patients")
    patients = DoctorAccount.list_patients()
    
    if patients:
        for patient_email in patients:
            if st.button(f"View {patient_email}"):
                patient_data = DoctorAccount.get_patient_data(patient_email)
                if patient_data:
                    st.json(patient_data)
                else:
                    st.error("Failed to retrieve patient data")
    else:
        st.info("No patients found")

def view_doctor_appointments():
    st.subheader("Upcoming Appointments")
    appointments = DoctorAccount.view_appointments()
    
    if appointments:
        df = pd.DataFrame(appointments)
        st.table(df)
    else:
        st.info("No upcoming appointments found")

def consultation_page():
    st.subheader("Consultation")
    
    patient_email = st.selectbox("Select Patient", DoctorAccount.list_patients())
    
    if patient_email:
        patient_data = DoctorAccount.get_patient_data(patient_email)
        if patient_data:
            display_patient_data(patient_data)
            
            notes = st.text_area("Consultation Notes")
            diagnosis = st.text_input("Diagnosis")
            prescription = st.text_area("Prescription")
            
            if st.button("Save Consultation"):
                consultation = {
                    "date": str(datetime.now().date()),
                    "time": datetime.now().strftime("%H:%M"),
                    "notes": notes,
                    "diagnosis": diagnosis,
                    "prescription": prescription
                }
                if DoctorAccount.add_consultation(patient_email, consultation):
                    st.success("Consultation saved successfully!")
                else:
                    st.error("Failed to save consultation")
            
            if st.button("Get AI Diagnostic Advice"):
                # Placeholder for AI diagnostic advice
                st.info("AI Predicted ICD9 Codes: ['305.1', '430', '493']. Tobacco use disorder, Subarachnoid hamorrhage, Asthma. Suggested treatment: inhaled corticosteroids")
        else:
            st.error("Failed to retrieve patient data")

def view_patients():
    st.subheader("Your Patients")
    patients = DoctorAccount.list_patients()
    
    if patients:
        selected_patient = st.selectbox("Select a patient to view details:", patients)
        if selected_patient:
            patient_data = DoctorAccount.get_patient_data(selected_patient)
            print(patient_data)
            if patient_data:
                display_patient_data(patient_data)
            else:
                st.error("Failed to retrieve patient data")
    else:
        st.info("No patients found")

def display_patient_data(patient_data):
    st.write("## Patient Information")
    
    # Personal Information
    st.write("### Personal Information")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Name:** {patient_data['name']}")
        st.write(f"**Email:** {patient_data['identifier']}")
    with col2:
        st.write(f"**Date of Birth:** {patient_data['date_of_birth']}")
        st.write(f"**Address:** {patient_data['address']}")

    st.write(f"**Assigned Doctor:** {patient_data['doctor_email']}")

    # EHR Data
    if 'ehr' in patient_data:
        st.write("### Electronic Health Record")
        for key, value in patient_data['ehr'].items():
            st.write(f"**{key.replace('_', ' ').title()}:** {value}")

    # Consultation History
    if 'consultation_history' in patient_data:
        st.write("### Consultation History")
        for idx, consultation in enumerate(patient_data['consultation_history'], 1):
            st.write(f"**Consultation {idx}**")
            st.write(f"Date: {consultation['date']}")
            if 'time' in consultation:
                st.write(f"Time: {consultation['time']}")
            st.write(f"Notes: {consultation['notes']}")
            if 'diagnosis' in consultation:
                st.write(f"Diagnosis: {consultation['diagnosis']}")
            if 'prescription' in consultation:
                st.write(f"Prescription: {consultation['prescription']}")
            st.write("---")

    # Scheduled Appointments
    if 'scheduled_appointments' in patient_data:
        st.write("### Scheduled Appointments")
        for appointment in patient_data['scheduled_appointments']:
            st.write(f"Date: {appointment['date']}, Time: {appointment['time']}")
            if 'symptoms' in appointment:
                st.write(f"Symptoms: {appointment['symptoms']}")
            if 'reason' in appointment:
                st.write(f"Reason: {appointment['reason']}")
            st.write(f"Doctor: {appointment['doctor_email']}")
            st.write("---")



if __name__ == "__main__":
    main()

