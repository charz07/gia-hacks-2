from nicegui import ui

def submit_form():
    ui.notify(f"Form submitted for {name.value}")

with ui.card().classes('w-full max-w-5xl mx-auto'):
    ui.label('Patient Information Form').classes('text-2xl font-bold mb-4')
    
    name = ui.input('Full Name').classes('w-full')
    
    ui.label('Date of Birth').classes('mt-4')
    dob = ui.date().classes('w-full')
    
    with ui.row().classes('w-full gap-4 mt-4'):
        gender = ui.select(['Male', 'Female', 'Other'], label='Gender').classes('flex-grow')
        phone = ui.input('Phone Number').classes('flex-grow')
    
    with ui.row().classes('w-full gap-4 mt-4'):
        email = ui.input('Email').classes('flex-grow')
        address = ui.input('Address').classes('flex-grow')
    
    ui.button('Submit', on_click=submit_form).classes('mt-4')

ui.run()