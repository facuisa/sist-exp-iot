# Definición de modelos Pydantic y enumeraciones de datos.

# Definición de modelos Pydantic y enumeraciones de datos.

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime

# ENUMERACIONES
class TipoDispositivo(str, Enum):
    TERMOSTATO = "termostato"
    LUZ_INTELIGENTE = "luz_inteligente"
    CAMARA_SEGURIDAD = "camara_seguridad"
    CERRADURA_INTELIGENTE = "cerradura_inteligente"
    ASISTENTE_VOZ = "asistente_voz"
    SENSOR_AGUA = "sensor_agua"

class Sintoma(str, Enum):
    NO_RESPONDE = "no_responde"
    ERROR_CONEXION = "error_conexion"
    REINICIOS_FRECUENTES = "reinicios_frecuentes"
    CONSUMO_ANOMALO = "consumo_anomalo"
    LATENCIA_ALTA = "latencia_alta"
    FALLA_AUTENTICACION = "falla_autenticacion"

class Causa(str, Enum):
    HARDWARE = "hardware"
    SOFTWARE = "software"
    RED = "red"
    CONFIGURACION = "configuracion"
    ENERGIA = "energia"

class NivelCriticidad(str, Enum):
    CRITICA = "critica"
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"

# MODELOS DE DATOS
class DispositivoInput(BaseModel):
    tipo: TipoDispositivo
    nombre: str
    sintomas: List[Sintoma]
    ultima_actualizacion_firmware: Optional[str] = None
    intensidad_señal_wifi: Optional[int] = Field(None, ge=-100, le=0)
    tiempo_encendido_dias: Optional[int] = None

class Diagnostico(BaseModel):
    causa: str
    categoria: Causa
    probabilidad: float = Field(..., ge=0, le=100)
    solucion: str

class Resultado(BaseModel):
    dispositivo: str
    tipo: TipoDispositivo
    criticidad: NivelCriticidad
    diagnosticos: List[Diagnostico]
    recomendacion_principal: str
    requiere_alerta: bool
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())