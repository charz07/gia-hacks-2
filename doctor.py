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
    output = "hello"
    return output



# Define your map of dates to values
date_values = {
    '2024-08-22': ehr,
    '2024-08-23': "Profile B",
    '2024-08-24': "Profile C",
}

# Define a function to update the label based on the selected date
def update_label(e):
    print("hello")
    selected_date = e.value
    value = date_values.get(selected_date, "No event on this date")
    result.set_text(f"Selected Date: {selected_date}\n{toString(value)}")

# Create a date picker and bind the change event to update the label
ui.date(value='2024-08-22', on_change=update_label)

# Create a styled label
result = ui.label()
result.style('font-size: 20px; color: #333; font-weight: bold; white-space: pre-wrap')

# Start the NiceGUI app
ui.run()
