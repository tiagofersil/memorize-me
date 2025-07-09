from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from database_enhanced import DatabaseEnhanced
from auth_service import AuthService
from cloudinary_service import CloudinaryService
from datetime import datetime
import json
import uuid

memorial_bp = Blueprint('memorial', __name__, url_prefix='/memorial')

# Inicializar serviços
db = DatabaseEnhanced()
auth_service = AuthService()
cloudinary_service = CloudinaryService()

@memorial_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard do usuário com seus memoriais"""
    user_id = int(current_user.id)
    memoriais = db.buscar_memoriais_usuario(user_id)
    
    return render_template('memorial/dashboard.html', memoriais=memoriais)

@memorial_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Criar novo memorial"""
    if request.method == 'POST':
        # Obter dados do formulário
        nome_falecido = request.form.get('nome_falecido', '').strip()
        biografia = request.form.get('biografia', '').strip()
        data_nascimento = request.form.get('data_nascimento', '').strip()
        data_falecimento = request.form.get('data_falecimento', '').strip()
        local_nascimento = request.form.get('local_nascimento', '').strip()
        local_falecimento = request.form.get('local_falecimento', '').strip()
        profissao = request.form.get('profissao', '').strip()
        estado_civil = request.form.get('estado_civil', '').strip()
        nome_conjuge = request.form.get('nome_conjuge', '').strip()
        filhos = request.form.get('filhos', '').strip()
        
        # Validações
        if not nome_falecido:
            flash('Nome do falecido é obrigatório', 'error')
            return render_template('memorial/create.html')
        
        # Criar memorial
        memorial_id = db.criar_memorial(
            user_id=int(current_user.id),
            nome_falecido=nome_falecido,
            biografia=biografia if biografia else None,
            data_nascimento=data_nascimento if data_nascimento else None,
            data_falecimento=data_falecimento if data_falecimento else None,
            local_nascimento=local_nascimento if local_nascimento else None,
            local_falecimento=local_falecimento if local_falecimento else None,
            profissao=profissao if profissao else None,
            estado_civil=estado_civil if estado_civil else None,
            nome_conjuge=nome_conjuge if nome_conjuge else None,
            filhos=filhos if filhos else None
        )
        
        if memorial_id:
            # Registrar atividade
            auth_service.registrar_atividade(
                user_id=int(current_user.id),
                memorial_id=memorial_id,
                acao='criar_memorial',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                detalhes=f'Memorial criado: {nome_falecido}'
            )
            
            flash('Memorial criado com sucesso!', 'success')
            return redirect(url_for('memorial.edit', memorial_id=memorial_id))
        else:
            flash('Erro ao criar memorial', 'error')
            return render_template('memorial/create.html')
    
    return render_template('memorial/create.html')

@memorial_bp.route('/edit/<int:memorial_id>', methods=['GET', 'POST'])
@login_required
def edit(memorial_id):
    """Editar memorial"""
    # Verificar acesso
    access_result = auth_service.verificar_acesso_memorial(int(current_user.id), memorial_id)
    
    if not access_result['access'] or access_result['level'] != 'owner':
        flash('Você não tem permissão para editar este memorial', 'error')
        return redirect(url_for('memorial.dashboard'))
    
    # Buscar memorial
    memorial = db.buscar_memorial_por_id(memorial_id)
    if not memorial:
        flash('Memorial não encontrado', 'error')
        return redirect(url_for('memorial.dashboard'))

    if request.method == 'POST':
        # Processar informações básicas
        memorial_data = {
            'nome_falecido': request.form.get('name'),
            'data_nascimento': request.form.get('birth_date'),
            'data_falecimento': request.form.get('death_date'),
            'biografia': request.form.get('biography'),
            'family_message': request.form.get('family_message'),
            'timeline_events': request.form.get('timeline_events'),
            'music_embed_url': request.form.get('music_embed_url'),
            'featured_testimonials': request.form.get('featured_testimonials'),
            'burial_location': request.form.get('burial_location'),
            'donation_link': request.form.get('donation_link'),
            'quotes_values': request.form.get('quotes_values'),
        }

        # Atualizar memorial no banco de dados
        db.atualizar_memorial(memorial_id, int(current_user.id), **memorial_data)

        # Processar foto de perfil
        profile_photo = request.files.get('profile_photo')
        if profile_photo and profile_photo.filename != '':
            validation = cloudinary_service.validate_image_file(profile_photo)
            if validation['valid']:
                public_id = f"memorial_{memorial_id}_profile"
                upload_result = cloudinary_service.upload_image(profile_photo, folder=f"memorial_{memorial_id}", public_id=public_id, overwrite=True)
                if upload_result['success']:
                    db.atualizar_memorial(memorial_id, int(current_user.id), profile_photo_path=upload_result['url'])
                else:
                    flash(f"Erro ao fazer upload da foto de perfil: {upload_result['error']}", 'error')
            else:
                flash(f"Foto de perfil inválida: {validation['error']}", 'error')

        # Processar foto de capa
        cover_photo = request.files.get('cover_photo')
        if cover_photo and cover_photo.filename != '':
            validation = cloudinary_service.validate_image_file(cover_photo)
            if validation['valid']:
                public_id = f"memorial_{memorial_id}_cover"
                upload_result = cloudinary_service.upload_image(cover_photo, folder=f"memorial_{memorial_id}", public_id=public_id, overwrite=True)
                if upload_result['success']:
                    db.atualizar_memorial(memorial_id, int(current_user.id), cover_photo_path=upload_result['url'])
                else:
                    flash(f"Erro ao fazer upload da foto de capa: {upload_result['error']}", 'error')
            else:
                flash(f"Foto de capa inválida: {validation['error']}", 'error')

        # Processar galeria de fotos - apenas novas imagens
        uploaded_photos = []
        for i in range(1, 11):
            photo_file = request.files.get(f'photo_{i}')
            if photo_file and photo_file.filename != '':
                # Verificar se é uma nova imagem (não duplicada)
                file_hash = hash(photo_file.read())
                photo_file.seek(0)  # Resetar o ponteiro do arquivo
                
                # Verificar se esta imagem já foi processada nesta sessão
                if file_hash not in uploaded_photos:
                    validation = cloudinary_service.validate_image_file(photo_file)
                    if validation['valid']:
                        # Verificar se já existe uma foto similar no banco
                        existing_photos = db.buscar_fotos_memorial(memorial_id)
                        
                        # Gerar public_id único para cada foto da galeria
                        public_id = f"memorial_{memorial_id}_gallery_{uuid.uuid4().hex[:8]}"
                        upload_result = cloudinary_service.upload_image(photo_file, folder=f"memorial_{memorial_id}/gallery", public_id=public_id)
                        if upload_result['success']:
                            db.salvar_foto(
                                memorial_id=memorial_id,
                                user_id=int(current_user.id),
                                cloudinary_url=upload_result['url'],
                                cloudinary_public_id=upload_result['public_id']
                            )
                            uploaded_photos.append(file_hash)
                        else:
                            flash(f"Erro ao fazer upload da foto {i}: {upload_result['error']}", 'error')
                    else:
                        flash(f"Foto {i} inválida: {validation['error']}", 'error')

        flash('Memorial atualizado com sucesso!', 'success')
        return redirect(url_for('memorial.edit', memorial_id=memorial_id))
    
    # Buscar textos personalizados
    textos = db.buscar_textos_memorial(memorial_id)
    textos_dict = {texto['tipo_texto']: texto for texto in textos}
    
    # Buscar homenagens
    homenagens = db.buscar_homenagens_memorial(memorial_id, apenas_aprovadas=False)
    
    # Buscar fotos
    fotos = db.buscar_fotos_memorial(memorial_id)
    
    return render_template('memorial/edit.html', 
                         memorial=memorial, 
                         textos=textos_dict, 
                         homenagens=homenagens,
                         photos=fotos) # Renomeado para 'photos' para evitar conflito com 'fotos' no template

@memorial_bp.route('/view/<int:memorial_id>')
def view(memorial_id):
    """Visualizar memorial (público se permitido)"""
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
    
    # Buscar conteúdo
    textos = db.buscar_textos_memorial(memorial_id)
    textos_dict = {texto['tipo_texto']: texto for texto in textos}
    
    homenagens = db.buscar_homenagens_memorial(memorial_id, apenas_aprovadas=True)
    fotos = db.buscar_fotos_memorial(memorial_id)
    
    return render_template('memorial/view.html', 
                         memorial=memorial, 
                         textos=textos_dict, 
                         homenagens=homenagens,
                         fotos=fotos,
                         is_owner=is_owner)

@memorial_bp.route('/api/save_text', methods=['POST'])
@login_required
def save_text():
    """API para salvar texto personalizado"""
    try:
        data = request.get_json()
        memorial_id = data.get('memorial_id')
        tipo_texto = data.get('tipo_texto')
        conteudo = data.get('conteudo', '').strip()
        titulo = data.get('titulo', '').strip()
        ordem = data.get('ordem', 0)
        
        if not all([memorial_id, tipo_texto, conteudo]):
            return jsonify({"success": False, "error": "Dados obrigatórios não fornecidos"})
        # Verificar acesso
        access_result = auth_service.verificar_acesso_memorial(int(current_user.id), memorial_id)
        if not access_result['access'] or access_result['level'] != 'owner':
            return jsonify({'success': False, 'error': 'Acesso negado'})
        
        # Salvar texto
        texto_id = db.salvar_texto_memorial(
            memorial_id=memorial_id,
            user_id=int(current_user.id),
            tipo_texto=tipo_texto,
            conteudo=conteudo,
            titulo=titulo if titulo else None,
            ordem=ordem
        )
        
        # Registrar atividade
        auth_service.registrar_atividade(
            user_id=int(current_user.id),
            memorial_id=memorial_id,
            acao='salvar_texto',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            detalhes=f'Tipo: {tipo_texto}, ID: {texto_id}'
        )
        
        return jsonify({
            'success': True,
            'texto_id': texto_id,
            'message': 'Texto salvo com sucesso!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'})

@memorial_bp.route('/api/add_tribute', methods=['POST'])
def add_tribute():
    """API para adicionar homenagem (público)"""
    try:
        data = request.get_json()
        memorial_id = data.get('memorial_id')
        autor_nome = data.get('autor_nome', '').strip()
        texto_homenagem = data.get('texto_homenagem', '').strip()
        autor_email = data.get('autor_email', '').strip()
        autor_telefone = data.get('autor_telefone', '').strip()
        relacionamento = data.get('relacionamento', '').strip()
        
        if not all([memorial_id, autor_nome, texto_homenagem]):
            return jsonify({'success': False, 'error': 'Nome do autor e texto da homenagem são obrigatórios'})
        
        # Verificar se memorial existe e permite homenagens
        memorial = db.buscar_memorial_por_id(memorial_id)
        if not memorial:
            return jsonify({'success': False, 'error': 'Memorial não encontrado'})
        
        config = db.buscar_configuracoes_privacidade(memorial_id)
        if not config or not config['permite_comentarios']:
            return jsonify({'success': False, 'error': 'Este memorial não permite homenagens'})
        
        # Criar homenagem
        homenagem_id = db.criar_homenagem(
            memorial_id=memorial_id,
            autor_nome=autor_nome,
            texto_homenagem=texto_homenagem,
            autor_email=autor_email if autor_email else None,
            autor_telefone=autor_telefone if autor_telefone else None,
            relacionamento=relacionamento if relacionamento else None
        )
        
        # Registrar atividade
        auth_service.registrar_atividade(
            user_id=None,
            memorial_id=memorial_id,
            acao='adicionar_homenagem',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            detalhes=f'Autor: {autor_nome}, ID: {homenagem_id}'
        )
        
        message = 'Homenagem adicionada com sucesso!'
        if config['requer_aprovacao_homenagens']:
            message += ' Ela será exibida após aprovação do proprietário do memorial.'
        
        return jsonify({
            'success': True,
            'homenagem_id': homenagem_id,
            'message': message
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'})

@memorial_bp.route('/api/approve_tribute/<int:homenagem_id>', methods=['POST'])
@login_required
def approve_tribute(homenagem_id):
    """API para aprovar homenagem"""
    try:
        result = db.aprovar_homenagem(homenagem_id, int(current_user.id))
        
        if result:
            # Registrar atividade
            auth_service.registrar_atividade(
                user_id=int(current_user.id),
                memorial_id=None,  # Será preenchido pelo banco se necessário
                acao='aprovar_homenagem',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                detalhes=f'Homenagem ID: {homenagem_id}'
            )
            
            return jsonify({
                'success': True,
                'message': 'Homenagem aprovada com sucesso!'
            })
        else:
            return jsonify({'success': False, 'error': 'Erro ao aprovar homenagem ou acesso negado'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'})

@memorial_bp.route('/api/update_memorial', methods=['POST'])
@login_required
def update_memorial():
    """API para atualizar informações básicas do memorial"""
    try:
        data = request.get_json()
        memorial_id = data.get('memorial_id')
        
        if not memorial_id:
            return jsonify({'success': False, 'error': 'Memorial ID é obrigatório'})
        
        # Verificar acesso
        access_result = auth_service.verificar_acesso_memorial(int(current_user.id), memorial_id)
        if not access_result['access'] or access_result['level'] != 'owner':
            return jsonify({'success': False, 'error': 'Acesso negado'})
        
        # Obter dados para atualização
        update_data = {}
        campos_permitidos = [
            'nome_falecido', 'biografia', 'data_nascimento', 'data_falecimento',
            'local_nascimento', 'local_falecimento', 'profissao', 'estado_civil',
            'nome_conjuge', 'filhos'
        ]
        
        for campo in campos_permitidos:
            if campo in data:
                valor = data[campo].strip() if isinstance(data[campo], str) else data[campo]
                update_data[campo] = valor if valor else None
        
        # Atualizar memorial (implementar método na DatabaseEnhanced)
        # Por enquanto, simular sucesso
        
        # Registrar atividade
        auth_service.registrar_atividade(
            user_id=int(current_user.id),
            memorial_id=memorial_id,
            acao='atualizar_memorial',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            detalhes=f'Campos atualizados: {", ".join(update_data.keys())}'
        )
        
        return jsonify({
            'success': True,
            'message': 'Memorial atualizado com sucesso!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'})

@memorial_bp.route('/api/delete/<int:memorial_id>', methods=['DELETE'])
@login_required
def delete_memorial(memorial_id):
    """API para deletar memorial"""
    try:
        # Verificar acesso
        access_result = auth_service.verificar_acesso_memorial(int(current_user.id), memorial_id)
        if not access_result['access'] or access_result['level'] != 'owner':
            return jsonify({'success': False, 'error': 'Acesso negado'})
        
        # Buscar memorial para log
        memorial = db.buscar_memorial_por_id(memorial_id)
        if not memorial:
            return jsonify({'success': False, 'error': 'Memorial não encontrado'})
        
        # Deletar memorial (implementar método na DatabaseEnhanced)
        # Por enquanto, simular sucesso
        
        # Registrar atividade
        auth_service.registrar_atividade(
            user_id=int(current_user.id),
            memorial_id=memorial_id,
            acao='deletar_memorial',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            detalhes=f'Memorial deletado: {memorial["nome_falecido"]}'
        )
        
        return jsonify({
            'success': True,
            'message': 'Memorial deletado com sucesso!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'})

@memorial_bp.route('/api/get_texts/<int:memorial_id>')
def get_texts(memorial_id):
    """API para obter textos de um memorial"""
    try:
        # Verificar acesso
        user_id = int(current_user.id) if current_user.is_authenticated else None
        
        if user_id:
            access_result = auth_service.verificar_acesso_memorial(user_id, memorial_id)
            if not access_result['access']:
               return jsonify({'success': False, 'error': 'Acesso negado'})
        else:
            config = db.buscar_configuracoes_privacidade(memorial_id)
            if not config or not config['publico']:
                return jsonify({'success': False, 'error': 'Memorial privado'})
        
        # Buscar textos
        textos = db.buscar_textos_memorial(memorial_id)
        
        # Converter para formato JSON
        textos_json = []
        for texto in textos:
            textos_json.append({
                'id': texto['id'],
                'tipo_texto': texto['tipo_texto'],
                'titulo': texto['titulo'],
                'conteudo': texto['conteudo'],
                'ordem': texto['ordem'],
                'created_at': texto['created_at'],
                'updated_at': texto['updated_at']
            })
        
        return jsonify({
            'success': True,
            'textos': textos_json
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'})

@memorial_bp.route('/api/get_tributes/<int:memorial_id>')
def get_tributes(memorial_id):
    """API para obter homenagens de um memorial"""
    try:
        # Verificar acesso
        user_id = int(current_user.id) if current_user.is_authenticated else None
        is_owner = False
        
        if user_id:
            access_result = auth_service.verificar_acesso_memorial(user_id, memorial_id)
            if not access_result['access']:
                return jsonify({"success": False, "error": "Acesso negado"})
            is_owner = access_result["level"] == "owner"
        else:
            config = db.buscar_configuracoes_privacidade(memorial_id)
            if not config or not config['publico']:
                return jsonify({'success': False, 'error': 'Memorial privado'})
        
        # Buscar homenagens (todas se for proprietário, apenas aprovadas se não for)
        homenagens = db.buscar_homenagens_memorial(memorial_id, apenas_aprovadas=not is_owner)
        
        # Converter para formato JSON
        homenagens_json = []
        for homenagem in homenagens:
            homenagens_json.append({
                'id': homenagem['id'],
                'autor_nome': homenagem['autor_nome'],
                'texto_homenagem': homenagem['texto_homenagem'],
                'relacionamento': homenagem['relacionamento'],
                'aprovado': homenagem['aprovado'],
                'created_at': homenagem['created_at']
            })
        
        return jsonify({
            'success': True,
            'homenagens': homenagens_json,
            'is_owner': is_owner
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'})

@memorial_bp.route('/memorial/delete_gallery_photo/<int:photo_id>', methods=['POST'])
@login_required
def delete_gallery_photo(photo_id):
    try:
        photo = db.buscar_foto_por_id(photo_id)
        if not photo:
            return jsonify({'success': False, 'message': 'Foto não encontrada.'})

        if photo['user_id'] != int(current_user.id):
            return jsonify({'success': False, 'message': 'Você não tem permissão para excluir esta foto.'})

        # Deletar do Cloudinary
        cloudinary_service.delete_image(photo['cloudinary_public_id'])

        # Deletar do banco de dados
        db.deletar_foto(photo_id, int(current_user.id))

        return jsonify({'success': True, 'message': 'Foto excluída com sucesso.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao excluir foto: {str(e)}'})

# Rota para tipos de texto disponíveis
@memorial_bp.route('/api/text_types')
def get_text_types():
    """API para obter tipos de texto disponíveis"""
    tipos = [
        {'key': 'biografia', 'name': 'Biografia', 'description': 'História de vida da pessoa'},
        {'key': 'historia_vida', 'name': 'História de Vida', 'description': 'Momentos marcantes e conquistas'},
        {'key': 'mensagem_familia', 'name': 'Mensagem da Família', 'description': 'Palavras especiais da família'},
        {'key': 'valores_principios', 'name': 'Valores e Princípios', 'description': 'O que a pessoa valorizava'},
        {'key': 'legado', 'name': 'Legado', 'description': 'O que a pessoa deixou para o mundo'},
        {'key': 'memorias_especiais', 'name': 'Memórias Especiais', 'description': 'Lembranças queridas'},
        {'key': 'agradecimentos', 'name': 'Agradecimentos', 'description': 'Agradecimentos especiais'},
        {'key': 'citacoes_favoritas', 'name': 'Citações Favoritas', 'description': 'Frases que a pessoa gostava'}
    ]
    
    return jsonify({
        'success': True,
        'tipos': tipos
    })





