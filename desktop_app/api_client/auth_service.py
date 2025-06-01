# desktop_app/api_client/auth_service.py

import requests
from config import API_BASE_URL

def login_user(username, password):
    # ... (código da função login_user que já temos - sem alterações aqui) ...
    login_url = f"{API_BASE_URL}/token/"
    credentials = {
        'username': username,
        'password': password
    }
    print(f"Auth Service: Tentando login em {login_url} com usuário '{username}'")
    try:
        response = requests.post(login_url, data=credentials, timeout=10)
        response.raise_for_status()
        tokens = response.json()
        print(f"Auth Service: Tokens recebidos.") # Não imprimir tokens inteiros no console por segurança
        return True, tokens
    except requests.exceptions.HTTPError as http_err:
        if http_err.response.status_code == 401:
            error_detail = http_err.response.json().get('detail', 'Credenciais inválidas fornecidas à API.')
            print(f"Auth Service: Erro 401 - {error_detail}")
            return False, {'detail': error_detail}
        else:
            error_detail = (
                f"Erro HTTP da API: {http_err.response.status_code} - "
                f"{http_err.response.text}"
            )
            print(f"Auth Service: {error_detail}")
            return False, {'detail': error_detail}
    except requests.exceptions.RequestException as req_err:
        error_detail = f"Erro de conexão com a API: {req_err}"
        print(f"Auth Service: {error_detail}")
        return False, {'detail': error_detail}

# NOVA FUNÇÃO ADICIONADA ABAIXO:
def get_current_user_details(access_token):
    """
    Busca os detalhes do usuário logado usando o token de acesso.
    Retorna uma tupla: (sucesso_boolean, dados_usuario_dict_ou_erro_dict)
    """
    me_url = f"{API_BASE_URL}/usuarios/me/" # Nosso novo endpoint
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    print(f"Auth Service: Buscando detalhes do usuário em {me_url}") # Debug
    try:
        response = requests.get(me_url, headers=headers, timeout=10)
        response.raise_for_status() # Lança erro para status 4xx/5xx

        user_details = response.json()
        print(f"Auth Service: Detalhes do usuário recebidos: {user_details.get('username')}") # Debug
        return True, user_details

    except requests.exceptions.HTTPError as http_err:
        error_detail = (
            f"Erro HTTP ao buscar detalhes do usuário: {http_err.response.status_code} - "
            f"{http_err.response.text}"
        )
        print(f"Auth Service: {error_detail}") # Debug
        return False, {'detail': error_detail}
    except requests.exceptions.RequestException as req_err:
        error_detail = f"Erro de conexão ao buscar detalhes do usuário: {req_err}"
        print(f"Auth Service: {error_detail}") # Debug
        return False, {'detail': error_detail}