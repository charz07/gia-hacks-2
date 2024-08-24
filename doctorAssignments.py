from nicegui import ui
from datetime import date

from doctorPatientView import viewPatient


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

patients = [(ehr, consultationHistory, currentAppointments), (ehr, consultationHistory, currentAppointments)]

# Create a styled label
result = ui.label()
result.style('font-size: 40px; color: #333; font-weight: bold; white-space: pre-wrap')
result.set_text(f"All of your patients: \n")

for i in patients:
    result = ui.label()
    result.style('font-size: 20px; color: #333; font-weight: bold; white-space: pre-wrap')
    result.set_text(f"\n{i[0]['name']}:")
    with ui.expansion('Profile', caption='See Charts and Enter Diagnoses').classes('w-full'):
        viewPatient(i)
    ui.separator().style('color: #333; height: 3px; margin: 15px 0;')

first = True
ui.run()
