# desktop_app/api_client/client_service.py

import requests
from config import API_BASE_URL
from state_manager.app_state import current_app_state

def get_clients():
    """Busca todos os clientes da API."""
    token = current_app_state.get_access_token()
    if not token:
        return False, {'detail': "Token de acesso não encontrado. Faça login."}

    headers = {'Authorization': f'Bearer {token}'}
    url = f"{API_BASE_URL}/clientes/"
    print(f"ClientService: Buscando clientes em {url}")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        clients = response.json()
        print(f"ClientService: {len(clients)} clientes recebidos.")
        return True, clients
    except requests.exceptions.HTTPError as http_err:
        error_detail = (f"Erro HTTP ao buscar clientes: {http_err.response.status_code} - "
                        f"{http_err.response.text}")
        print(f"ClientService: {error_detail}")
        return False, {'detail': error_detail}
    except requests.exceptions.RequestException as req_err:
        error_detail = f"Erro de conexão ao buscar clientes: {req_err}"
        print(f"ClientService: {error_detail}")
        return False, {'detail': error_detail}

def get_client_by_id(client_id):
    """Busca os detalhes de um cliente específico pela API."""
    token = current_app_state.get_access_token()
    if not token:
        return False, {'detail': "Token de acesso não encontrado. Faça login."}

    headers = {'Authorization': f'Bearer {token}'}
    url = f"{API_BASE_URL}/clientes/{client_id}/"
    print(f"ClientService: Buscando cliente ID {client_id} em {url}")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        client_details = response.json()
        print(f"ClientService: Detalhes do cliente ID {client_id} recebidos.")
        return True, client_details
    except requests.exceptions.HTTPError as http_err:
        error_detail = (f"Erro HTTP ao buscar cliente ID {client_id}: {http_err.response.status_code} - "
                        f"{http_err.response.text}")
        print(f"ClientService: {error_detail}")
        return False, {'detail': error_detail}
    except requests.exceptions.RequestException as req_err:
        error_detail = f"Erro de conexão ao buscar cliente ID {client_id}: {req_err}"
        print(f"ClientService: {error_detail}")
        return False, {'detail': error_detail}

def create_client(client_data):
    """Cria um novo cliente na API."""
    token = current_app_state.get_access_token()
    if not token:
        return False, {'detail': "Token de acesso não encontrado. Faça login."}

    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    url = f"{API_BASE_URL}/clientes/"
    print(f"ClientService: Criando cliente em {url} com dados: {client_data}")

    try:
        response = requests.post(url, headers=headers, json=client_data, timeout=10)
        response.raise_for_status()
        created_client = response.json()
        print(f"ClientService: Cliente '{created_client.get('nome')}' criado com sucesso.")
        return True, created_client
    except requests.exceptions.HTTPError as http_err:
        try:
            error_body = http_err.response.json()
            if isinstance(error_body, dict):
                error_messages = [f"{field}: {', '.join(msgs) if isinstance(msgs, list) else msgs}" for field, msgs in error_body.items()]
                error_detail = f"Erro HTTP ao criar cliente ({http_err.response.status_code}): {'; '.join(error_messages)}"
            else:
                error_detail = f"Erro HTTP ao criar cliente ({http_err.response.status_code}): {http_err.response.text}"
        except ValueError:
            error_detail = f"Erro HTTP ao criar cliente ({http_err.response.status_code}): {http_err.response.text}"
        print(f"ClientService: {error_detail}")
        return False, {'detail': error_detail}
    except requests.exceptions.RequestException as req_err:
        error_detail = f"Erro de conexão ao criar cliente: {req_err}"
        print(f"ClientService: {error_detail}")
        return False, {'detail': error_detail}

def update_client(client_id, client_data):
    """Atualiza um cliente existente na API."""
    token = current_app_state.get_access_token()
    if not token:
        return False, {'detail': "Token de acesso não encontrado. Faça login."}

    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    url = f"{API_BASE_URL}/clientes/{client_id}/"
    print(f"ClientService: Atualizando cliente ID {client_id} em {url} com dados: {client_data}")

    try:
        response = requests.put(url, headers=headers, json=client_data, timeout=10)
        response.raise_for_status()
        updated_client = response.json()
        print(f"ClientService: Cliente ID {client_id} '{updated_client.get('nome')}' atualizado com sucesso.")
        return True, updated_client
    except requests.exceptions.HTTPError as http_err:
        try:
            error_body = http_err.response.json()
            if isinstance(error_body, dict):
                error_messages = [f"{field}: {', '.join(msgs) if isinstance(msgs, list) else msgs}" for field, msgs in error_body.items()]
                error_detail = f"Erro HTTP ao atualizar cliente ID {client_id} ({http_err.response.status_code}): {'; '.join(error_messages)}"
            else:
                error_detail = f"Erro HTTP ao atualizar cliente ID {client_id} ({http_err.response.status_code}): {http_err.response.text}"
        except ValueError:
            error_detail = f"Erro HTTP ao atualizar cliente ID {client_id} ({http_err.response.status_code}): {http_err.response.text}"
        print(f"ClientService: {error_detail}")
        return False, {'detail': error_detail}
    except requests.exceptions.RequestException as req_err:
        error_detail = f"Erro de conexão ao atualizar cliente ID {client_id}: {req_err}"
        print(f"ClientService: {error_detail}")
        return False, {'detail': error_detail}

def delete_client(client_id):
    """Exclui um cliente existente na API."""
    token = current_app_state.get_access_token()
    if not token:
        return False, {'detail': "Token de acesso não encontrado. Faça login."}

    headers = {'Authorization': f'Bearer {token}'}
    url = f"{API_BASE_URL}/clientes/{client_id}/"
    print(f"ClientService: Excluindo cliente ID {client_id} em {url}")

    try:
        response = requests.delete(url, headers=headers, timeout=10)
        response.raise_for_status()
        if response.status_code == 204:
            print(f"ClientService: Cliente ID {client_id} excluído com sucesso (204 No Content).")
            return True, {'detail': 'Cliente excluído com sucesso.'}
        else:
            deleted_info = response.json() if response.content else {'detail': f'Exclusão bem-sucedida com status {response.status_code}'}
            print(f"ClientService: Cliente ID {client_id} excluído. Resposta: {deleted_info}")
            return True, deleted_info
    except requests.exceptions.HTTPError as http_err:
        try:
            error_body = http_err.response.json()
            error_detail = error_body.get('detail', http_err.response.text)
        except ValueError:
            error_detail = http_err.response.text
        full_error_detail = f"Erro HTTP ao excluir cliente ID {client_id} ({http_err.response.status_code}): {error_detail}"
        print(f"ClientService: {full_error_detail}")
        return False, {'detail': full_error_detail}
    except requests.exceptions.RequestException as req_err:
        error_detail = f"Erro de conexão ao excluir cliente ID {client_id}: {req_err}"
        print(f"ClientService: {error_detail}")
        return False, {'detail': error_detail}

def search_clients(search_term):
    """Busca clientes na API usando um termo de pesquisa (nome, CPF, etc.)."""
    token = current_app_state.get_access_token()
    if not token:
        return False, {'detail': "Token de acesso não encontrado. Faça login."}

    headers = {'Authorization': f'Bearer {token}'}
    # Adiciona o parâmetro 'search' à URL, codificando o search_term
    url = f"{API_BASE_URL}/clientes/?search={requests.utils.quote(search_term)}"
    print(f"ClientService: Buscando clientes com termo '{search_term}' em {url}")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        clients = response.json()
        print(f"ClientService: Busca por '{search_term}' retornou {len(clients)} clientes.")
        return True, clients
    except requests.exceptions.HTTPError as http_err:
        error_detail = (
            f"Erro HTTP ao buscar clientes por termo '{search_term}': {http_err.response.status_code} - "
            f"{http_err.response.text}"
        )
        print(f"ClientService: {error_detail}")
        return False, {'detail': error_detail}
    except requests.exceptions.RequestException as req_err:
        error_detail = f"Erro de conexão ao buscar clientes por termo '{search_term}': {req_err}"
        print(f"ClientService: {error_detail}")
        return False, {'detail': error_detail}