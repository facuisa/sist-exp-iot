import uvicorn
import httpx
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Optional

app = FastAPI(title="Interfaz del Sistema Experto")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

API_BACKEND_URL = "http://127.0.0.1:8000"

@app.get("/", response_class=HTMLResponse)
async def mostrar_formulario(request: Request):
    """Muestra el formulario principal y obtiene los datos dinámicos desde la API."""
    try:
        async with httpx.AsyncClient() as client:
            resp_dispositivos = await client.get(f"{API_BACKEND_URL}/dispositivos")
            resp_sintomas = await client.get(f"{API_BACKEND_URL}/sintomas")
            resp_dispositivos.raise_for_status()
            resp_sintomas.raise_for_status()
            dispositivos = resp_dispositivos.json().get("dispositivos", [])
            sintomas = resp_sintomas.json().get("sintomas", [])
    except httpx.RequestError:
        dispositivos, sintomas = [], [{"valor": "error", "descripcion": "No se pudo conectar con la API."}]
    
    return templates.TemplateResponse("index.html", {
        "request": request, "dispositivos": dispositivos, "sintomas": sintomas
    })

@app.post("/resultado", response_class=HTMLResponse)
async def obtener_diagnostico(
    request: Request,
    nombre: str = Form(...),
    tipo: str = Form(...),
    sintomas: List[str] = Form(...),
    intensidad_wifi: Optional[str] = Form(None),
    tiempo_encendido: Optional[str] = Form(None)
):
    """Recibe los datos del formulario, los envía a la API y muestra el resultado."""
    wifi_val = int(intensidad_wifi) if intensidad_wifi else None
    tiempo_val = int(tiempo_encendido) if tiempo_encendido else None
    
    datos_para_api = {
        "tipo": tipo, "nombre": nombre, "sintomas": sintomas,
        "intensidad_señal_wifi": wifi_val, "tiempo_encendido_dias": tiempo_val
    }

    resultado, error_msg = None, None
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_BACKEND_URL}/diagnosticar", json=datos_para_api)
            response.raise_for_status()
            resultado = response.json()
    except httpx.HTTPStatusError as e:
        error_msg = f"Error de la API: {e.response.status_code} - {e.response.json().get('detail')}"
    except httpx.RequestError:
        error_msg = "No se pudo conectar con el motor de diagnóstico."

    return templates.TemplateResponse("resultado.html", {
        "request": request, "resultado": resultado, "error": error_msg
    })

if __name__ == "__main__":
    uvicorn.run("app_visual:app", host="0.0.0.0", port=8080, reload=True)