#!/usr/bin/env python3
"""
Enhanced Memorial Application - Main Flask Application
Integrates all advanced features for a comprehensive memorial experience
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from datetime import datetime, timedelta
import qrcode
import io
import base64
from functools import wraps

# Import enhanced modules
from database_enhanced import Database
from enhanced_routes import memorial_bp

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Configuration
app.config.update(
    UPLOAD_FOLDER='media/uploads',
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max file size
    ALLOWED_EXTENSIONS={'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'mp3', 'wav', 'pdf', 'doc', 'docx'},
    PERMANENT_SESSION_LIFETIME=timedelta(days=30)
)

# Ensure upload directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
for subfolder in ['photos', 'timeline', 'guestbook', 'locations', 'family', 'music', 'recipes', 'contributions']:
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], subfolder), exist_ok=True)

# Register blueprints
app.register_blueprint(memorial_bp)

# Initialize database
db = Database()

# Utility functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def generate_qr_code(url):
    """Generate QR Code for memorial sharing"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    return qr_code_base64

# Main routes
@app.route('/')
def index():
    """Home page with featured memorials"""
    # Usar métodos existentes do database
    recent_memorials = []
    try:
        # Buscar alguns memoriais recentes se o usuário estiver logado
        if 'user_id' in session:
            recent_memorials = db.get_user_memorials(session['user_id'])[:6]
    except:
        recent_memorials = []
    
    return render_template('index.html', 
                         featured_memorials=[],
                         recent_memorials=recent_memorials)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([name, email, password, confirm_password]):
            flash('Todos os campos são obrigatórios.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('As senhas não coincidem.', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        if db.get_user_by_email(email):
            flash('Este email já está cadastrado.', 'error')
            return render_template('register.html')
        
        # Create user
        password_hash = generate_password_hash(password)
        user_id = db.create_user(name, email, password_hash)
        
        if user_id:
            session['user_id'] = user_id
            session['user_name'] = name
            session['user_email'] = email
            session.permanent = True
            
            flash('Conta criada com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Erro ao criar conta. Tente novamente.', 'error')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me')
        
        if not email or not password:
            flash('Email e senha são obrigatórios.', 'error')
            return render_template('login.html')
        
        user = db.get_user_by_email(email)
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            
            if remember_me:
                session.permanent = True
            
            flash('Login realizado com sucesso!', 'success')
            
            # Redirect to intended page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Email ou senha incorretos.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('Logout realizado com sucesso.', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    user_memorials = db.get_user_memorials(session['user_id'])
    recent_activity = db.get_user_recent_activity(session['user_id'])
    stats = db.get_user_stats(session['user_id'])
    
    return render_template('dashboard.html',
                         memorials=user_memorials,
                         recent_activity=recent_activity,
                         stats=stats)

@app.route('/create-memorial', methods=['GET', 'POST'])
@login_required
def create_memorial():
    """Create new memorial"""
    if request.method == 'POST':
        # Basic memorial information
        name = request.form.get('name')
        birth_date = request.form.get('birth_date')
        death_date = request.form.get('death_date')
        biography = request.form.get('biography')
        family_message = request.form.get('family_message')
        
        # Validation
        if not name:
            flash('O nome é obrigatório.', 'error')
            return render_template('create_memorial.html')
        
        # Handle file uploads
        profile_photo = None
        cover_photo = None
        
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'photos', filename)
                file.save(file_path)
                profile_photo = os.path.join('photos', filename)
        
        if 'cover_photo' in request.files:
            file = request.files['cover_photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'photos', filename)
                file.save(file_path)
                cover_photo = os.path.join('photos', filename)
        
        # Create memorial
        memorial_id = db.create_memorial(
            user_id=session['user_id'],
            name=name,
            birth_date=birth_date,
            death_date=death_date,
            biography=biography,
            family_message=family_message,
            profile_photo=profile_photo,
            cover_photo=cover_photo
        )
        
        if memorial_id:
            flash('Memorial criado com sucesso!', 'success')
            return redirect(url_for('memorial_enhanced.view_memorial_enhanced', memorial_id=memorial_id))
        else:
            flash('Erro ao criar memorial. Tente novamente.', 'error')
    
    return render_template('create_memorial.html')

@app.route('/memorial/<int:memorial_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_memorial(memorial_id):
    """Edit memorial basic information"""
    memorial = db.get_memorial_by_id(memorial_id)
    
    if not memorial or memorial['user_id'] != session['user_id']:
        flash('Memorial não encontrado ou sem permissão.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Update memorial information
        name = request.form.get('name')
        birth_date = request.form.get('birth_date')
        death_date = request.form.get('death_date')
        biography = request.form.get('biography')
        family_message = request.form.get('family_message')
        
        # New fields
        timeline_events = request.form.get('timeline_events')
        music_embed_url = request.form.get('music_embed_url')
        featured_testimonials = request.form.get('featured_testimonials')
        burial_location = request.form.get('burial_location')
        donation_link = request.form.get('donation_link')
        quotes_values = request.form.get('quotes_values')
        
        # Handle file uploads
        profile_photo = memorial['profile_photo']
        cover_photo = memorial['cover_photo']
        
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'photos', filename)
                file.save(file_path)
                profile_photo = os.path.join('photos', filename)
        
        if 'cover_photo' in request.files:
            file = request.files['cover_photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'photos', filename)
                file.save(file_path)
                cover_photo = os.path.join('photos', filename)
        
        # Update memorial
        success = db.update_memorial(
            memorial_id=memorial_id,
            name=name,
            birth_date=birth_date,
            death_date=death_date,
            biography=biography,
            family_message=family_message,
            profile_photo=profile_photo,
            cover_photo=cover_photo,
            timeline_events=timeline_events,
            music_embed_url=music_embed_url,
            featured_testimonials=featured_testimonials,
            burial_location=burial_location,
            donation_link=donation_link,
            quotes_values=quotes_values
        )
        
        if success:
            flash('Memorial atualizado com sucesso!', 'success')
            return redirect(url_for('memorial_enhanced.view_memorial_enhanced', memorial_id=memorial_id))
        else:
            flash('Erro ao atualizar memorial.', 'error')
    
    return render_template('edit_memorial.html', memorial=memorial)

@app.route('/search')
def search():
    """Search memorials"""
    query = request.args.get('q', '')
    page = int(request.args.get('page', 1))
    per_page = 12
    
    if query:
        results, total = db.search_memorials(query, page, per_page)
        total_pages = (total + per_page - 1) // per_page
    else:
        results = []
        total = 0
        total_pages = 0
    
    return render_template('search_results.html',
                         query=query,
                         results=results,
                         total=total,
                         page=page,
                         total_pages=total_pages)

@app.route('/browse')
def browse():
    """Browse all memorials"""
    page = int(request.args.get('page', 1))
    category = request.args.get('category', 'all')
    sort_by = request.args.get('sort', 'recent')
    per_page = 12
    
    memorials, total = db.browse_memorials(page, per_page, category, sort_by)
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('browse_memorials.html',
                         memorials=memorials,
                         total=total,
                         page=page,
                         total_pages=total_pages,
                         category=category,
                         sort_by=sort_by)

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    user = db.get_user_by_id(session['user_id'])
    user_stats = db.get_user_stats(session['user_id'])
    
    return render_template('profile.html', user=user, stats=user_stats)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    user = db.get_user_by_id(session['user_id'])
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not name or not email:
            flash('Nome e email são obrigatórios.', 'error')
            return render_template('edit_profile.html', user=user)
        
        # Check if email is already taken by another user
        existing_user = db.get_user_by_email(email)
        if existing_user and existing_user['id'] != session['user_id']:
            flash('Este email já está sendo usado por outro usuário.', 'error')
            return render_template('edit_profile.html', user=user)
        
        # Password change validation
        password_hash = user['password_hash']
        if new_password:
            if not current_password:
                flash('Senha atual é obrigatória para alterar a senha.', 'error')
                return render_template('edit_profile.html', user=user)
            
            if not check_password_hash(user['password_hash'], current_password):
                flash('Senha atual incorreta.', 'error')
                return render_template('edit_profile.html', user=user)
            
            if new_password != confirm_password:
                flash('As novas senhas não coincidem.', 'error')
                return render_template('edit_profile.html', user=user)
            
            if len(new_password) < 6:
                flash('A nova senha deve ter pelo menos 6 caracteres.', 'error')
                return render_template('edit_profile.html', user=user)
            
            password_hash = generate_password_hash(new_password)
        
        # Update user
        success = db.update_user(session['user_id'], name, email, password_hash)
        
        if success:
            session['user_name'] = name
            session['user_email'] = email
            flash('Perfil atualizado com sucesso!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Erro ao atualizar perfil.', 'error')
    
    return render_template('edit_profile.html', user=user)

# API Routes
@app.route('/api/memorial/<int:memorial_id>/stats')
def api_memorial_stats(memorial_id):
    """API endpoint for memorial statistics"""
    stats = {
        'photos': len(db.get_memorial_photos(memorial_id)),
        'comments': len(db.get_memorial_comments(memorial_id)),
        'guestbook_entries': len(db.get_guestbook_entries(memorial_id)),
        'timeline_events': len(db.get_timeline_events(memorial_id)),
        'family_members': len(db.get_family_members(memorial_id)),
        'favorite_music': len(db.get_favorite_music(memorial_id)),
        'quotes': len(db.get_quotes(memorial_id)),
        'recipes': len(db.get_recipes(memorial_id)),
        'memorial_events': len(db.get_memorial_events(memorial_id)),
        'visitor_contributions': len(db.get_visitor_contributions(memorial_id)),
        'memory_locations': len(db.get_memory_locations(memorial_id))
    }
    
    return jsonify(stats)

@app.route('/api/themes')
def api_themes():
    """API endpoint for available themes"""
    themes = db.get_all_themes()
    
    themes_list = []
    for theme in themes:
        themes_list.append({
            'id': theme['id'],
            'name': theme['name'],
            'description': theme['description'],
            'primary_color': theme['primary_color'],
            'secondary_color': theme['secondary_color'],
            'accent_color': theme['accent_color'],
            'background_color': theme['background_color'],
            'text_color': theme['text_color']
        })
    
    return jsonify(themes_list)

@app.route('/api/upload', methods=['POST'])
@login_required
def api_upload():
    """API endpoint for file uploads"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        
        subfolder = request.form.get('subfolder', 'general')
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], subfolder)
        os.makedirs(upload_path, exist_ok=True)
        
        file_path = os.path.join(upload_path, filename)
        file.save(file_path)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'path': os.path.join(subfolder, filename)
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.errorhandler(413)
def file_too_large(error):
    flash('Arquivo muito grande. O tamanho máximo é 16MB.', 'error')
    return redirect(request.url)

# Template filters
@app.template_filter('datetime')
def datetime_filter(value, format='%d/%m/%Y'):
    if isinstance(value, str):
        value = datetime.strptime(value, '%Y-%m-%d')
    return value.strftime(format)

@app.template_filter('timeago')
def timeago_filter(value):
    if isinstance(value, str):
        value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    
    now = datetime.now()
    diff = now - value
    
    if diff.days > 0:
        return f'{diff.days} dia{"s" if diff.days > 1 else ""} atrás'
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f'{hours} hora{"s" if hours > 1 else ""} atrás'
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f'{minutes} minuto{"s" if minutes > 1 else ""} atrás'
    else:
        return 'Agora mesmo'

# Context processors
@app.context_processor
def inject_user():
    return dict(
        current_user_id=session.get('user_id'),
        current_user_name=session.get('user_name'),
        current_user_email=session.get('user_email')
    )

@app.context_processor
def inject_globals():
    return dict(
        app_name='Memorial Online',
        app_version='2.0.0',
        current_year=datetime.now().year
    )

# CLI Commands
@app.cli.command()
def init_db():
    """Initialize the database with sample data"""
    db.init_db()
#     db.create_sample_themes()
    print("Database initialized successfully!")

@app.cli.command()
def create_admin():
    """Create admin user"""
    name = input("Admin name: ")
    email = input("Admin email: ")
    password = input("Admin password: ")
    
    password_hash = generate_password_hash(password)
    user_id = db.create_user(name, email, password_hash, is_admin=True)
    
    if user_id:
        print(f"Admin user created successfully! ID: {user_id}")
    else:
        print("Error creating admin user.")

# Development configuration
if __name__ == '__main__':
    # Initialize database on first run
    if not os.path.exists('memorial.db'):
        db.init_db()
#         db.create_sample_themes()
        print("Database initialized!")
    
    # Run development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )

