from nicegui import ui
from datetime import datetime, timedelta
import asyncio

async def link_google_calendar():
    await asyncio.sleep(2)
    ui.notify("Google Calendar linked successfully!")

def generate_time_slots(date):
    start_time = datetime.combine(date, datetime.min.time()).replace(hour=9)
    end_time = start_time.replace(hour=17)
    time_slots = []
    while start_time < end_time:
        time_slots.append(start_time.strftime("%I:%M %p"))
        start_time += timedelta(minutes=30)
    return time_slots

@ui.page('/')
def consultation_form():
    with ui.column().classes('w-full max-w-3xl mx-auto'):
        ui.label("Consultation Request and Scheduling Form").classes('text-h4 q-my-md')

        with ui.row().classes('w-full'):
            ui.label("Name:").classes('w-1/4')
            name_input = ui.input(placeholder="Enter your name").classes('w-3/4')

        with ui.row().classes('w-full'):
            ui.label("Email:").classes('w-1/4')
            email_input = ui.input(placeholder="Enter your email").classes('w-3/4')

        with ui.row().classes('w-full'):
            ui.label("Consultation Type:").classes('w-1/4')
            consultation_type = ui.select(['General', 'Technical', 'Business'], label="Select type").classes('w-3/4')

        ui.label("Scheduling Options:").classes('text-h6 q-mt-md')

        with ui.row().classes('w-3/4'):
            google_calendar_btn = ui.button("Link Google Calendar", on_click=link_google_calendar).classes('w-3/4')

        ui.label("Or choose a date and time manually:").classes('text-h6 q-mt-md')

        with ui.row().classes('w-full'):
            ui.label("Date:").classes('w-1/4')
            date_picker = ui.date(value=datetime.now()).classes('w-3/4')

        with ui.row().classes('w-full'):
            ui.label("Time:").classes('w-1/4')
            time_slot_select = ui.select(generate_time_slots(datetime.now().date()), label="Select time slot").classes('w-3/4')

        def update_time_slots(e):
            time_slot_select.options.clear()
            time_slot_select.options.extend(generate_time_slots(e.value))
            time_slot_select.update()

        date_picker.on('change', update_time_slots)

        def submit():
            ui.notify(f"Consultation request submitted for {name_input.value} on {date_picker.value} at {time_slot_select.value}")

        ui.button("Submit Request", on_click=submit).classes('w-full q-mt-md')

ui.run()