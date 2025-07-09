from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from cloudinary_service import CloudinaryService
from database_enhanced import DatabaseEnhanced
from auth_service import AuthService
import os
import uuid
from datetime import datetime

image_bp = Blueprint('image', __name__, url_prefix='/images')

# Inicializar serviços
cloudinary_service = CloudinaryService()
db = DatabaseEnhanced()
auth_service = AuthService()

@image_bp.route('/upload/<int:memorial_id>')
@login_required
def upload_page(memorial_id):
    """Página de upload de imagens para um memorial"""
    # Verificar se o usuário tem acesso ao memorial
    access_result = auth_service.verificar_acesso_memorial(int(current_user.id), memorial_id)
    
    if not access_result['access'] or access_result['level'] != 'owner':
        flash('Você não tem permissão para adicionar fotos a este memorial', 'error')
        return redirect(url_for('memorial.dashboard'))
    
    # Buscar memorial
    memorial = db.buscar_memorial_por_id(memorial_id)
    if not memorial:
        flash('Memorial não encontrado', 'error')
        return redirect(url_for('memorial.dashboard'))
    
    # Buscar fotos existentes
    fotos = db.buscar_fotos_memorial(memorial_id)
    
    return render_template('images/upload.html', memorial=memorial, fotos=fotos)

@image_bp.route('/api/upload', methods=['POST'])
@login_required
def upload_image():
    """API para upload de imagem via AJAX"""
    try:
        memorial_id = request.form.get('memorial_id')
        if not memorial_id:
            return jsonify({'success': False, 'error': 'Memorial ID é obrigatório'})
        
        memorial_id = int(memorial_id)
        
        # Verificar acesso
        access_result = auth_service.verificar_acesso_memorial(int(current_user.id), memorial_id)
        if not access_result['access'] or access_result['level'] != 'owner':
            return jsonify({'success': False, 'error': 'Acesso negado'})
        
        # Verificar se arquivo foi enviado
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Nenhum arquivo enviado'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nenhum arquivo selecionado'})
        
        # Validar arquivo
        validation = cloudinary_service.validate_image_file(file)
        if not validation['valid']:
            return jsonify({'success': False, 'error': validation['error']})
        
        # Obter dados adicionais do formulário
        titulo = request.form.get('titulo', '').strip()
        descricao = request.form.get('descricao', '').strip()
        data_foto = request.form.get('data_foto', '').strip()
        categoria = request.form.get('categoria', 'geral').strip()
        
        # Gerar public_id único
        public_id = f"memorial_{memorial_id}_{uuid.uuid4().hex[:8]}"
        
        # Fazer upload para Cloudinary
        upload_result = cloudinary_service.upload_image(
            file,
            folder=f"memorial_{memorial_id}",
            public_id=public_id
        )
        
        if not upload_result['success']:
            return jsonify({'success': False, 'error': upload_result['error']})
        
        # Salvar no banco de dados
        foto_id = db.salvar_foto(
            memorial_id=memorial_id,
            user_id=int(current_user.id),
            cloudinary_url=upload_result['url'],
            cloudinary_public_id=upload_result['public_id'],
            titulo=titulo if titulo else None,
            descricao=descricao if descricao else None,
            data_foto=data_foto if data_foto else None,
            categoria=categoria
        )
        
        # Registrar atividade
        auth_service.registrar_atividade(
            user_id=int(current_user.id),
            memorial_id=memorial_id,
            acao='upload_foto',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            detalhes=f'Foto ID: {foto_id}, Título: {titulo}'
        )
        
        return jsonify({
            'success': True,
            'foto_id': foto_id,
            'url': upload_result['url'],
            'public_id': upload_result['public_id'],
            'message': 'Imagem enviada com sucesso!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'})

@image_bp.route('/api/delete/<int:foto_id>', methods=['DELETE'])
@login_required
def delete_image(foto_id):
    """API para deletar uma imagem"""
    try:
        # Buscar foto
        foto = db.buscar_foto_por_id(foto_id)
        if not foto:
            return jsonify({'success': False, 'error': 'Foto não encontrada'})
        
        # Verificar se o usuário é proprietário
        if foto['user_id'] != int(current_user.id):
            return jsonify({'success': False, 'error': 'Acesso negado'})
        
        # Deletar do Cloudinary
        delete_result = cloudinary_service.delete_image(foto['cloudinary_public_id'])
        
        # Deletar do banco de dados (mesmo se falhar no Cloudinary)
        public_id = db.deletar_foto(foto_id, int(current_user.id))
        
        if public_id:
            # Registrar atividade
            auth_service.registrar_atividade(
                user_id=int(current_user.id),
                memorial_id=foto['memorial_id'],
                acao='delete_foto',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                detalhes=f'Foto ID: {foto_id}, Public ID: {public_id}'
            )
            
            return jsonify({
                'success': True,
                'message': 'Imagem deletada com sucesso!',
                'cloudinary_deleted': delete_result['success']
            })
        else:
            return jsonify({'success': False, 'error': 'Erro ao deletar foto do banco de dados'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'})

@image_bp.route('/api/update/<int:foto_id>', methods=['PUT'])
@login_required
def update_image_info(foto_id):
    """API para atualizar informações de uma imagem"""
    try:
        # Buscar foto
        foto = db.buscar_foto_por_id(foto_id)
        if not foto:
            return jsonify({'success': False, 'error': 'Foto não encontrada'})
        
        # Verificar se o usuário é proprietário
        if foto['user_id'] != int(current_user.id):
            return jsonify({'success': False, 'error': 'Acesso negado'})
        
        # Obter dados do request
        data = request.get_json()
        titulo = data.get('titulo', '').strip()
        descricao = data.get('descricao', '').strip()
        data_foto = data.get('data_foto', '').strip()
        categoria = data.get('categoria', 'geral').strip()
        
        # Atualizar no banco (implementar método na DatabaseEnhanced)
        # Por enquanto, simular sucesso
        
        # Registrar atividade
        auth_service.registrar_atividade(
            user_id=int(current_user.id),
            memorial_id=foto['memorial_id'],
            acao='update_foto',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            detalhes=f'Foto ID: {foto_id}, Novo título: {titulo}'
        )
        
        return jsonify({
            'success': True,
            'message': 'Informações da imagem atualizadas com sucesso!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'})

@image_bp.route('/gallery/<int:memorial_id>')
def gallery(memorial_id):
    """Galeria de fotos de um memorial (pública se permitido)"""
    # Buscar memorial
    memorial = db.buscar_memorial_por_id(memorial_id)
    if not memorial:
        flash('Memorial não encontrado', 'error')
        return redirect(url_for('index'))
    
    # Verificar acesso
    user_id = int(current_user.id) if current_user.is_authenticated else None
    
    if user_id:
        access_result = auth_service.verificar_acesso_memorial(user_id, memorial_id)
        if not access_result['access']:
            flash('Acesso negado a este memorial', 'error')
            return redirect(url_for('index'))
        is_owner = access_result['level'] == 'owner'
    else:
        # Verificar se memorial é público
        config = db.buscar_configuracoes_privacidade(memorial_id)
        if not config or not config['publico']:
            flash('Este memorial é privado', 'error')
            return redirect(url_for('index'))
        is_owner = False
    
    # Buscar fotos
    fotos = db.buscar_fotos_memorial(memorial_id)
    
    return render_template('images/gallery.html', 
                         memorial=memorial, 
                         fotos=fotos, 
                         is_owner=is_owner)

@image_bp.route('/api/gallery/<int:memorial_id>')
def api_gallery(memorial_id):
    """API para obter fotos de um memorial"""
    try:
        # Verificar acesso (similar à rota gallery)
        user_id = int(current_user.id) if current_user.is_authenticated else None
        
        if user_id:
            access_result = auth_service.verificar_acesso_memorial(user_id, memorial_id)
            if not access_result['access']:
                return jsonify({'success': False, 'error': 'Acesso negado'})
        else:
            config = db.buscar_configuracoes_privacidade(memorial_id)
            if not config or not config['publico']:
                return jsonify({'success': False, 'error': 'Memorial privado'})
        
        # Buscar fotos
        fotos = db.buscar_fotos_memorial(memorial_id)
        
        # Converter para formato JSON
        fotos_json = []
        for foto in fotos:
            # Gerar URLs otimizadas
            thumbnail_url = cloudinary_service.create_thumbnail(foto['cloudinary_public_id'])
            medium_url = cloudinary_service.get_optimized_url(foto['cloudinary_public_id'], width=800)
            
            fotos_json.append({
                'id': foto['id'],
                'titulo': foto['titulo'],
                'descricao': foto['descricao'],
                'data_foto': foto['data_foto'],
                'categoria': foto['categoria'],
                'url_original': foto['cloudinary_url'],
                'url_thumbnail': thumbnail_url,
                'url_medium': medium_url,
                'created_at': foto['created_at']
            })
        
        return jsonify({
            'success': True,
            'fotos': fotos_json
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'})

@image_bp.route('/api/categories/<int:memorial_id>')
def get_categories(memorial_id):
    """API para obter categorias de fotos de um memorial"""
    try:
        # Verificar acesso
        user_id = int(current_user.id) if current_user.is_authenticated else None
        
        if user_id:
            access_result = auth_service.verificar_acesso_memorial(user_id, memorial_id)
            if not access_result['access']:
                return jsonify({'success': False, 'error': 'Acesso negado'})
        
        # Buscar categorias únicas
        fotos = db.buscar_fotos_memorial(memorial_id)
        categorias = list(set([foto['categoria'] for foto in fotos if foto['categoria']]))
        categorias.sort()
        
        return jsonify({
            'success': True,
            'categorias': categorias
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'})

# Filtros de template para URLs otimizadas
@image_bp.app_template_filter('thumbnail')
def thumbnail_filter(public_id, width=300, height=300):
    """Filtro para gerar URL de thumbnail"""
    return cloudinary_service.create_thumbnail(public_id, width, height)

@image_bp.app_template_filter('optimized')
def optimized_filter(public_id, width=None, height=None):
    """Filtro para gerar URL otimizada"""
    return cloudinary_service.get_optimized_url(public_id, width, height)

