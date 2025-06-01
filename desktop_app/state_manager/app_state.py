# desktop_app/state_manager/app_state.py
# ... (outras partes da classe AppState) ...
class AppState:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AppState, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.access_token = None
            self.refresh_token = None
            self.username_logged_in = None
            self.user_id_logged_in = None
            self.user_groups = []
            self.is_superuser_logged_in = False # Adicionado
            self._initialized = True

    def set_auth_tokens(self, access_token, refresh_token):
        self.access_token = access_token
        self.refresh_token = refresh_token

    # Modificado para incluir is_superuser
    def set_user_info(self, username, user_id=None, groups=None, is_superuser=False):
        self.username_logged_in = username
        self.user_id_logged_in = user_id
        self.user_groups = groups if groups is not None else []
        self.is_superuser_logged_in = is_superuser
        print(f"AppState ATUALIZADO: User: {self.username_logged_in}, ID: {self.user_id_logged_in}, Groups: {self.user_groups}, IsSuperuser: {self.is_superuser_logged_in}")


    def get_access_token(self):
        return self.access_token

    def get_refresh_token(self):
        return self.refresh_token

    def get_username(self):
        return self.username_logged_in

    def get_user_id(self):
        return self.user_id_logged_in
    
    def get_user_groups(self):
        return self.user_groups

    def is_current_user_superuser(self): # Novo método
        return self.is_superuser_logged_in

    def is_user_in_group(self, group_name):
        # Verifica se o nome do grupo está na lista E/OU se o usuário é superuser (superusers têm acesso a tudo)
        # Se quiser que superuser precise estar explicitamente no grupo, remova a parte do is_current_user_superuser() daqui
        # e trate o superuser separadamente nos menus.
        # Para simplificar, vamos assumir que um superuser tem acesso implícito onde um supervisor teria.
        if self.is_current_user_superuser():
            return True # Superusuário tem acesso a tudo que um supervisor teria
        return group_name in self.user_groups


    def clear_auth_state(self):
        self.access_token = None
        self.refresh_token = None
        self.username_logged_in = None
        self.user_id_logged_in = None
        self.user_groups = []
        self.is_superuser_logged_in = False
        print("AppState: Estado de autenticação limpo (logout).")

    def is_authenticated(self):
        return bool(self.access_token and self.username_logged_in)

current_app_state = AppState()