from nicegui import ui

symptom_list = [
    'Fever', 'Cough', 'Headache', 'Fatigue', 'Shortness of breath', 
    'Sore throat', 'Runny nose', 'Muscle ache', 'Loss of taste or smell',
    'Nausea', 'Vomiting', 'Diarrhea', 'Chest pain', 'Dizziness'
]

symptom_selectors = []

def add_symptom_selector():
    with symptom_container:
        selector = ui.select(symptom_list, label='Select Symptom').classes('w-full mt-2')
        symptom_selectors.append(selector)

def submit_symptoms():
    symptoms = [selector.value for selector in symptom_selectors if selector.value]
    if other_symptom.value:
        symptoms.append(other_symptom.value)
    ui.notify(f"Symptoms submitted: {', '.join(symptoms)}")

with ui.card().classes('w-full max-w-3xl mx-auto'):
    ui.label('Symptom Input Form').classes('text-2xl font-bold mb-4')
    
    with ui.row().classes('w-full items-start'):
        with ui.column().classes('w-3/4'):
            symptom_container = ui.column().classes('w-full')
            add_symptom_selector()
            other_symptom = ui.input('Other symptom (if not listed above)').classes('w-full mt-4')
        
        with ui.column().classes('w-1/4 ml-4'):
            with ui.row().classes('gap-2'):
                ui.button('+', on_click=add_symptom_selector).classes('h-10')
                ui.button('Submit', on_click=submit_symptoms).classes('h-10')

ui.run()