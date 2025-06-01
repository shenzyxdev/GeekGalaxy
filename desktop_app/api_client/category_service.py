# desktop_app/api_client/category_service.py

import requests
from config import API_BASE_URL
from state_manager.app_state import current_app_state

def get_categories():
    """Busca todas as categorias de produtos da API."""
    token = current_app_state.get_access_token()
    if not token:
        return False, {'detail': "Token de acesso não encontrado. Faça login."}

    headers = {
        'Authorization': f'Bearer {token}'
    }
    url = f"{API_BASE_URL}/categorias/" # Endpoint de categorias
    print(f"CategoryService: Buscando categorias em {url}") # Debug

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Lança erro para status 4xx/5xx
        categories = response.json()
        print(f"CategoryService: {len(categories)} categorias recebidas.") # Debug
        return True, categories
    except requests.exceptions.HTTPError as http_err:
        error_detail = (
            f"Erro HTTP ao buscar categorias: {http_err.response.status_code} - "
            f"{http_err.response.text}"
        )
        print(f"CategoryService: {error_detail}") # Debug
        return False, {'detail': error_detail}
    except requests.exceptions.RequestException as req_err:
        error_detail = f"Erro de conexão ao buscar categorias: {req_err}"
        print(f"CategoryService: {error_detail}") # Debug
        return False, {'detail': error_detail}