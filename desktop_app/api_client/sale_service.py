# desktop_app/api_client/sale_service.py

import requests
from config import API_BASE_URL
from state_manager.app_state import current_app_state

def create_sale(sale_data):
    # ... (código da função create_sale que já temos) ...
    token = current_app_state.get_access_token()
    if not token:
        return False, {'detail': "Token de acesso não encontrado. Faça login."}
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    url = f"{API_BASE_URL}/vendas/"
    print(f"SaleService: Criando venda em {url} com dados: {sale_data}")
    try:
        response = requests.post(url, headers=headers, json=sale_data, timeout=15)
        response.raise_for_status()
        created_sale = response.json()
        print(f"SaleService: Venda ID {created_sale.get('id')} criada com sucesso.")
        return True, created_sale
    except requests.exceptions.HTTPError as http_err:
        # ... (tratamento de erro existente) ...
        try:
            error_body = http_err.response.json()
            if isinstance(error_body, dict):
                error_messages = []
                if 'detail' in error_body: error_messages.append(str(error_body['detail']))
                else:
                    for field, messages in error_body.items():
                        if isinstance(messages, list):
                            field_errors = [str(m) for m in messages if isinstance(m, (str, dict))]
                            if field == 'itens' and field_errors and isinstance(messages[0], dict):
                                 for i, item_error_dict in enumerate(messages):
                                     for item_field, item_msgs in item_error_dict.items():
                                         if item_msgs: error_messages.append(f"Item {i+1} - {item_field}: {', '.join(item_msgs)}")
                            else: error_messages.append(f"{field}: {', '.join(field_errors)}")
                        else: error_messages.append(f"{field}: {str(messages)}")
                error_detail = f"Erro HTTP ao criar venda ({http_err.response.status_code}): {'; '.join(error_messages) if error_messages else http_err.response.text}"
            else: error_detail = f"Erro HTTP ao criar venda ({http_err.response.status_code}): {http_err.response.text}"
        except ValueError: error_detail = f"Erro HTTP ao criar venda ({http_err.response.status_code}): {http_err.response.text}"
        print(f"SaleService: {error_detail}")
        return False, {'detail': error_detail}
    except requests.exceptions.RequestException as req_err:
        error_detail = f"Erro de conexão ao criar venda: {req_err}"
        print(f"SaleService: {error_detail}")
        return False, {'detail': error_detail}


# NOVA FUNÇÃO ADICIONADA ABAIXO:
def get_sales(filters=None):
    """
    Busca todas as vendas da API, opcionalmente aplicando filtros.
    filters: Um dicionário de parâmetros de filtro (ex: {'data_inicio': 'YYYY-MM-DD'})
    """
    token = current_app_state.get_access_token()
    if not token:
        return False, {'detail': "Token de acesso não encontrado. Faça login."}

    headers = {'Authorization': f'Bearer {token}'}
    url = f"{API_BASE_URL}/vendas/"

    params = {}
    if filters:
        for key, value in filters.items():
            if value: # Adiciona ao params apenas se o filtro tiver um valor
                params[key] = value

    print(f"SaleService: Buscando vendas em {url} com filtros: {params}") # Debug

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10) # Adicionado params
        response.raise_for_status()
        sales = response.json() # A API retorna uma lista de vendas ou um objeto com 'results' se paginado

        # Se a API retornar um objeto com 'results' (paginação do DRF)
        if isinstance(sales, dict) and 'results' in sales:
            sales_list = sales['results']
            print(f"SaleService: {len(sales_list)} vendas recebidas (de {sales.get('count', '?')} no total).") # Debug
            return True, sales_list # Retorna apenas a lista de resultados por enquanto
        elif isinstance(sales, list):
            print(f"SaleService: {len(sales)} vendas recebidas.") # Debug
            return True, sales
        else:
            print(f"SaleService: Resposta inesperada da API ao listar vendas: {sales}")
            return False, {'detail': 'Formato de resposta inesperado da API.'}

    except requests.exceptions.HTTPError as http_err:
        error_detail = (
            f"Erro HTTP ao buscar vendas: {http_err.response.status_code} - "
            f"{http_err.response.text}"
        )
        print(f"SaleService: {error_detail}") # Debug
        return False, {'detail': error_detail}
    except requests.exceptions.RequestException as req_err:
        error_detail = f"Erro de conexão ao buscar vendas: {req_err}"
        print(f"SaleService: {error_detail}") # Debug
        return False, {'detail': error_detail}

def get_sale_details(sale_id):
    """
    Busca os detalhes completos de uma venda específica, incluindo seus itens.
    """
    token = current_app_state.get_access_token()
    if not token:
        return False, {'detail': "Token de acesso não encontrado. Faça login."}

    headers = {'Authorization': f'Bearer {token}'}
    url = f"{API_BASE_URL}/vendas/{sale_id}/" # Endpoint para detalhes de uma venda
    print(f"SaleService: Buscando detalhes da venda ID {sale_id} em {url}")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        sale_details = response.json()
        # O VendaSerializer já deve estar configurado para retornar os itens aninhados
        print(f"SaleService: Detalhes da venda ID {sale_id} recebidos.")
        return True, sale_details
    except requests.exceptions.HTTPError as http_err:
        error_detail = (
            f"Erro HTTP ao buscar detalhes da venda ID {sale_id}: {http_err.response.status_code} - "
            f"{http_err.response.text}"
        )
        print(f"SaleService: {error_detail}")
        return False, {'detail': error_detail}
    except requests.exceptions.RequestException as req_err:
        error_detail = f"Erro de conexão ao buscar detalhes da venda ID {sale_id}: {req_err}"
        print(f"SaleService: {error_detail}")
        return False, {'detail': error_detail}