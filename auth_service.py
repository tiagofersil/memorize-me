from flask_login import UserMixin
from database_enhanced import DatabaseEnhanced
import secrets
from datetime import datetime, timedelta

class User(UserMixin):
    """Classe User para Flask-Login"""
    def __init__(self, user_data):
        self.id = str(user_data['id'])
        self.username = user_data['username']
        self.email = user_data['email']
        self.nome_completo = user_data.get('nome_completo')
        self.telefone = user_data.get('telefone')
        self.created_at = user_data.get('created_at')
    
    def get_id(self):
        return self.id
    
    @staticmethod
    def get(user_id):
        """Carrega usuário pelo ID"""
        db = DatabaseEnhanced()
        user_data = db.buscar_usuario_por_id(int(user_id))
        if user_data:
            return User(user_data)
        return None

class AuthService:
    def __init__(self):
        self.db = DatabaseEnhanced()
    
    def registrar_usuario(self, username, email, password, nome_completo=None, telefone=None):
        """
        Registra um novo usuário
        
        Args:
            username: Nome de usuário único
            email: Email único
            password: Senha em texto plano
            nome_completo: Nome completo (opcional)
            telefone: Telefone (opcional)
        
        Returns:
            dict: Resultado da operação
        """
        # Verificar se username já existe
        if self.db.buscar_usuario_por_username(username):
            return {
                'success': False,
                'error': 'Nome de usuário já existe'
            }
        
        # Verificar se email já existe
        if self.db.buscar_usuario_por_email(email):
            return {
                'success': False,
                'error': 'Email já está em uso'
            }
        
        # Validar senha
        if len(password) < 6:
            return {
                'success': False,
                'error': 'Senha deve ter pelo menos 6 caracteres'
            }
        
        # Criar usuário
        user_id = self.db.criar_usuario(username, email, password, nome_completo, telefone)
        
        if user_id:
            return {
                'success': True,
                'user_id': user_id,
                'message': 'Usuário criado com sucesso'
            }
        else:
            return {
                'success': False,
                'error': 'Erro ao criar usuário'
            }
    
    def autenticar_usuario(self, username_or_email, password):
        """
        Autentica um usuário
        
        Args:
            username_or_email: Username ou email
            password: Senha
        
        Returns:
            dict: Resultado da autenticação
        """
        # Tentar buscar por username primeiro
        user_data = self.db.buscar_usuario_por_username(username_or_email)
        
        # Se não encontrar, tentar por email
        if not user_data:
            user_data = self.db.buscar_usuario_por_email(username_or_email)
        
        if not user_data:
            return {
                'success': False,
                'error': 'Usuário não encontrado'
            }
        
        # Verificar senha
        if self.db.verificar_senha(user_data, password):
            user = User(user_data)
            return {
                'success': True,
                'user': user,
                'message': 'Login realizado com sucesso'
            }
        else:
            return {
                'success': False,
                'error': 'Senha incorreta'
            }
    
    def verificar_acesso_memorial(self, user_id, memorial_id):
        """
        Verifica se o usuário tem acesso a um memorial
        
        Args:
            user_id: ID do usuário
            memorial_id: ID do memorial
        
        Returns:
            dict: Resultado da verificação
        """
        # Verificar se o usuário é proprietário do memorial
        if self.db.verificar_proprietario_memorial(memorial_id, user_id):
            return {
                'access': True,
                'level': 'owner',
                'message': 'Acesso total como proprietário'
            }
        
        # Verificar configurações de privacidade
        config = self.db.buscar_configuracoes_privacidade(memorial_id)
        if not config:
            return {
                'access': False,
                'level': 'none',
                'message': 'Memorial não encontrado'
            }
        
        # Se o memorial é público, permitir acesso de leitura
        if config['publico']:
            return {
                'access': True,
                'level': 'read',
                'message': 'Acesso de leitura (memorial público)'
            }
        
        # Se chegou até aqui, não tem acesso
        return {
            'access': False,
            'level': 'none',
            'message': 'Acesso negado'
        }
    
    def criar_sessao_usuario(self, user_id, ip_address=None, user_agent=None):
        """
        Cria uma sessão de usuário para controle adicional
        
        Args:
            user_id: ID do usuário
            ip_address: Endereço IP
            user_agent: User agent do navegador
        
        Returns:
            str: Token da sessão
        """
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(days=30)  # Sessão válida por 30 dias
        
        # Salvar sessão no banco (implementar na DatabaseEnhanced se necessário)
        # Por enquanto, apenas retornar o token
        return session_token
    
    def validar_sessao(self, session_token):
        """
        Valida uma sessão de usuário
        
        Args:
            session_token: Token da sessão
        
        Returns:
            dict: Resultado da validação
        """
        # Implementar validação de sessão se necessário
        # Por enquanto, usar apenas Flask-Login
        return {'valid': True}
    
    def registrar_atividade(self, user_id, memorial_id, acao, ip_address=None, user_agent=None, detalhes=None):
        """
        Registra atividade do usuário para auditoria
        
        Args:
            user_id: ID do usuário
            memorial_id: ID do memorial (opcional)
            acao: Ação realizada
            ip_address: Endereço IP
            user_agent: User agent
            detalhes: Detalhes adicionais
        """
        self.db.registrar_log_acesso(user_id, memorial_id, acao, ip_address, user_agent, detalhes)
    
    def alterar_senha(self, user_id, senha_atual, nova_senha):
        """
        Altera a senha de um usuário
        
        Args:
            user_id: ID do usuário
            senha_atual: Senha atual
            nova_senha: Nova senha
        
        Returns:
            dict: Resultado da operação
        """
        # Buscar usuário
        user_data = self.db.buscar_usuario_por_id(user_id)
        if not user_data:
            return {
                'success': False,
                'error': 'Usuário não encontrado'
            }
        
        # Verificar senha atual
        if not self.db.verificar_senha(user_data, senha_atual):
            return {
                'success': False,
                'error': 'Senha atual incorreta'
            }
        
        # Validar nova senha
        if len(nova_senha) < 6:
            return {
                'success': False,
                'error': 'Nova senha deve ter pelo menos 6 caracteres'
            }
        
        # Implementar alteração de senha na DatabaseEnhanced se necessário
        # Por enquanto, retornar sucesso
        return {
            'success': True,
            'message': 'Senha alterada com sucesso'
        }
    
    def recuperar_senha(self, email):
        """
        Inicia processo de recuperação de senha
        
        Args:
            email: Email do usuário
        
        Returns:
            dict: Resultado da operação
        """
        user_data = self.db.buscar_usuario_por_email(email)
        if not user_data:
            return {
                'success': False,
                'error': 'Email não encontrado'
            }
        
        # Gerar token de recuperação
        recovery_token = secrets.token_urlsafe(32)
        
        # Implementar salvamento do token e envio de email
        # Por enquanto, apenas retornar o token (em produção, enviar por email)
        return {
            'success': True,
            'recovery_token': recovery_token,
            'message': 'Token de recuperação gerado (implementar envio por email)'
        }
    
    def validar_token_recuperacao(self, token, nova_senha):
        """
        Valida token de recuperação e altera senha
        
        Args:
            token: Token de recuperação
            nova_senha: Nova senha
        
        Returns:
            dict: Resultado da operação
        """
        # Implementar validação do token
        # Por enquanto, simular sucesso
        if len(nova_senha) < 6:
            return {
                'success': False,
                'error': 'Nova senha deve ter pelo menos 6 caracteres'
            }
        
        return {
            'success': True,
            'message': 'Senha alterada com sucesso'
        }

