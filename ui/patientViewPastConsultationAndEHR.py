from nicegui import ui
from datetime import datetime, timedelta
import random

# Mock data for demonstration
def generate_mock_data():
    consultations = [
        {
            'date': (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d'),
            'type': random.choice(['General', 'Technical', 'Business']),
            'notes': f"Consultation notes {i+1}"
        } for i in range(5)
    ]
    
    ehr = {
        'name': 'Sophia Yan',
        'dob': '1980-01-01',
        'gender': 'Male',
        'allergies': ['Penicillin', 'Peanuts'],
        'medications': ['Lisinopril', 'Metformin'],
        'conditions': ['Hypertension', 'Type 2 Diabetes']
    }
    
    return consultations, ehr

@ui.page('/')
def main_page():
    ui.label('Consultation Request Form').classes('text-h4')
    ui.button('View History', on_click=lambda: ui.open('/history'))

@ui.page('/history')
def history_page():
    consultations, ehr = generate_mock_data()
    
    with ui.column().classes('w-full max-w-3xl mx-auto'):
        ui.label('Consultation History and EHR Summary').classes('text-h4 q-mb-md')
        
        ui.button('Back to Consultation Form', on_click=lambda: ui.open('/')).classes('q-mb-lg')
        
        # EHR Summary
        with ui.card().classes('w-full q-mb-md'):
            ui.label('EHR Summary').classes('text-h5 q-mb-sm')
            ui.label(f"Name: {ehr['name']}")
            ui.label(f"Date of Birth: {ehr['dob']}")
            ui.label(f"Gender: {ehr['gender']}")
            ui.label(f"Allergies: {', '.join(ehr['allergies'])}")
            ui.label(f"Medications: {', '.join(ehr['medications'])}")
            ui.label(f"Conditions: {', '.join(ehr['conditions'])}")
        
        # Consultation History
        ui.label('Consultation History').classes('text-h5 q-mb-sm')
        for consultation in consultations:
            with ui.card().classes('w-full q-mb-sm'):
                ui.label(f"Date: {consultation['date']}")
                ui.label(f"Type: {consultation['type']}")
                ui.label(f"Notes: {consultation['notes']}")

ui.run()