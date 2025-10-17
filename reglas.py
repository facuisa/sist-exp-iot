# Carga la base de conocimiento desde un JSON y contiene el motor de inferencia.

import json
from typing import List
from modelos import DispositivoInput, Diagnostico, TipoDispositivo, Sintoma, Causa, NivelCriticidad

class BaseConocimiento:
    def __init__(self, ruta_json='base_conocimiento.json'):
        try:
            with open(ruta_json, 'r', encoding='utf-8') as f:
                conocimiento = json.load(f)
                self.reglas = conocimiento['reglas_por_sintoma']
                self.reglas_dispositivo = conocimiento['reglas_por_dispositivo']
            print("✅ Base de conocimiento cargada exitosamente desde base_conocimiento.json")
        except Exception as e:
            print(f"❌ ERROR al cargar la base de conocimiento: {e}")
            self.reglas = {}
            self.reglas_dispositivo = {}

    def obtener_diagnosticos(self, dispositivo: DispositivoInput) -> List[Diagnostico]:
        diagnosticos = []
        for sintoma_enum in dispositivo.sintomas:
            sintoma_str = sintoma_enum.value
            if sintoma_str in self.reglas:
                for regla in self.reglas[sintoma_str]:
                    prob_base = regla['probabilidad_base']
                    categoria = Causa(regla['categoria'])
                    probabilidad_ajustada = prob_base

                    if dispositivo.tipo.value in self.reglas_dispositivo:
                        regla_disp = self.reglas_dispositivo[dispositivo.tipo.value]
                        if categoria == Causa.HARDWARE and "factor_hardware" in regla_disp:
                            probabilidad_ajustada *= regla_disp["factor_hardware"]
                        elif categoria == Causa.RED and "factor_red" in regla_disp:
                            probabilidad_ajustada *= regla_disp["factor_red"]
                    
                    if categoria == Causa.RED and dispositivo.intensidad_señal_wifi is not None:
                        if dispositivo.intensidad_señal_wifi < -80: probabilidad_ajustada *= 1.3
                        elif dispositivo.intensidad_señal_wifi > -60: probabilidad_ajustada *= 0.7
                    
                    if categoria == Causa.SOFTWARE and dispositivo.ultima_actualizacion_firmware:
                        probabilidad_ajustada *= 0.9
                    
                    if categoria == Causa.HARDWARE and dispositivo.tiempo_encendido_dias is not None:
                        if dispositivo.tiempo_encendido_dias > 90: probabilidad_ajustada *= 1.2

                    diagnostico = Diagnostico(
                        causa=regla['causa'],
                        categoria=categoria,
                        probabilidad=min(round(probabilidad_ajustada, 2), 100.0),
                        solucion=regla['solucion']
                    )
                    diagnosticos.append(diagnostico)

        diagnosticos_unicos = {diag.causa: diag for diag in sorted(diagnosticos, key=lambda x: x.probabilidad)}
        return sorted(list(diagnosticos_unicos.values()), key=lambda x: x.probabilidad, reverse=True)

    def calcular_criticidad(self, dispositivo: DispositivoInput, diagnosticos: List[Diagnostico]) -> NivelCriticidad:
        reglas_disp = self.reglas_dispositivo.get(dispositivo.tipo.value, {})
        sintomas_criticos = reglas_disp.get("sintomas_criticos", [])
        
        if any(s.value in sintomas_criticos for s in dispositivo.sintomas):
            if dispositivo.tipo in [TipoDispositivo.CERRADURA_INTELIGENTE, TipoDispositivo.CAMARA_SEGURIDAD, TipoDispositivo.SENSOR_AGUA]:
                return NivelCriticidad.CRITICA
            return NivelCriticidad.ALTA

        if diagnosticos and diagnosticos[0].probabilidad > 80:
            if diagnosticos[0].categoria in [Causa.ENERGIA, Causa.HARDWARE]:
                return NivelCriticidad.ALTA
            return NivelCriticidad.MEDIA

        if len(dispositivo.sintomas) >= 3: return NivelCriticidad.ALTA
        if len(dispositivo.sintomas) >= 2: return NivelCriticidad.MEDIA
        return NivelCriticidad.BAJA