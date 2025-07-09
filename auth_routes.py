from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from auth_service import AuthService, User
from werkzeug.utils import secure_filename
import os

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
auth_service = AuthService()

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Página e processamento de registro"""
    if request.method == 'POST':
        # Processar dados do formulário
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        nome_completo = request.form.get('nome_completo', '').strip()
        telefone = request.form.get('telefone', '').strip()
        
        # Validações básicas
        if not all([username, email, password]):
            flash('Todos os campos obrigatórios devem ser preenchidos', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Senhas não coincidem', 'error')
            return render_template('auth/register.html')
        
        # Tentar registrar usuário
        result = auth_service.registrar_usuario(
            username=username,
            email=email,
            password=password,
            nome_completo=nome_completo if nome_completo else None,
            telefone=telefone if telefone else None
        )
        
        if result['success']:
            flash('Usuário criado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(result['error'], 'error')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página e processamento de login"""
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email', '').strip()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'on'
        
        if not all([username_or_email, password]):
            flash('Username/email e senha são obrigatórios', 'error')
            return render_template('auth/login.html')
        
        # Tentar autenticar
        result = auth_service.autenticar_usuario(username_or_email, password)
        
        if result['success']:
            user = result['user']
            login_user(user, remember=remember_me)
            
            # Registrar atividade
            auth_service.registrar_atividade(
                user_id=int(user.id),
                memorial_id=None,
                acao='login',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            flash(f'Bem-vindo, {user.username}!', 'success')
            
            # Redirecionar para página solicitada ou dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('memorial.dashboard'))
        else:
            flash(result['error'], 'error')
            return render_template('auth/login.html')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    # Registrar atividade
    auth_service.registrar_atividade(
        user_id=int(current_user.id),
        memorial_id=None,
        acao='logout',
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    
    logout_user()
    flash('Logout realizado com sucesso', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """Página de perfil do usuário"""
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Alterar senha do usuário"""
    if request.method == 'POST':
        senha_atual = request.form.get('senha_atual', '')
        nova_senha = request.form.get('nova_senha', '')
        confirmar_senha = request.form.get('confirmar_senha', '')
        
        if not all([senha_atual, nova_senha, confirmar_senha]):
            flash('Todos os campos são obrigatórios', 'error')
            return render_template('auth/change_password.html')
        
        if nova_senha != confirmar_senha:
            flash('Nova senha e confirmação não coincidem', 'error')
            return render_template('auth/change_password.html')
        
        result = auth_service.alterar_senha(
            user_id=int(current_user.id),
            senha_atual=senha_atual,
            nova_senha=nova_senha
        )
        
        if result['success']:
            flash('Senha alterada com sucesso', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash(result['error'], 'error')
            return render_template('auth/change_password.html')
    
    return render_template('auth/change_password.html')

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """Recuperação de senha"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash('Email é obrigatório', 'error')
            return render_template('auth/forgot_password.html')
        
        result = auth_service.recuperar_senha(email)
        
        if result['success']:
            flash('Instruções de recuperação enviadas para seu email', 'info')
            # Em produção, não mostrar o token
            flash(f'Token de recuperação: {result["recovery_token"]}', 'warning')
            return redirect(url_for('auth.reset_password'))
        else:
            flash(result['error'], 'error')
            return render_template('auth/forgot_password.html')
    
    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    """Redefinir senha com token"""
    if request.method == 'POST':
        token = request.form.get('token', '').strip()
        nova_senha = request.form.get('nova_senha', '')
        confirmar_senha = request.form.get('confirmar_senha', '')
        
        if not all([token, nova_senha, confirmar_senha]):
            flash('Todos os campos são obrigatórios', 'error')
            return render_template('auth/reset_password.html')
        
        if nova_senha != confirmar_senha:
            flash('Senhas não coincidem', 'error')
            return render_template('auth/reset_password.html')
        
        result = auth_service.validar_token_recuperacao(token, nova_senha)
        
        if result['success']:
            flash('Senha redefinida com sucesso! Faça login com sua nova senha.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(result['error'], 'error')
            return render_template('auth/reset_password.html')
    
    return render_template('auth/reset_password.html')

# API endpoints para verificações AJAX
@auth_bp.route('/api/check_username', methods=['POST'])
def check_username():
    """Verifica se username está disponível"""
    username = request.json.get('username', '').strip()
    
    if not username:
        return jsonify({'available': False, 'message': 'Username é obrigatório'})
    
    user = auth_service.db.buscar_usuario_por_username(username)
    
    return jsonify({
        'available': user is None,
        'message': 'Username disponível' if user is None else 'Username já está em uso'
    })

@auth_bp.route('/api/check_email', methods=['POST'])
def check_email():
    """Verifica se email está disponível"""
    email = request.json.get('email', '').strip()
    
    if not email:
        return jsonify({'available': False, 'message': 'Email é obrigatório'})
    
    user = auth_service.db.buscar_usuario_por_email(email)
    
    return jsonify({
        'available': user is None,
        'message': 'Email disponível' if user is None else 'Email já está em uso'
    })

@auth_bp.route('/api/user_info')
@login_required
def user_info():
    """Retorna informações do usuário logado"""
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'nome_completo': current_user.nome_completo,
        'telefone': current_user.telefone
    })

# Middleware para verificar acesso a memoriais
def verificar_acesso_memorial(memorial_id):
    """
    Decorator para verificar acesso a memorial
    """
    def decorator(f):
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Você precisa estar logado para acessar esta página', 'error')
                return redirect(url_for('auth.login'))
            
            result = auth_service.verificar_acesso_memorial(
                user_id=int(current_user.id),
                memorial_id=memorial_id
            )
            
            if not result['access']:
                flash(result['message'], 'error')
                return redirect(url_for('memorial.dashboard'))
            
            # Adicionar nível de acesso ao request
            request.access_level = result['level']
            
            return f(*args, **kwargs)
        
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

