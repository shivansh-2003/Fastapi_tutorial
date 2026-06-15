from fastapi import FastAPI
import json

def load_data():
    with open('patient.json','r') as f:
        data = json.load(f)
    return data    
 
app = FastAPI()

@app.get("/")
def hello():
    return {'message':'patient management system api'}

@app.get("/view")
def view():
    data = load_data()
    return data