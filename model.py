# -*- coding: utf-8 -*-
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import requests
from groq import Groq


tokenizer = AutoTokenizer.from_pretrained("bvanaken/CORe-clinical-diagnosis-prediction")
model = AutoModelForSequenceClassification.from_pretrained("bvanaken/CORe-clinical-diagnosis-prediction")
groq_client = Groq(api_key="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")

# inputs a list of symptoms and medical history, output text in patient note form 
def symptom_to_patient_note(symptoms):
    messages = [
        {"role": "system", "content": """
        Given the following formatfor patient notes(add more categories if additional information is provided):
CHIEF COMPLAINT: Knee pain.

PRESENT ILLNESS: HPI: Patient is woman w/ a hx of ESRD on HD, waiting for transplant, and hypertension who presented with sudden onset right knee pain. She noted that her knee was swollen with reduced range of motion. Pain present at rest and with motion. Pt also noted fevers and chills the night before, but no nausea or vomiting. She did not recall any trauma to the knee. She is on a dialysis schedule, but because of increased pain and swelling, presented to ED instead of usual HD. Her knee was aspirated and returned pus, consistent with septic arthritis. Pt taken to the OR by plastic surgery for wash-out of pus in the joint and placement of Penrose drain. 

MEDICATION ON ADMISSION: Nephrocaps daily Clonidine 0.1 mg daily Moexipril 15 mg in the morning and 30mg in the evening Metoprolol 50 mg [**Hospital1 **] Minoxidil 5 mg daily Lorazepam or valium at night

ALLERGIES: Patient recorded as having No Known Allergies to Drugs

PHYSICAL EXAM: VITALS: 98.4 HR 98 192/131 21 100%RA  Gen: Alert and oriented. No acute distress. Sclerae anicteric. HEENT: pupils minimally reactive, + oral thrush CV: regular, S1 S2, no murmurs Extrem: WWP. No edema.  R Knee wound w/ erythema and swelling.  Neuro: A&Ox3, CNII-XII intact, sensation and strength grossly intact in all extremities. Very inattentive. Comprehension intact to 2 step commands. Unclear if pain complicating strength exam. Proprioception intact. Unable to cooperate w/ finger to nose testing.

FAMILY HISTORY: Brother died of emphysema, smoker. Father died of liver cancer at age 66.

SOCIAL HISTORY: Tobacco history: history of [**12-10**] pack for 10 yrs. Denies ETOH, IVDU. Pt lives with husband and son in [**Name (NI) **].
         
        Generate the patient notes for the provided symptom list
         """},
        {"role": "user", "content": str(symptoms)}
    ]
    response = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages,
        temperature=0.0,
        max_tokens=4096
    )
    return response.choices[0].message.content.strip()

def predict_diagnosis(input):
    tokenized_input = tokenizer(input, return_tensors="pt")
    output = model(**tokenized_input)

    predictions = torch.sigmoid(output.logits)
    predicted_labels = [model.config.id2label[_id] for _id in (predictions > 0.3).nonzero()[:, 1].tolist()]

    icd9_codes = [code for code in predicted_labels if code.isdigit() or code.startswith('V') or code.startswith('E')]

    return icd9_codes

# bad conversion of icd9 to english, need to find a way to map codes to description
# hallucinates for V and E starting icd9 codes
def icd9_to_english(code):
  messages = [
        {"role": "system", "content": """
        Your role is to convert the given ICD9 code to its English description only.
        Under the standard ICD9 code english description, write a short paragraph describing the   
        ailment and recommended treatment methods. Do not restate the prompt in any way, only provide
        the ICD9 code, description, and recommendations
        """},
        {"role": "user", "content": str(code)}
  ]
  response = groq_client.chat.completions.create(
      model="llama3-70b-8192",
      messages=messages,
      temperature=0.0,
      max_tokens=4096
  )
  return response.choices[0].message.content.strip()

if __name__ == "__main__":
   patient_info_test = patient_info = {
        "personal_details": {
            "name": "Jane Doe",
            "age": 42,
            "gender": "Female",
            "occupation": "Teacher",
            "marital_status": "Married"
        },
        "medical_history": {
            "allergies": ["Penicillin", "Pollen"],
            "chronic_conditions": ["Asthma", "Hypertension"],
            "previous_surgeries": ["Appendectomy (2010)", "Knee arthroscopy (2018)"],
            "family_history": {
                "diabetes": "Mother",
                "heart_disease": "Father",
                "breast_cancer": "Maternal aunt"
            }
        },
        "current_symptoms": [
            {
                "symptom": "Headache",
                "duration": "3 days",
                "severity": "Moderate",
                "location": "Frontal and temporal regions"
            },
            {
                "symptom": "Fatigue",
                "duration": "1 week",
                "severity": "Severe",
                "additional_info": "Interfering with daily activities"
            },
            {
                "symptom": "Nausea",
                "duration": "2 days",
                "severity": "Mild",
                "frequency": "Intermittent"
            },
            {
                "symptom": "Dizziness",
                "duration": "3 days",
                "severity": "Moderate",
                "triggers": "Standing up quickly"
            }
        ],
        "vital_signs": {
            "blood_pressure": "140/90 mmHg",
            "heart_rate": "88 bpm",
            "temperature": "37.2°C",
            "respiratory_rate": "16 breaths/min"
        },
        "medications": [
            {
                "name": "Lisinopril",
                "dosage": "10 mg",
                "frequency": "Once daily"
            },
            {
                "name": "Albuterol inhaler",
                "dosage": "2 puffs",
                "frequency": "As needed"
            }
        ],
        "lifestyle_factors": {
            "smoking": "Non-smoker",
            "alcohol_consumption": "Occasional (1-2 drinks per week)",
            "exercise": "Moderate (30 minutes of walking, 3 times a week)",
            "diet": "Balanced, with occasional fast food"
        }
    }
   note = symptom_to_patient_note(patient_info_test)
   print(note)
   diagnosis = predict_diagnosis(note)
   print(diagnosis)
   print(icd9_to_english(diagnosis))
