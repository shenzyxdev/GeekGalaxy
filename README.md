# 🎮 GeekGalaxy Store - Sistema de Gerenciamento de Vendas 🛍️

![GeekGalaxy Store Banner](https://i.imgur.com/YOUR_BANNER_IMAGE_URL.png) Bem-vindo ao repositório do **GeekGalaxy Store**, um sistema de gerenciamento de vendas completo, projetado como parte do Projeto Integrado Multidisciplinar (PIM VI) para o curso Superior de Tecnologia em Análise e Desenvolvimento de Sistemas da UNIP! 🚀

Este projeto demonstra a aplicação prática de conceitos de engenharia de software, desde o levantamento de requisitos até a implementação de uma solução funcional com back-end robusto e um front-end desktop interativo.

## ✨ Visão Geral do Projeto

O GeekGalaxy Store é um sistema desktop desenvolvido para auxiliar no gerenciamento de uma loja fictícia especializada em jogos eletrônicos, acessórios e produtos do universo geek. Ele visa substituir controles manuais (como planilhas Excel) por uma solução moderna, eficiente e segura.

**Principais Funcionalidades Implementadas:**
* 🔑 Autenticação de Usuários com diferentes níveis de permissão.
* 📦 Gerenciamento de Produtos (CRUD completo).
* 🧑‍🤝‍🧑 Gerenciamento de Clientes (CRUD completo).
* 🛒 Ponto de Venda (PDV) para registro de transações.
    * Busca e adição de produtos à venda.
    * Seleção de cliente para a venda.
    * Cálculo de totais.
    * Finalização da venda e atualização de estoque.
    * Emissão de Recibo/Comprovante (simulado).
* 📊 Relatório de Vendas detalhado com filtros.
* 👤 Gerenciamento de Usuários do sistema (Adicionar/Editar com atribuição de grupos) pela interface desktop.

## 🛠️ Tecnologias Utilizadas

Este projeto foi construído utilizando um stack de tecnologias moderno e robusto:

* **Back-end (API):**
    * 🐍 **Python 3.x**
    * 🕸️ **Django**: Framework web de alto nível para desenvolvimento rápido e seguro.
    * 🔗 **Django REST Framework**: Para a construção da API RESTful.
    * 🔑 **djangorestframework-simplejwt**: Para autenticação baseada em JSON Web Tokens (JWT).
    * 🔍 **django-filter**: Para filtragem avançada nos endpoints da API.
    * 🗄️ **MySQL**: Como sistema de gerenciamento de banco de dados relacional.
* **Front-end (Aplicação Desktop):**
    * 🐍 **Python 3.x**
    * 🖼️ **PyQt5**: Para a construção da interface gráfica do usuário (GUI).
    * 🌐 **Requests**: Para comunicação HTTP com a API Django.
* **Controle de Versão:**
    * 🐙 **Git & GitHub**
* **Ambiente de Desenvolvimento:**
    * izolált **Ambientes Virtuais Python (venv)**
* **Empacotamento (Futuro):**
    * 📦 **PyInstaller**: Para criar o executável `.exe` da aplicação desktop.

## 🚀 Como Executar o Projeto

### Pré-requisitos

* Python 3.8 ou superior.
* Git.
* MySQL Server instalado e rodando.
* Um editor de código (ex: VS Code).
* Postman (opcional, para testar a API diretamente).

### Configuração do Back-end (API Django)

1.  **Clone o repositório (se ainda não o fez):**
    ```bash
    git clone [https://github.com/SEUNOMEUSUARIOGIT/NOMEDOREPOSITORIO.git](https://github.com/SEUNOMEUSUARIOGIT/NOMEDOREPOSITORIO.git)
    cd NOMEDOREPOSITORIO
    ```
2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv_geekgalaxy
    # Windows (PowerShell)
    .\venv_geekgalaxy\Scripts\Activate.ps1
    # Linux/macOS
    # source venv_geekgalaxy/bin/activate
    ```
3.  **Instale as dependências do back-end:**
    ```bash
    pip install -r requirements_backend.txt 
    ```
    *(Você precisará criar um arquivo `requirements_backend.txt` na raiz do projeto com o output de `pip freeze` do seu ambiente de desenvolvimento Django. Ex: `django`, `djangorestframework`, `mysqlclient`, `django-cors-headers`, `djangorestframework-simplejwt`, `django-filter`)*

4.  **Configure o Banco de Dados:**
    * Crie um banco de dados MySQL chamado `geekgalaxy_db` (ou o nome que preferir).
    * Copie `geekgalaxy_project/settings_example.py` para `geekgalaxy_project/settings.py` (ou edite `settings.py` diretamente).
    * Ajuste as configurações `DATABASES` no `settings.py` com suas credenciais do MySQL.
    * Certifique-se de que `AUTH_USER_MODEL = 'vendas_api.Usuario'` está definido.
5.  **Aplique as migrações:**
    ```bash
    python manage.py makemigrations vendas_api
    python manage.py migrate
    ```
6.  **Crie um superusuário (para acesso ao admin do Django):**
    ```bash
    python manage.py createsuperuser
    ```
7.  **Cadastre os Grupos de Permissão no Admin do Django:**
    * Acesse `http://127.0.0.1:8000/admin/`.
    * Crie os grupos: `ATENDENTE`, `ESTOQUISTA`, `SUPERVISOR` (em maiúsculas).
8.  **Inicie o servidor Django:**
    ```bash
    python manage.py runserver
    ```
    A API estará rodando em `http://127.0.0.1:8000/api/`.

### Configuração e Execução do Front-end (Aplicação Desktop PyQt)

1.  **Instale as dependências do front-end (no mesmo ambiente virtual ou em um separado, se preferir):**
    ```bash
    pip install -r requirements_frontend.txt
    ```
    *(Você precisará criar um arquivo `requirements_frontend.txt` na raiz da pasta `desktop_app` com `PyQt5` e `requests`)*
    Ou instale manualmente:
    ```bash
    pip install PyQt5 requests
    ```
2.  **Verifique a URL da API:**
    * Certifique-se de que o arquivo `desktop_app/config.py` tem a `API_BASE_URL` correta (normalmente `http://127.0.0.1:8000/api` se o servidor Django estiver rodando localmente).
3.  **Execute a aplicação desktop:**
    * Navegue até a pasta `desktop_app`:
        ```bash
        cd desktop_app
        ```
    * Execute o `main.py`:
        ```bash
        python main.py
        ```


