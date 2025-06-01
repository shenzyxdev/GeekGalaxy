# desktop_app/api_client/product_service.py

import requests
from config import API_BASE_URL
from state_manager.app_state import current_app_state

# ... (funções get_products, create_product, get_product_by_id, update_product que já temos) ...
def get_products():
    token = current_app_state.get_access_token()
    if not token:
        return False, {'detail': "Token de acesso não encontrado. Faça login."}
    headers = {'Authorization': f'Bearer {token}'}
    url = f"{API_BASE_URL}/produtos/"
    print(f"ProductService: Buscando produtos em {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        products = response.json()
        print(f"ProductService: {len(products)} produtos recebidos.")
        return True, products
    except requests.exceptions.HTTPError as http_err:
        error_detail = (f"Erro HTTP ao buscar produtos: {http_err.response.status_code} - "
                        f"{http_err.response.text}")
        print(f"ProductService: {error_detail}")
        return False, {'detail': error_detail}
    except requests.exceptions.RequestException as req_err:
        error_detail = f"Erro de conexão ao buscar produtos: {req_err}"
        print(f"ProductService: {error_detail}")
        return False, {'detail': error_detail}

def create_product(product_data):
    token = current_app_state.get_access_token()
    if not token:
        return False, {'detail': "Token de acesso não encontrado. Faça login."}
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    url = f"{API_BASE_URL}/produtos/"
    print(f"ProductService: Criando produto em {url} com dados: {product_data}")
    try:
        response = requests.post(url, headers=headers, json=product_data, timeout=10)
        response.raise_for_status()
        created_product = response.json()
        print(f"ProductService: Produto '{created_product.get('nomeProduto')}' criado com sucesso.")
        return True, created_product
    except requests.exceptions.HTTPError as http_err:
        try:
            error_body = http_err.response.json()
            if isinstance(error_body, dict):
                error_messages = [f"{field}: {', '.join(msgs) if isinstance(msgs, list) else msgs}" for field, msgs in error_body.items()]
                error_detail = f"Erro HTTP ao criar produto ({http_err.response.status_code}): {'; '.join(error_messages)}"
            else:
                error_detail = f"Erro HTTP ao criar produto ({http_err.response.status_code}): {http_err.response.text}"
        except ValueError:
            error_detail = f"Erro HTTP ao criar produto ({http_err.response.status_code}): {http_err.response.text}"
        print(f"ProductService: {error_detail}")
        return False, {'detail': error_detail}
    except requests.exceptions.RequestException as req_err:
        error_detail = f"Erro de conexão ao criar produto: {req_err}"
        print(f"ProductService: {error_detail}")
        return False, {'detail': error_detail}

def get_product_by_id(product_id):
    token = current_app_state.get_access_token()
    if not token:
        return False, {'detail': "Token de acesso não encontrado. Faça login."}
    headers = {'Authorization': f'Bearer {token}'}
    url = f"{API_BASE_URL}/produtos/{product_id}/"
    print(f"ProductService: Buscando produto ID {product_id} em {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        product_details = response.json()
        print(f"ProductService: Detalhes do produto ID {product_id} recebidos.")
        return True, product_details
    except requests.exceptions.HTTPError as http_err:
        error_detail = (
            f"Erro HTTP ao buscar produto ID {product_id}: {http_err.response.status_code} - "
            f"{http_err.response.text}"
        )
        print(f"ProductService: {error_detail}")
        return False, {'detail': error_detail}
    except requests.exceptions.RequestException as req_err:
        error_detail = f"Erro de conexão ao buscar produto ID {product_id}: {req_err}"
        print(f"ProductService: {error_detail}")
        return False, {'detail': error_detail}

def update_product(product_id, product_data):
    token = current_app_state.get_access_token()
    if not token:
        return False, {'detail': "Token de acesso não encontrado. Faça login."}
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    url = f"{API_BASE_URL}/produtos/{product_id}/"
    print(f"ProductService: Atualizando produto ID {product_id} em {url} com dados: {product_data}")
    try:
        response = requests.put(url, headers=headers, json=product_data, timeout=10)
        response.raise_for_status()
        updated_product = response.json()
        print(f"ProductService: Produto ID {product_id} '{updated_product.get('nomeProduto')}' atualizado com sucesso.")
        return True, updated_product
    except requests.exceptions.HTTPError as http_err:
        try:
            error_body = http_err.response.json()
            if isinstance(error_body, dict):
                error_messages = [f"{field}: {', '.join(msgs) if isinstance(msgs, list) else msgs}" for field, msgs in error_body.items()]
                error_detail = f"Erro HTTP ao atualizar produto ID {product_id} ({http_err.response.status_code}): {'; '.join(error_messages)}"
            else:
                error_detail = f"Erro HTTP ao atualizar produto ID {product_id} ({http_err.response.status_code}): {http_err.response.text}"
        except ValueError:
            error_detail = f"Erro HTTP ao atualizar produto ID {product_id} ({http_err.response.status_code}): {http_err.response.text}"
        print(f"ProductService: {error_detail}")
        return False, {'detail': error_detail}
    except requests.exceptions.RequestException as req_err:
        error_detail = f"Erro de conexão ao atualizar produto ID {product_id}: {req_err}"
        print(f"ProductService: {error_detail}")
        return False, {'detail': error_detail}

# NOVA FUNÇÃO OU ATUALIZAÇÃO DO PLACEHOLDER:
def delete_product(product_id):
    """
    Exclui um produto existente na API.
    product_id: ID do produto a ser excluído.
    """
    token = current_app_state.get_access_token()
    if not token:
        return False, {'detail': "Token de acesso não encontrado. Faça login."}

    headers = {
        'Authorization': f'Bearer {token}'
        # 'Content-Type' não é usualmente necessário para DELETE, a menos que a API espere um corpo.
    }
    url = f"{API_BASE_URL}/produtos/{product_id}/" # Endpoint para excluir um produto específico
    print(f"ProductService: Excluindo produto ID {product_id} em {url}") # Debug

    try:
        response = requests.delete(url, headers=headers, timeout=10)
        response.raise_for_status() # Lança erro para status 4xx/5xx.
                                    # Para DELETE, um status 204 No Content é sucesso e não tem corpo.

        # Se o status for 204 (No Content), a exclusão foi bem-sucedida e não há corpo JSON.
        if response.status_code == 204:
            print(f"ProductService: Produto ID {product_id} excluído com sucesso (204 No Content).") # Debug
            return True, {'detail': 'Produto excluído com sucesso.'} # Retorna um dict para consistência
        else:
            # Se a API retornar um corpo JSON mesmo para DELETE com status 2xx (incomum para 204)
            deleted_product_info = response.json()
            print(f"ProductService: Produto ID {product_id} excluído. Resposta: {deleted_product_info}") # Debug
            return True, deleted_product_info

    except requests.exceptions.HTTPError as http_err:
        # Tenta pegar uma mensagem de erro mais específica do corpo da resposta JSON
        try:
            error_body = http_err.response.json()
            error_detail = error_body.get('detail', http_err.response.text)
        except ValueError: # Se o corpo do erro não for JSON
            error_detail = http_err.response.text

        full_error_detail = f"Erro HTTP ao excluir produto ID {product_id} ({http_err.response.status_code}): {error_detail}"
        print(f"ProductService: {full_error_detail}") # Debug
        return False, {'detail': full_error_detail}
    except requests.exceptions.RequestException as req_err:
        error_detail = f"Erro de conexão ao excluir produto ID {product_id}: {req_err}"
        print(f"ProductService: {error_detail}") # Debug
        return False, {'detail': error_detail}
    
def search_products_for_sale(search_term):
    """Busca produtos na API usando um termo de pesquisa (nome, código, etc.)."""
    token = current_app_state.get_access_token()
    if not token:
        return False, {'detail': "Token de acesso não encontrado. Faça login."}

    headers = {'Authorization': f'Bearer {token}'}
    # Adiciona o parâmetro 'search' à URL
    url = f"{API_BASE_URL}/produtos/?search={requests.utils.quote(search_term)}"
    print(f"ProductService: Buscando produtos para venda em {url}") # Debug

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        products = response.json() # API retorna uma lista de produtos correspondentes
        print(f"ProductService: Busca por '{search_term}' retornou {len(products)} produtos.") # Debug
        return True, products
    except requests.exceptions.HTTPError as http_err:
        error_detail = (
            f"Erro HTTP ao buscar produtos por termo '{search_term}': {http_err.response.status_code} - "
            f"{http_err.response.text}"
        )
        print(f"ProductService: {error_detail}") # Debug
        return False, {'detail': error_detail}
    except requests.exceptions.RequestException as req_err:
        error_detail = f"Erro de conexão ao buscar produtos por termo '{search_term}': {req_err}"
        print(f"ProductService: {error_detail}") # Debug
        return False, {'detail': error_detail}