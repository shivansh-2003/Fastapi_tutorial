from fastapi import FastAPI, Path, HTTPException, Query
import json

def load_data():
    try:
        with open("patient.json", 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="patient.json file not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in patient.json")


app = FastAPI()


@app.get("/view")
def view():
    return load_data()


@app.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(..., description='id of patient in database', example='P001')):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail='Patient not found')


@app.get('/sort')
def sort_patients(
    sort_by: str = Query(..., description="Sort on the basis of height, weight or bmi"),
    order: str = Query("asc", description="sort in asc or desc order")
):
    valid_fields = ['height', 'weight', 'bmi']

    if sort_by not in valid_fields:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid field '{sort_by}'. Select from {valid_fields}"
        )
    
    if order not in ['asc', 'desc']:
        raise HTTPException(
            status_code=400, 
            detail="Invalid order. Select between 'asc' and 'desc'"
        )
    
    data = load_data()

    sorted_data = sorted(
        data.values(), 
        key=lambda x: x.get(sort_by, 0), 
        reverse=(order == 'desc')
    )

    return sorted_data