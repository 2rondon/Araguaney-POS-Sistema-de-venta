import requests

def obtener_tasa_bcv():
    """
    Obtiene la tasa oficial del BCV desde DolarApi.
    Si falla la conexión, retorna un valor de respaldo (45.0) para garantizar operatividad.
    """
    try:
        response = requests.get("https://ve.dolarapi.com/v1/dolares/oficial", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return float(data.get("promedio", 45.00))
    except Exception:
        pass
    return 45.00  # Valor de respaldo / contingencia