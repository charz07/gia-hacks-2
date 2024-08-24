from nicegui import ui
from datetime import date

from doctorPatientView import viewPatient

class samplePatient():
    ehr = {
            'name': 'Sophia Yan',
            'dob': '1980-01-01',
            'gender': 'Male',
            'allergies': ['Penicillin', 'Peanuts'],
            'medications': ['Lisinopril', 'Metformin'],
            'conditions': ['Hypertension', 'Type 2 Diabetes']
        }

    consultationHistory = {
            'Medical History' : ['\n1981-02-03: blood transfusion due to blood loss from trampoline accident ', '\n1981-02-05: second blood transfusion due to rejection of previous transfusion']
    }

    currentAppointments = {
            'Scheduled Appointments' : '2024-08-23'
    }

    diagnoses = []

def toString(profile):
    output = ''
    
    if isinstance(profile, dict):
        for key, value in profile.items():
            if isinstance(value, list):
                output += f"{key}: {', '.join(map(str, value))}\n"
            else:
                output += f"{key}: {value}\n"
    elif isinstance(profile, str):
        output = profile

    print(output)
    return output


patient = samplePatient()

#LOAD PATIENT PROFILE GIVEN DOCTOR PROFILE 
requests = [(patient, "2024-08-23")]
result = ui.label()
result.style('font-size: 40px; color: #333; font-weight: bold; white-space: pre-wrap')
result.set_text(f"Current Requests for Appointments \n")

def saveAppointment():
    result.delete()
    result1.delete()
    button.delete()
    print("hello") 
    ui.notify("Appointment Accepted!")
    #ADD APPOINTMENT TO RELEVANT DATA (BOTH DOCTOR AND PATIENT)
    return

for request in requests:
    result = ui.label()
    result.style('font-size: 20px; color: #333; font-weight: bold; white-space: pre-wrap')
    result.set_text(f"Patient Profile: \n")
    result1 = ui.label()
    result1.style('font-size: 20px; color: #333; font-weight: bold; white-space: pre-wrap;background-color: #f0f0f0')
    result1.set_text(f"\n{toString(request[0].ehr)}\n\n{toString(request[0].consultationHistory)}\n\n{toString(request[0].currentAppointments)}")
    
    button = ui.button('Accept', on_click=saveAppointment)

    ui.separator().style('color: #333; height: 3px; margin: 15px 0;')

ui.run()