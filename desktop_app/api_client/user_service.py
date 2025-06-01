# desktop_app/api_client/user_service.py

import requests
import json # Para o corpo do POST/PUT
from config import API_BASE_URL
from state_manager.app_state import current_app_state

def _get_auth_headers():
    """Retorna os cabeçalhos de autenticação ou None se não houver token."""
    token = current_app_state.get_access_token()
    if not token:
        print("UserService: Token de acesso não encontrado.")
        return None
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

def get_users():
    """Busca todos os usuários da API."""
    headers = _get_auth_headers()
    if not headers:
        return False, {'detail': "Usuário não autenticado."}

    url = f"{API_BASE_URL}/usuarios/"
    print(f"UserService: Buscando usuários em {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        users = response.json()
        # DRF ModelViewSet geralmente retorna uma lista diretamente para listagem sem paginação
        # Se houver paginação, seria users.get('results', [])
        if isinstance(users, dict) and 'results' in users: # Lida com paginação
            users_list = users['results']
            print(f"UserService: {len(users_list)} usuários recebidos (de {users.get('count', '?')}).")
            return True, users_list
        elif isinstance(users, list):
            print(f"UserService: {len(users)} usuários recebidos.")
            return True, users
        else:
            print(f"UserService: Resposta inesperada ao listar usuários: {users}")
            return False, {'detail': 'Formato de resposta inesperado da API.'}
    except requests.exceptions.HTTPError as http_err:
        error_detail = f"Erro HTTP ao buscar usuários: {http_err.response.status_code} - {http_err.response.text}"
        print(f"UserService: {error_detail}")
        return False, {'detail': error_detail}
    except requests.exceptions.RequestException as req_err:
        error_detail = f"Erro de conexão ao buscar usuários: {req_err}"
        print(f"UserService: {error_detail}")
        return False, {'detail': error_detail}

def get_user_details(user_id):
    """Busca os detalhes de um usuário específico."""
    headers = _get_auth_headers()
    if not headers:
        return False, {'detail': "Usuário não autenticado."}

    url = f"{API_BASE_URL}/usuarios/{user_id}/"
    print(f"UserService: Buscando detalhes do usuário ID {user_id} em {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.HTTPError as http_err:
        error_detail = f"Erro HTTP ao buscar detalhes do usuário {user_id}: {http_err.response.status_code} - {http_err.response.text}"
        print(f"UserService: {error_detail}")
        return False, {'detail': error_detail}
    except requests.exceptions.RequestException as req_err:
        error_detail = f"Erro de conexão ao buscar detalhes do usuário {user_id}: {req_err}"
        print(f"UserService: {error_detail}")
        return False, {'detail': error_detail}


def create_user(user_data):
    """
    Cria um novo usuário na API.
    user_data deve conter: username, password, email (opc), first_name (opc),
                           last_name (opc), groups_ids (lista de IDs de grupo, opc),
                           is_active (opc), is_staff (opc).
                           is_superuser NÃO deve ser enviado por um Supervisor.
    """
    headers = _get_auth_headers()
    if not headers:
        return False, {'detail': "Usuário não autenticado."}

    url = f"{API_BASE_URL}/usuarios/"
    print(f"UserService: Criando usuário em {url} com dados: {user_data}")
    try:
        response = requests.post(url, headers=headers, json=user_data, timeout=15)
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.HTTPError as http_err:
        try:
            error_body = http_err.response.json()
            error_detail = f"Erro HTTP ({http_err.response.status_code}): {json.dumps(error_body)}"
        except ValueError:
            error_detail = f"Erro HTTP ({http_err.response.status_code}): {http_err.response.text}"
        print(f"UserService: Erro ao criar usuário - {error_detail}")
        return False, {'detail': error_detail}
    except requests.exceptions.RequestException as req_err:
        error_detail = f"Erro de conexão ao criar usuário: {req_err}"
        print(f"UserService: {error_detail}")
        return False, {'detail': error_detail}

def update_user(user_id, user_data):
    """
    Atualiza um usuário existente na API.
    user_data pode conter os mesmos campos de create_user.
    A senha é opcional; se fornecida, será atualizada.
    """
    headers = _get_auth_headers()
    if not headers:
        return False, {'detail': "Usuário não autenticado."}

    url = f"{API_BASE_URL}/usuarios/{user_id}/"
    print(f"UserService: Atualizando usuário ID {user_id} em {url} com dados: {user_data}")
    try:
        # Usar PATCH para atualização parcial é geralmente melhor para não ter que enviar todos os campos.
        # Se o serializer no backend estiver configurado para partial=True, o PUT também pode funcionar parcialmente.
        # Vamos usar PUT por enquanto, assumindo que enviaremos todos os dados editáveis.
        response = requests.put(url, headers=headers, json=user_data, timeout=15)
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.HTTPError as http_err:
        try:
            error_body = http_err.response.json()
            error_detail = f"Erro HTTP ({http_err.response.status_code}): {json.dumps(error_body)}"
        except ValueError:
            error_detail = f"Erro HTTP ({http_err.response.status_code}): {http_err.response.text}"
        print(f"UserService: Erro ao atualizar usuário ID {user_id} - {error_detail}")
        return False, {'detail': error_detail}
    except requests.exceptions.RequestException as req_err:
        error_detail = f"Erro de conexão ao atualizar usuário ID {user_id}: {req_err}"
        print(f"UserService: {error_detail}")
        return False, {'detail': error_detail}

def get_groups():
    """Busca todos os grupos de permissão da API."""
    headers = _get_auth_headers()
    if not headers:
        return False, {'detail': "Usuário não autenticado."}

    url = f"{API_BASE_URL}/grupos/" # Endpoint de listagem de grupos
    print(f"UserService: Buscando grupos em {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        groups = response.json()
        if isinstance(groups, dict) and 'results' in groups: # Lida com paginação
            groups_list = groups['results']
            print(f"UserService: {len(groups_list)} grupos recebidos (de {groups.get('count', '?')}).")
            return True, groups_list
        elif isinstance(groups, list):
            print(f"UserService: {len(groups)} grupos recebidos.")
            return True, groups
        else:
            print(f"UserService: Resposta inesperada ao listar grupos: {groups}")
            return False, {'detail': 'Formato de resposta inesperado da API para grupos.'}
    except requests.exceptions.HTTPError as http_err:
        error_detail = f"Erro HTTP ao buscar grupos: {http_err.response.status_code} - {http_err.response.text}"
        print(f"UserService: {error_detail}")
        return False, {'detail': error_detail}
    except requests.exceptions.RequestException as req_err:
        error_detail = f"Erro de conexão ao buscar grupos: {req_err}"
        print(f"UserService: {error_detail}")
        return False, {'detail': error_detail}

# delete_user pode ser implementado depois, ou podemos focar em ativar/desativar (update com is_active=False)
# def delete_user(user_id):
#     pass