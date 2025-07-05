from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from werkzeug.utils import secure_filename
from database_enhanced import Database
import os
import json
from datetime import datetime
import qrcode
import io
import base64

# Criar blueprint para as rotas do memorial
memorial_bp = Blueprint('memorial_enhanced', __name__)

# Configurações
UPLOAD_FOLDER = 'media/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'mp3', 'wav'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, subfolder=''):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Adicionar timestamp para evitar conflitos
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        
        upload_path = os.path.join(UPLOAD_FOLDER, subfolder)
        os.makedirs(upload_path, exist_ok=True)
        
        file_path = os.path.join(upload_path, filename)
        file.save(file_path)
        return os.path.join(subfolder, filename) if subfolder else filename
    return None

@memorial_bp.route('/memorial/<int:memorial_id>')
def view_memorial_enhanced(memorial_id):
    """Visualizar memorial com todas as funcionalidades"""
    db = Database()
    
    # Buscar dados básicos do memorial
    memorial = db.get_memorial_by_id(memorial_id)
    if not memorial:
        flash('Memorial não encontrado.', 'error')
        return redirect(url_for('memorial.memorial_home'))
    
    # Buscar todos os dados relacionados
    photos = db.get_memorial_photos(memorial_id)
    comments = db.get_memorial_comments(memorial_id)
    timeline_events = db.get_timeline_events(memorial_id)
    guestbook_entries = db.get_guestbook_entries(memorial_id)
    memory_locations = db.get_memory_locations(memorial_id)
    family_members = db.get_family_members(memorial_id)
    favorite_music = db.get_favorite_music(memorial_id)
    quotes = db.get_quotes(memorial_id)
    recipes = db.get_recipes(memorial_id)
    memorial_events = db.get_memorial_events(memorial_id)
    visitor_contributions = db.get_visitor_contributions(memorial_id)
    
    # Gerar QR Code
    qr_code = generate_qr_code(request.url)
    
    return render_template('generate_memorial_enhanced.html',
                         memorial=memorial,
                         photos=photos,
                         comments=comments,
                         timeline_events=timeline_events,
                         guestbook_entries=guestbook_entries,
                         memory_locations=memory_locations,
                         family_members=family_members,
                         favorite_music=favorite_music,
                         quotes=quotes,
                         recipes=recipes,
                         memorial_events=memorial_events,
                         visitor_contributions=visitor_contributions,
                         qr_code=qr_code)

# TIMELINE EVENTS
@memorial_bp.route('/memorial/<int:memorial_id>/timeline/add', methods=['POST'])
def add_timeline_event(memorial_id):
    """Adicionar evento à linha do tempo"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    db = Database()
    memorial = db.get_memorial_by_id(memorial_id)
    
    if not memorial or memorial['user_id'] != session['user_id']:
        return jsonify({'error': 'Memorial não encontrado ou sem permissão'}), 403
    
    title = request.form.get('title')
    description = request.form.get('description')
    event_date = request.form.get('event_date')
    event_type = request.form.get('event_type', 'milestone')
    location = request.form.get('location')
    
    # Upload de foto se fornecida
    photo_path = None
    if 'photo' in request.files:
        photo_path = save_uploaded_file(request.files['photo'], 'timeline')
    
    event_id = db.add_timeline_event(memorial_id, title, description, event_date, event_type, photo_path, location)
    
    if event_id:
        flash('Evento adicionado à linha do tempo!', 'success')
    else:
        flash('Erro ao adicionar evento.', 'error')
    
    return redirect(url_for('memorial_enhanced.view_memorial_enhanced', memorial_id=memorial_id))

# GUESTBOOK
@memorial_bp.route('/memorial/<int:memorial_id>/guestbook/add', methods=['POST'])
def add_guestbook_entry(memorial_id):
    """Adicionar entrada no livro de visitas"""
    db = Database()
    memorial = db.get_memorial_by_id(memorial_id)
    
    if not memorial:
        flash('Memorial não encontrado.', 'error')
        return redirect(url_for('memorial.memorial_home'))
    
    author_name = request.form.get('author_name')
    author_email = request.form.get('author_email')
    relationship = request.form.get('relationship')
    message = request.form.get('message')
    
    if not author_name or not message:
        flash('Nome e mensagem são obrigatórios.', 'error')
        return redirect(url_for('memorial_enhanced.view_memorial_enhanced', memorial_id=memorial_id))
    
    # Upload de arquivos opcionais
    photo_path = None
    video_path = None
    
    if 'photo_upload' in request.files:
        photo_path = save_uploaded_file(request.files['photo_upload'], 'guestbook')
    
    if 'video_upload' in request.files:
        video_path = save_uploaded_file(request.files['video_upload'], 'guestbook')
    
    entry_id = db.add_guestbook_entry(memorial_id, author_name, message, author_email, relationship, photo_path, video_path)
    
    if entry_id:
        flash('Sua mensagem foi adicionada ao livro de visitas!', 'success')
    else:
        flash('Erro ao adicionar mensagem.', 'error')
    
    return redirect(url_for('memorial_enhanced.view_memorial_enhanced', memorial_id=memorial_id))

# MEMORY LOCATIONS
@memorial_bp.route('/memorial/<int:memorial_id>/locations/add', methods=['POST'])
def add_memory_location(memorial_id):
    """Adicionar local de memória"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    db = Database()
    memorial = db.get_memorial_by_id(memorial_id)
    
    if not memorial or memorial['user_id'] != session['user_id']:
        return jsonify({'error': 'Memorial não encontrado ou sem permissão'}), 403
    
    location_name = request.form.get('location_name')
    description = request.form.get('description')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    address = request.form.get('address')
    location_type = request.form.get('location_type', 'memory')
    
    # Upload de foto se fornecida
    photo_path = None
    if 'photo' in request.files:
        photo_path = save_uploaded_file(request.files['photo'], 'locations')
    
    location_id = db.add_memory_location(memorial_id, location_name, description, 
                                       float(latitude) if latitude else None,
                                       float(longitude) if longitude else None,
                                       address, location_type, photo_path)
    
    if location_id:
        flash('Local de memória adicionado!', 'success')
    else:
        flash('Erro ao adicionar local.', 'error')
    
    return redirect(url_for('memorial_enhanced.view_memorial_enhanced', memorial_id=memorial_id))

# FAMILY TREE
@memorial_bp.route('/memorial/<int:memorial_id>/family/add', methods=['POST'])
def add_family_member(memorial_id):
    """Adicionar membro da família"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    db = Database()
    memorial = db.get_memorial_by_id(memorial_id)
    
    if not memorial or memorial['user_id'] != session['user_id']:
        return jsonify({'error': 'Memorial não encontrado ou sem permissão'}), 403
    
    name = request.form.get('name')
    relationship = request.form.get('relationship')
    birth_date = request.form.get('birth_date')
    death_date = request.form.get('death_date')
    memorial_link = request.form.get('memorial_link')
    notes = request.form.get('notes')
    
    # Upload de foto se fornecida
    photo_path = None
    if 'photo' in request.files:
        photo_path = save_uploaded_file(request.files['photo'], 'family')
    
    member_id = db.add_family_member(memorial_id, name, relationship, birth_date, death_date, photo_path, memorial_link, notes)
    
    if member_id:
        flash('Membro da família adicionado!', 'success')
    else:
        flash('Erro ao adicionar membro da família.', 'error')
    
    return redirect(url_for('memorial_enhanced.view_memorial_enhanced', memorial_id=memorial_id))

# FAVORITE MUSIC
@memorial_bp.route('/memorial/<int:memorial_id>/music/add', methods=['POST'])
def add_favorite_music(memorial_id):
    """Adicionar música favorita"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    db = Database()
    memorial = db.get_memorial_by_id(memorial_id)
    
    if not memorial or memorial['user_id'] != session['user_id']:
        return jsonify({'error': 'Memorial não encontrado ou sem permissão'}), 403
    
    title = request.form.get('title')
    artist = request.form.get('artist')
    album = request.form.get('album')
    youtube_url = request.form.get('youtube_url')
    spotify_url = request.form.get('spotify_url')
    description = request.form.get('description')
    
    # Upload de arquivo MP3 se fornecido
    file_path = None
    if 'music_file' in request.files:
        file_path = save_uploaded_file(request.files['music_file'], 'music')
    
    music_id = db.add_favorite_music(memorial_id, title, artist, album, file_path, youtube_url, spotify_url, description)
    
    if music_id:
        flash('Música favorita adicionada!', 'success')
    else:
        flash('Erro ao adicionar música.', 'error')
    
    return redirect(url_for('memorial_enhanced.view_memorial_enhanced', memorial_id=memorial_id))

# QUOTES
@memorial_bp.route('/memorial/<int:memorial_id>/quotes/add', methods=['POST'])
def add_quote(memorial_id):
    """Adicionar citação"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    db = Database()
    memorial = db.get_memorial_by_id(memorial_id)
    
    if not memorial or memorial['user_id'] != session['user_id']:
        return jsonify({'error': 'Memorial não encontrado ou sem permissão'}), 403
    
    quote_text = request.form.get('quote_text')
    context = request.form.get('context')
    category = request.form.get('category', 'wisdom')
    contributed_by = request.form.get('contributed_by')
    
    quote_id = db.add_quote(memorial_id, quote_text, context, category, contributed_by)
    
    if quote_id:
        flash('Citação adicionada!', 'success')
    else:
        flash('Erro ao adicionar citação.', 'error')
    
    return redirect(url_for('memorial_enhanced.view_memorial_enhanced', memorial_id=memorial_id))

# RECIPES
@memorial_bp.route('/memorial/<int:memorial_id>/recipes/add', methods=['POST'])
def add_recipe(memorial_id):
    """Adicionar receita"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    db = Database()
    memorial = db.get_memorial_by_id(memorial_id)
    
    if not memorial or memorial['user_id'] != session['user_id']:
        return jsonify({'error': 'Memorial não encontrado ou sem permissão'}), 403
    
    title = request.form.get('title')
    description = request.form.get('description')
    ingredients = request.form.get('ingredients')
    instructions = request.form.get('instructions')
    prep_time = request.form.get('prep_time')
    cook_time = request.form.get('cook_time')
    servings = request.form.get('servings')
    story = request.form.get('story')
    
    # Upload de foto se fornecida
    photo_path = None
    if 'photo' in request.files:
        photo_path = save_uploaded_file(request.files['photo'], 'recipes')
    
    recipe_id = db.add_recipe(memorial_id, title, ingredients, instructions, description,
                             int(prep_time) if prep_time else None,
                             int(cook_time) if cook_time else None,
                             int(servings) if servings else None,
                             photo_path, story)
    
    if recipe_id:
        flash('Receita adicionada!', 'success')
    else:
        flash('Erro ao adicionar receita.', 'error')
    
    return redirect(url_for('memorial_enhanced.view_memorial_enhanced', memorial_id=memorial_id))

# VISITOR CONTRIBUTIONS
@memorial_bp.route('/memorial/<int:memorial_id>/contribute', methods=['POST'])
def add_visitor_contribution(memorial_id):
    """Adicionar contribuição de visitante"""
    db = Database()
    memorial = db.get_memorial_by_id(memorial_id)
    
    if not memorial:
        flash('Memorial não encontrado.', 'error')
        return redirect(url_for('memorial.memorial_home'))
    
    contributor_name = request.form.get('contributor_name')
    contributor_email = request.form.get('contributor_email')
    contribution_type = request.form.get('contribution_type')
    title = request.form.get('title')
    description = request.form.get('description')
    content_text = request.form.get('content_text')
    
    if not contributor_name or not contribution_type:
        flash('Nome e tipo de contribuição são obrigatórios.', 'error')
        return redirect(url_for('memorial_enhanced.view_memorial_enhanced', memorial_id=memorial_id))
    
    # Upload de arquivo se fornecido
    file_path = None
    if 'file_upload' in request.files:
        file_path = save_uploaded_file(request.files['file_upload'], 'contributions')
    
    contribution_id = db.add_visitor_contribution(memorial_id, contributor_name, contribution_type,
                                                title, description, file_path, content_text, contributor_email)
    
    if contribution_id:
        flash('Sua contribuição foi enviada e está aguardando aprovação!', 'success')
    else:
        flash('Erro ao enviar contribuição.', 'error')
    
    return redirect(url_for('memorial_enhanced.view_memorial_enhanced', memorial_id=memorial_id))

# MEMORIAL EVENTS
@memorial_bp.route('/memorial/<int:memorial_id>/events/add', methods=['POST'])
def add_memorial_event(memorial_id):
    """Adicionar evento do memorial"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    db = Database()
    memorial = db.get_memorial_by_id(memorial_id)
    
    if not memorial or memorial['user_id'] != session['user_id']:
        return jsonify({'error': 'Memorial não encontrado ou sem permissão'}), 403
    
    title = request.form.get('title')
    description = request.form.get('description')
    event_date = request.form.get('event_date')
    event_time = request.form.get('event_time')
    location = request.form.get('location')
    event_type = request.form.get('event_type', 'memorial')
    organizer_name = request.form.get('organizer_name')
    organizer_contact = request.form.get('organizer_contact')
    max_attendees = request.form.get('max_attendees')
    
    event_id = db.add_memorial_event(memorial_id, title, event_date, description, event_time,
                                   location, event_type, organizer_name, organizer_contact,
                                   int(max_attendees) if max_attendees else None)
    
    if event_id:
        flash('Evento adicionado!', 'success')
    else:
        flash('Erro ao adicionar evento.', 'error')
    
    return redirect(url_for('memorial_enhanced.view_memorial_enhanced', memorial_id=memorial_id))

# ADMIN ROUTES
@memorial_bp.route('/memorial/<int:memorial_id>/admin')
def memorial_admin(memorial_id):
    """Painel administrativo do memorial"""
    if 'user_id' not in session:
        flash('Você precisa estar logado.', 'error')
        return redirect(url_for('auth.login'))
    
    db = Database()
    memorial = db.get_memorial_by_id(memorial_id)
    
    if not memorial or memorial['user_id'] != session['user_id']:
        flash('Memorial não encontrado ou sem permissão.', 'error')
        return redirect(url_for('memorial.memorial_home'))
    
    # Buscar contribuições pendentes
    pending_contributions = db.get_visitor_contributions(memorial_id, approved_only=False)
    pending_guestbook = db.get_guestbook_entries(memorial_id, approved_only=False)
    
    return render_template('memorial_admin.html',
                         memorial=memorial,
                         pending_contributions=pending_contributions,
                         pending_guestbook=pending_guestbook)

@memorial_bp.route('/memorial/<int:memorial_id>/approve/<item_type>/<int:item_id>')
def approve_item(memorial_id, item_type, item_id):
    """Aprovar item (contribuição, entrada do livro de visitas, etc.)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    db = Database()
    memorial = db.get_memorial_by_id(memorial_id)
    
    if not memorial or memorial['user_id'] != session['user_id']:
        return jsonify({'error': 'Memorial não encontrado ou sem permissão'}), 403
    
    conn = db.get_connection()
    
    if item_type == 'contribution':
        conn.execute("UPDATE visitor_contributions SET is_approved = 1 WHERE id = ?", (item_id,))
    elif item_type == 'guestbook':
        conn.execute("UPDATE guestbook_entries SET is_approved = 1 WHERE id = ?", (item_id,))
    
    conn.commit()
    conn.close()
    
    flash('Item aprovado!', 'success')
    return redirect(url_for('memorial_enhanced.memorial_admin', memorial_id=memorial_id))

# THEMES
@memorial_bp.route('/memorial/<int:memorial_id>/theme/change', methods=['POST'])
def change_theme(memorial_id):
    """Alterar tema do memorial"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    db = Database()
    memorial = db.get_memorial_by_id(memorial_id)
    
    if not memorial or memorial['user_id'] != session['user_id']:
        return jsonify({'error': 'Memorial não encontrado ou sem permissão'}), 403
    
    theme_id = request.form.get('theme_id')
    custom_colors = request.form.get('custom_colors')  # JSON string
    
    conn = db.get_connection()
    
    update_fields = ["theme_id = ?"]
    values = [theme_id]
    
    if custom_colors:
        update_fields.append("custom_colors = ?")
        values.append(custom_colors)
    
    values.append(memorial_id)
    
    query = f"UPDATE memorials SET {', '.join(update_fields)} WHERE id = ?"
    conn.execute(query, values)
    conn.commit()
    conn.close()
    
    flash('Tema alterado!', 'success')
    return redirect(url_for('memorial_enhanced.view_memorial_enhanced', memorial_id=memorial_id))

@memorial_bp.route('/api/themes')
def get_themes():
    """API para buscar temas disponíveis"""
    db = Database()
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

# DOWNLOAD/EXPORT
@memorial_bp.route('/memorial/<int:memorial_id>/download')
def download_memorial(memorial_id):
    """Download do memorial em PDF"""
    # Esta funcionalidade seria implementada com uma biblioteca como WeasyPrint
    # Por enquanto, retorna um placeholder
    flash('Funcionalidade de download em desenvolvimento.', 'info')
    return redirect(url_for('memorial_enhanced.view_memorial_enhanced', memorial_id=memorial_id))

# STATISTICS
@memorial_bp.route('/api/memorial/<int:memorial_id>/stats')
def memorial_stats(memorial_id):
    """API para estatísticas do memorial"""
    db = Database()
    
    stats = {
        'photos': len(db.get_memorial_photos(memorial_id)),
        'comments': len(db.get_memorial_comments(memorial_id)),
        'guestbook_entries': len(db.get_guestbook_entries(memorial_id)),
        'timeline_events': len(db.get_timeline_events(memorial_id)),
        'family_members': len(db.get_family_members(memorial_id)),
        'favorite_music': len(db.get_favorite_music(memorial_id)),
        'quotes': len(db.get_quotes(memorial_id)),
        'recipes': len(db.get_recipes(memorial_id)),
        'memorial_events': len(db.get_memorial_events(memorial_id))
    }
    
    return jsonify(stats)

# UTILITY FUNCTIONS
def generate_qr_code(url):
    """Gerar QR Code para o memorial"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Converter para base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    return qr_code_base64

# SEARCH AND FILTER
@memorial_bp.route('/api/memorial/<int:memorial_id>/search')
def search_memorial_content(memorial_id):
    """Buscar conteúdo dentro do memorial"""
    query = request.args.get('q', '')
    content_type = request.args.get('type', 'all')
    
    if not query:
        return jsonify([])
    
    db = Database()
    conn = db.get_connection()
    
    results = []
    
    if content_type in ['all', 'timeline']:
        timeline_results = conn.execute(
            "SELECT 'timeline' as type, title, description FROM timeline_events WHERE memorial_id = ? AND (title LIKE ? OR description LIKE ?)",
            (memorial_id, f'%{query}%', f'%{query}%')
        ).fetchall()
        results.extend([dict(row) for row in timeline_results])
    
    if content_type in ['all', 'quotes']:
        quote_results = conn.execute(
            "SELECT 'quote' as type, quote_text as title, context as description FROM quotes WHERE memorial_id = ? AND quote_text LIKE ?",
            (memorial_id, f'%{query}%')
        ).fetchall()
        results.extend([dict(row) for row in quote_results])
    
    if content_type in ['all', 'recipes']:
        recipe_results = conn.execute(
            "SELECT 'recipe' as type, title, description FROM recipes WHERE memorial_id = ? AND (title LIKE ? OR description LIKE ?)",
            (memorial_id, f'%{query}%', f'%{query}%')
        ).fetchall()
        results.extend([dict(row) for row in recipe_results])
    
    conn.close()
    return jsonify(results)

# ERROR HANDLERS
@memorial_bp.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@memorial_bp.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

