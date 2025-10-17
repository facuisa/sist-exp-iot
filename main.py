# Archivo principal de FastAPI con todos los endpoints.

from fastapi import FastAPI, HTTPException
from modelos import DispositivoInput, Resultado, TipoDispositivo, Sintoma
from reglas import BaseConocimiento

app = FastAPI(
    title="SISTEMA EXPERTO IoT",
    description="API PARA DIAGNOSTICO INTELIGENTE DE DISPOSITIVOS INTELIGENTES DEL HOGAR",
    version="2.0.0" # Versión actualizada
)

base_conocimiento = BaseConocimiento()

def obtener_descripcion_sintoma(sintoma: Sintoma) -> str:
    descripciones = {
        Sintoma.NO_RESPONDE: "El dispositivo no reacciona a comandos ni muestra actividad.",
        Sintoma.ERROR_CONEXION: "Fallas recurrentes al conectar con WiFi o servidor cloud.",
        Sintoma.REINICIOS_FRECUENTES: "El dispositivo se apaga y enciende sin intervención.",
        Sintoma.CONSUMO_ANOMALO: "Consumo eléctrico fuera de especificaciones normales.",
        Sintoma.LATENCIA_ALTA: "Retardo superior a 2 segundos en responder comandos.",
        Sintoma.FALLA_AUTENTICACION: "Errores de login, tokens inválidos o acceso denegado."
    }
    return descripciones.get(sintoma, "Sin descripción.")

@app.get("/")
def raiz():
    return {"mensaje": "SISTEMA EXPERTO IoT ACTIVO"}

@app.post("/diagnosticar", response_model=Resultado)
def diagnosticar_dispositivo(dispositivo: DispositivoInput):
    if not dispositivo.sintomas:
        raise HTTPException(status_code=400, detail="Debe proporcionar al menos un síntoma.")

    diagnosticos = base_conocimiento.obtener_diagnosticos(dispositivo)
    if not diagnosticos:
        raise HTTPException(status_code=404, detail="No se encontraron diagnósticos para los síntomas.")

    criticidad = base_conocimiento.calcular_criticidad(dispositivo, diagnosticos)
    requiere_alerta = (criticidad == criticidad.CRITICA)
    
    diag_principal = diagnosticos[0]
    recomendacion = f"[{diag_principal.categoria.value.upper()}] {diag_principal.solucion}"
    if requiere_alerta:
        recomendacion = f"⚠️ URGENTE: {recomendacion}"

    return Resultado(
        dispositivo=dispositivo.nombre,
        tipo=dispositivo.tipo,
        criticidad=criticidad,
        diagnosticos=diagnosticos[:5],
        recomendacion_principal=recomendacion,
        requiere_alerta=requiere_alerta,
    )

@app.get("/sintomas")
def listar_sintomas():
    return {
        "sintomas": [
            {"valor": s.value, "nombre": s.name, "descripcion": obtener_descripcion_sintoma(s)}
            for s in Sintoma
        ]
    }

@app.get("/dispositivos")
def listar_dispositivos():
    return {
        "dispositivos": [
            {"tipo": t.value, "nombre": t.name} for t in TipoDispositivo
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)