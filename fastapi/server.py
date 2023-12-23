from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class InputData(BaseModel):
    name: str

@app.post("/save_brand/")
def save_brand(data: InputData):
    return {"message": f"Se ha añadido {data.name} a tu lista de favoritos"}

@app.post("/delete_brand/")
def delete_brand(data: InputData):
    return {"message": f"Se ha eliminado {data.name} de tu lista de favoritos"}