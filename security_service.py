from flask import request, session, current_app
from functools import wraps
from database_enhanced import DatabaseEnhanced
from auth_service import AuthService
import hashlib
import secrets
import time
from datetime import datetime, timedelta
import re

class SecurityService:
    def __init__(self):
        self.db = DatabaseEnhanced()
        self.auth_service = AuthService()
        
        # Configurações de segurança
        self.max_login_attempts = 5
        self.lockout_duration = 300  # 5 minutos em segundos
        self.session_timeout = 3600  # 1 hora em segundos
        self.password_min_length = 6
        
        # Rate limiting
        self.rate_limits = {
            'login': {'max_attempts': 5, 'window': 300},  # 5 tentativas em 5 minutos
            'register': {'max_attempts': 3, 'window': 600},  # 3 tentativas em 10 minutos
            'upload': {'max_attempts': 20, 'window': 3600},  # 20 uploads por hora
            'api': {'max_attempts': 100, 'window': 3600}  # 100 requests API por hora
        }
        
        # Cache para rate limiting (em produção, usar Redis)
        self.rate_limit_cache = {}
    
    def validate_password_strength(self, password):
        """
        Valida a força da senha
        
        Args:
            password: Senha a ser validada
        
        Returns:
            dict: Resultado da validação
        """
        errors = []
        
        if len(password) < self.password_min_length:
            errors.append(f'Senha deve ter pelo menos {self.password_min_length} caracteres')
        
        if not re.search(r'[A-Z]', password):
            errors.append('Senha deve conter pelo menos uma letra maiúscula')
        
        if not re.search(r'[a-z]', password):
            errors.append('Senha deve conter pelo menos uma letra minúscula')
        
        if not re.search(r'\d', password):
            errors.append('Senha deve conter pelo menos um número')
        
        # Verificar senhas comuns
        common_passwords = [
            '123456', 'password', '123456789', '12345678', '12345',
            '1234567', '1234567890', 'qwerty', 'abc123', 'password123'
        ]
        
        if password.lower() in common_passwords:
            errors.append('Senha muito comum, escolha uma senha mais segura')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'strength': self._calculate_password_strength(password)
        }
    
    def _calculate_password_strength(self, password):
        """Calcula a força da senha (0-100)"""
        score = 0
        
        # Comprimento
        if len(password) >= 8:
            score += 25
        elif len(password) >= 6:
            score += 15
        
        # Caracteres diferentes
        if re.search(r'[a-z]', password):
            score += 15
        if re.search(r'[A-Z]', password):
            score += 15
        if re.search(r'\d', password):
            score += 15
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 20
        
        # Diversidade
        unique_chars = len(set(password))
        if unique_chars >= len(password) * 0.7:
            score += 10
        
        return min(score, 100)
    
    def check_rate_limit(self, identifier, action):
        """
        Verifica rate limiting
        
        Args:
            identifier: Identificador único (IP, user_id, etc.)
            action: Tipo de ação (login, register, upload, api)
        
        Returns:
            dict: Resultado da verificação
        """
        if action not in self.rate_limits:
            return {'allowed': True}
        
        config = self.rate_limits[action]
        current_time = int(time.time())
        window_start = current_time - config['window']
        
        # Chave para o cache
        cache_key = f"{identifier}:{action}"
        
        # Limpar entradas antigas
        if cache_key in self.rate_limit_cache:
            self.rate_limit_cache[cache_key] = [
                timestamp for timestamp in self.rate_limit_cache[cache_key]
                if timestamp > window_start
            ]
        else:
            self.rate_limit_cache[cache_key] = []
        
        # Verificar limite
        attempts = len(self.rate_limit_cache[cache_key])
        
        if attempts >= config['max_attempts']:
            return {
                'allowed': False,
                'error': f'Muitas tentativas. Tente novamente em {config["window"]} segundos.',
                'retry_after': config['window']
            }
        
        # Registrar tentativa
        self.rate_limit_cache[cache_key].append(current_time)
        
        return {
            'allowed': True,
            'remaining': config['max_attempts'] - attempts - 1
        }
    
    def validate_input(self, data, rules):
        """
        Valida dados de entrada
        
        Args:
            data: Dados a serem validados
            rules: Regras de validação
        
        Returns:
            dict: Resultado da validação
        """
        errors = {}
        
        for field, field_rules in rules.items():
            value = data.get(field)
            field_errors = []
            
            # Required
            if field_rules.get('required', False) and not value:
                field_errors.append(f'{field} é obrigatório')
                continue
            
            if value:
                # Max length
                if 'max_length' in field_rules and len(str(value)) > field_rules['max_length']:
                    field_errors.append(f'{field} deve ter no máximo {field_rules["max_length"]} caracteres')
                
                # Min length
                if 'min_length' in field_rules and len(str(value)) < field_rules['min_length']:
                    field_errors.append(f'{field} deve ter pelo menos {field_rules["min_length"]} caracteres')
                
                # Email
                if field_rules.get('email', False) and not re.match(r'^[^@]+@[^@]+\.[^@]+$', value):
                    field_errors.append(f'{field} deve ser um email válido')
                
                # Alphanumeric
                if field_rules.get('alphanumeric', False) and not re.match(r'^[a-zA-Z0-9_]+$', value):
                    field_errors.append(f'{field} deve conter apenas letras, números e underscore')
                
                # Custom pattern
                if 'pattern' in field_rules and not re.match(field_rules['pattern'], value):
                    field_errors.append(field_rules.get('pattern_error', f'{field} tem formato inválido'))
            
            if field_errors:
                errors[field] = field_errors
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def sanitize_input(self, data):
        """
        Sanitiza dados de entrada
        
        Args:
            data: Dados a serem sanitizados
        
        Returns:
            dict: Dados sanitizados
        """
        if isinstance(data, dict):
            return {key: self.sanitize_input(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_input(item) for item in data]
        elif isinstance(data, str):
            # Remove caracteres perigosos
            data = data.strip()
            # Remove tags HTML básicas (implementação simples)
            data = re.sub(r'<[^>]+>', '', data)
            # Remove caracteres de controle
            data = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', data)
            return data
        else:
            return data
    
    def check_memorial_access(self, user_id, memorial_id, required_level='read'):
        """
        Verifica acesso a um memorial
        
        Args:
            user_id: ID do usuário (None para visitante)
            memorial_id: ID do memorial
            required_level: Nível de acesso necessário ('read', 'write', 'owner')
        
        Returns:
            dict: Resultado da verificação
        """
        # Buscar memorial
        memorial = self.db.buscar_memorial_por_id(memorial_id)
        if not memorial:
            return {
                'allowed': False,
                'error': 'Memorial não encontrado'
            }
        
        # Verificar se é proprietário
        is_owner = user_id and memorial['user_id'] == user_id
        
        if required_level == 'owner' and not is_owner:
            return {
                'allowed': False,
                'error': 'Apenas o proprietário pode realizar esta ação'
            }
        
        if required_level == 'write' and not is_owner:
            return {
                'allowed': False,
                'error': 'Apenas o proprietário pode editar este memorial'
            }
        
        # Para leitura, verificar configurações de privacidade
        if required_level == 'read':
            if is_owner:
                return {'allowed': True, 'level': 'owner'}
            
            # Verificar se é público
            config = self.db.buscar_configuracoes_privacidade(memorial_id)
            if config and config['publico']:
                return {'allowed': True, 'level': 'read'}
            
            # Verificar senha de acesso se configurada
            if config and config['senha_acesso']:
                # Implementar verificação de senha de acesso
                return {
                    'allowed': False,
                    'error': 'Memorial protegido por senha',
                    'requires_password': True
                }
            
            return {
                'allowed': False,
                'error': 'Memorial privado'
            }
        
        return {'allowed': True, 'level': 'owner' if is_owner else 'read'}
    
    def log_security_event(self, event_type, user_id=None, memorial_id=None, 
                          ip_address=None, user_agent=None, details=None):
        """
        Registra evento de segurança
        
        Args:
            event_type: Tipo do evento
            user_id: ID do usuário
            memorial_id: ID do memorial
            ip_address: Endereço IP
            user_agent: User agent
            details: Detalhes adicionais
        """
        self.db.registrar_log_acesso(
            user_id=user_id,
            memorial_id=memorial_id,
            acao=f'security:{event_type}',
            ip_address=ip_address,
            user_agent=user_agent,
            detalhes=details
        )
    
    def detect_suspicious_activity(self, user_id, ip_address):
        """
        Detecta atividade suspeita
        
        Args:
            user_id: ID do usuário
            ip_address: Endereço IP
        
        Returns:
            dict: Resultado da análise
        """
        # Implementar detecção de atividade suspeita
        # Por exemplo: múltiplos IPs, tentativas de acesso a muitos memoriais, etc.
        
        suspicious_indicators = []
        
        # Verificar múltiplos IPs em pouco tempo
        # Verificar tentativas de acesso a memoriais não autorizados
        # Verificar padrões de upload suspeitos
        
        return {
            'suspicious': len(suspicious_indicators) > 0,
            'indicators': suspicious_indicators,
            'risk_level': 'low'  # low, medium, high
        }
    
    def generate_csrf_token(self):
        """Gera token CSRF"""
        token = secrets.token_urlsafe(32)
        session['csrf_token'] = token
        return token
    
    def validate_csrf_token(self, token):
        """Valida token CSRF"""
        return session.get('csrf_token') == token
    
    def hash_sensitive_data(self, data):
        """Hash para dados sensíveis"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def encrypt_sensitive_data(self, data, key=None):
        """Criptografia simples para dados sensíveis (implementar com biblioteca adequada)"""
        # Em produção, usar biblioteca como cryptography
        return data  # Placeholder
    
    def decrypt_sensitive_data(self, encrypted_data, key=None):
        """Descriptografia de dados sensíveis"""
        # Em produção, usar biblioteca como cryptography
        return encrypted_data  # Placeholder

# Decoradores de segurança
def require_auth(f):
    """Decorator que requer autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user
        if not current_user.is_authenticated:
            return {'error': 'Autenticação necessária'}, 401
        return f(*args, **kwargs)
    return decorated_function

def require_memorial_access(level='read'):
    """Decorator que requer acesso a memorial"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask_login import current_user
            
            memorial_id = kwargs.get('memorial_id') or request.view_args.get('memorial_id')
            if not memorial_id:
                return {'error': 'Memorial ID necessário'}, 400
            
            security_service = SecurityService()
            user_id = int(current_user.id) if current_user.is_authenticated else None
            
            access_result = security_service.check_memorial_access(user_id, memorial_id, level)
            
            if not access_result['allowed']:
                return {'error': access_result['error']}, 403
            
            # Adicionar informações de acesso ao request
            request.memorial_access = access_result
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def rate_limit(action):
    """Decorator para rate limiting"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            security_service = SecurityService()
            
            # Usar IP como identificador
            identifier = request.remote_addr
            
            rate_result = security_service.check_rate_limit(identifier, action)
            
            if not rate_result['allowed']:
                return {'error': rate_result['error']}, 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_input_decorator(rules):
    """Decorator para validação de entrada"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            security_service = SecurityService()
            
            # Obter dados do request
            if request.is_json:
                data = request.get_json() or {}
            else:
                data = request.form.to_dict()
            
            # Validar dados
            validation_result = security_service.validate_input(data, rules)
            
            if not validation_result['valid']:
                return {'error': 'Dados inválidos', 'details': validation_result['errors']}, 400
            
            # Sanitizar dados
            sanitized_data = security_service.sanitize_input(data)
            
            # Adicionar dados sanitizados ao request
            request.validated_data = sanitized_data
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

