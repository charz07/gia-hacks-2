# -*- coding: utf-8 -*-
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import requests
from groq import Groq


tokenizer = AutoTokenizer.from_pretrained("bvanaken/CORe-clinical-diagnosis-prediction")
model = AutoModelForSequenceClassification.from_pretrained("bvanaken/CORe-clinical-diagnosis-prediction")
groq_client = Groq(api_key="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")

def predict_diagnosis(input):
    input = "CHIEF COMPLAINT: Headaches\n\nPRESENT ILLNESS: 58yo man w/ hx of hypertension, AFib on coumadin presented to ED with the worst headache of his life."
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
        {"role": "system", "content": "Your role is to convert the given ICD9 code to its English description only, with no other words."},
        {"role": "user", "content": code}
  ]
  response = groq_client.chat.completions.create(
      model="llama3-70b-8192",
      messages=messages,
      temperature=0.0,
      max_tokens=4096
  )
  return response.choices[0].message.content.strip()