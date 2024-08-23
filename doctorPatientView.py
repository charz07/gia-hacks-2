from nicegui import ui
from datetime import date



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

patient = (ehr, consultationHistory, currentAppointments)

#pass in patient object/ tuple, THIS IS A PLACEHOLDER
def getAIdiag(p):
    return "hey its me mr conlin gpt i think this person should get a lobotomy"

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

def save_text(e):
    global saved_text
    saved_text = e.value
    print(f"Text saved: {saved_text}")


# Create a styled label
result = ui.label()
result.style('font-size: 40px; color: #333; font-weight: bold; white-space: pre-wrap')
result.set_text(f"Current Patient Profile: \n")
result1 = ui.label()
result1.style('font-size: 20px; color: #333; font-weight: bold; white-space: pre-wrap')
result1.set_text(f"\n{toString(patient[0])}\n\n{toString(patient[1])}\n\n{toString(patient[2])}")
ui.separator().style('color: #333; height: 3px; margin: 15px 0;')

aiDiag = ui.label()
aiDiag.style('font-size: 20px; color: #333; font-weight: bold; white-space: pre-wrap')
aiDiag.set_text(f"Here is our AI diagnostic, please use this as a tool for you decisions, not as something to copy\n\n {getAIdiag(patient)}")
ui.separator().style('color: #333; height: 3px; margin: 15px 0;')

# Create a text area
text_area = ui.textarea(
    label="Enter Diagnoses",
    placeholder="Type something...",
    on_change=save_text
).style(
    'width: 400px; height: 200px; background-color: #f0f0f0;'
)



# Start the NiceGUI app
print("\n\n\n\n\n\n\nThe file itself is being updated\n\n\n\n")
ui.run()
