from pydantic import BaseModel, EmailStr, AnyUrl,Field , field_validator
from typing import List, Dict,Optional,Annotated


class Patient(BaseModel):
    name: Annotated[str, Field(max_length=50, title='Name of the patient', description='Give the name of the patient in less than 50 chars', examples=['Nitish', 'Amit'])]
    age: int=Field(gt=0,lt=130)
    gaymail: EmailStr
    lankdin_url: AnyUrl
    weight: float
    biyahoelebaa:Optional[str]=None 
    bimari:  Annotated[Optional[List[str]], Field(default=None, max_length=5)]
    samsoongkano: Dict[str, str]

    


def update_patient_data(patient: Patient):
    print(patient.name)
    print(patient.age)
    print(patient.gaymail)          # Fixed: was trying to access 'allergies'
    print(patient.lankdin_url)      # Fixed: was trying to access 'married'
    print('updated')


# Updated patient_info to match the exact field names in Patient class
patient_info = {
    "name": "nitish",
    "age": 30,                       # Must be int
    "gaymail": "abc@gmail.com",      # Matches class field
    "lankdin_url": "http://linkedin.com/1322",  # Matches class field
    "weight": 75.2,
    "biyahoelebaa": "Yes",           # Example value (adjust as needed)
    "bimari": ["Diabetes", "Asthma"],  # List of strings
    "samsoongkano": {"phone": "2353462", "address": "Delhi"}  # Dict[str, str]
}

# Create Patient instance
patient1 = Patient(**patient_info)

# Call the function
update_patient_data(patient1)