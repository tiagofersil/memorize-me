from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import Database

accounts_bp = Blueprint('accounts', __name__)
db = Database()

@accounts_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = db.get_user_by_username(username)
        
        if user and db.verify_password(user, password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('accounts.profile'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')
    
    return render_template('login.html')

@accounts_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Verificar se usuário já existe
        if db.get_user_by_username(username):
            flash('Nome de usuário já existe.', 'danger')
            return render_template('register.html')
        
        if db.get_user_by_email(email):
            flash('Email já está cadastrado.', 'danger')
            return render_template('register.html')
        
        # Criar novo usuário
        if db.create_user(username, email, password):
            flash('Cadastro realizado com sucesso! Faça login.', 'success')
            return redirect(url_for('accounts.login'))
        else:
            flash('Erro ao criar usuário. Tente novamente.', 'danger')
    
    return render_template('register.html')

@accounts_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Você precisa fazer login para acessar esta página.', 'warning')
        return redirect(url_for('accounts.login'))
    
    user_id = session['user_id']
    memorials = db.get_user_memorials(user_id)
    
    return render_template('profile.html', memorials=memorials)

@accounts_bp.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('index'))

