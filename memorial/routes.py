from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from werkzeug.utils import secure_filename
from database import Database
from mercadopago_service import MercadoPagoService
import os
import qrcode
from io import BytesIO
import base64

memorial_bp = Blueprint("memorial", __name__)
db = Database()
mp_service = MercadoPagoService()

UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'media', 'uploads')
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4", "avi", "mov"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_qr_code(memorial_url):
    """Gera um QR Code para o memorial"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(memorial_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Converter para base64 para salvar no banco
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return img_str

@memorial_bp.route("/memorial")
def memorial_home():
    if "user_id" not in session:
        flash("Você precisa fazer login para acessar esta página.", "warning")
        return redirect(url_for("accounts.login"))
    
    user_id = session["user_id"]
    memorials = db.get_user_memorials(user_id)
    
    # Buscar todos os planos do usuário e seus créditos
    user_plans_credits = db.get_all_user_plans(user_id)
    
    # Definir os 5 planos fixos para exibição
    all_plans = {
        "basic": {"name": "Plano Básico", "credits": user_plans_credits.get("basic", 0)},
        "premium": {"name": "Plano Premium", "credits": user_plans_credits.get("premium", 0)},
        "family": {"name": "Plano Família", "credits": user_plans_credits.get("family", 0)},
        "pet_basic": {"name": "Pet Básico", "credits": user_plans_credits.get("pet_basic", 0)},
        "pet_premium": {"name": "Pet Premium", "credits": user_plans_credits.get("pet_premium", 0)}
    }
    
    return render_template("memorial_home.html", memorials=memorials, all_plans=all_plans)

@memorial_bp.route("/memorial/create", methods=["GET", "POST"])
def create_memorial():
    if "user_id" not in session:
        flash("Você precisa fazer login para acessar esta página.", "warning")
        return redirect(url_for("accounts.login"))
    
    user_id = session["user_id"]
    
    # Determinar qual tipo de memorial o usuário está tentando criar (ex: a partir de um botão no memorial_home)
    # Por enquanto, vamos assumir que o tipo de plano é passado via query param ou form
    # Para simplificar, vamos permitir a criação se houver QUALQUER crédito disponível
    # No futuro, pode-se adicionar um campo oculto no formulário de criação de memorial para o plan_type
    
    # Para a lógica atual, vamos verificar se o usuário tem algum crédito disponível em qualquer plano
    has_credits = False
    user_plans_credits = db.get_all_user_plans(user_id)
    for plan_type, credits in user_plans_credits.items():
        if credits > 0:
            has_credits = True
            break

    if not has_credits:
        flash("Você não possui créditos para criar memoriais. Adquira um plano.", "warning")
        return redirect(url_for("payments.show_payment_plans"))
    
    if request.method == "POST":
        name = request.form["name"]
        biography = request.form.get("biography")
        family_message = request.form.get("family_message")
        birth_date = request.form.get("birth_date")
        death_date = request.form.get("death_date")
        
        # Criar memorial no banco
        memorial_id = db.create_memorial(user_id, name, biography, family_message, birth_date, death_date, None, None)
        
        # Processar upload da foto de perfil
        profile_photo_path = None
        if 'profile_photo' in request.files:
            profile_file = request.files['profile_photo']
            if profile_file and profile_file.filename != "" and allowed_file(profile_file.filename):
                filename = secure_filename(profile_file.filename)
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                profile_photo_path = f"uploads/{memorial_id}_profile_{filename}"
                full_path = os.path.join(UPLOAD_FOLDER, f"{memorial_id}_profile_{filename}")
                profile_file.save(full_path)
        
        # Processar upload da foto de capa
        cover_photo_path = None
        if 'cover_photo' in request.files:
            cover_file = request.files['cover_photo']
            if cover_file and cover_file.filename != "" and allowed_file(cover_file.filename):
                filename = secure_filename(cover_file.filename)
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                cover_photo_path = f"uploads/{memorial_id}_cover_{filename}"
                full_path = os.path.join(UPLOAD_FOLDER, f"{memorial_id}_cover_{filename}")
                cover_file.save(full_path)
        
        # Atualizar memorial com os caminhos das fotos
        db.update_memorial_photos(memorial_id, profile_photo_path, cover_photo_path)
        # Decrementar o crédito do plano usado (precisamos saber qual plano foi usado para criar o memorial)
        # Por enquanto, vamos decrementar o primeiro plano com créditos encontrados
        # Uma solução mais robusta seria associar o memorial a um plan_type específico na criação
        plan_type_to_decrement = None
        for p_type, credits in user_plans_credits.items():
            if credits > 0:
                plan_type_to_decrement = p_type
                break
        
        if plan_type_to_decrement:
            db.decrement_memorial_usage(user_id, plan_type_to_decrement)
        
        # Gerar QR Code
        memorial_url = f"http://localhost:5000/memorial/{memorial_id}"
        qr_code_data = generate_qr_code(memorial_url)
        
        # Processar uploads de fotos da galeria
        print(f"DEBUG: Processando fotos da galeria para memorial_id: {memorial_id}")
        print(f"DEBUG: request.files keys: {list(request.files.keys())}")
        
        for i in range(1, 11):
            photo_field = f"photo_{i}"
            print(f"DEBUG: Verificando campo {photo_field}")
            
            if photo_field in request.files:
                file = request.files[photo_field]
                print(f"DEBUG: Arquivo encontrado para {photo_field}: filename='{file.filename}', content_type='{file.content_type}'")
                
                if file and file.filename != "" and allowed_file(file.filename):
                    try:
                        filename = secure_filename(file.filename)
                        # Criar diretório se não existir
                        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                        # Salvar o caminho correto no banco (relativo à pasta media)
                        file_path = f"uploads/{memorial_id}_{filename}"
                        full_path = os.path.join(UPLOAD_FOLDER, f"{memorial_id}_{filename}")
                        print(f"DEBUG: Salvando arquivo em: {full_path}")
                        
                        # Salvar o arquivo
                        file.save(full_path)
                        print(f"DEBUG: Arquivo salvo fisicamente com sucesso")
                        
                        # Verificar se o arquivo foi salvo
                        if os.path.exists(full_path):
                            print(f"DEBUG: Arquivo confirmado no sistema de arquivos: {full_path}")
                            file_size = os.path.getsize(full_path)
                            print(f"DEBUG: Tamanho do arquivo: {file_size} bytes")
                        else:
                            print(f"ERROR: Arquivo não encontrado após salvamento: {full_path}")
                            continue
                        
                        # Adicionar ao banco de dados
                        print(f"DEBUG: Adicionando foto ao banco: memorial_id={memorial_id}, file_path={file_path}")
                        db.add_memorial_photo(memorial_id, file_path)
                        print(f"DEBUG: Foto {photo_field} salva com sucesso no banco!")
                        
                        # Verificar se foi salvo no banco
                        saved_photos = db.get_memorial_photos(memorial_id)
                        print(f"DEBUG: Total de fotos no banco após inserção: {len(saved_photos)}")
                        
                    except Exception as e:
                        print(f"ERROR: Erro ao processar {photo_field}: {str(e)}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"DEBUG: Arquivo {photo_field} inválido ou vazio - filename: '{file.filename if file else 'None'}'")
            else:
                print(f"DEBUG: Campo {photo_field} não encontrado nos arquivos enviados")
        
        flash("Memorial criado com sucesso!", "success")
        return redirect(url_for("memorial.view_memorial", memorial_id=memorial_id))
    
    # Buscar todos os planos do usuário e seus créditos para exibir na página de criação
    user_plans_credits = db.get_all_user_plans(user_id)
    
    # Filtrar apenas planos com créditos para exibir opções de criação
    available_plans_for_creation = {p_type: credits for p_type, credits in user_plans_credits.items() if credits > 0}
    
    return render_template("edit_memorial.html", available_plans_for_creation=available_plans_for_creation)

@memorial_bp.route("/memorial/<int:memorial_id>")
def view_memorial(memorial_id):
    memorial = db.get_memorial_by_id(memorial_id)
    
    if not memorial:
        flash("Memorial não encontrado.", "danger")
        return redirect(url_for("memorial.memorial_home"))
    
    photos = db.get_memorial_photos(memorial_id)
    shared_photos = []  # Por enquanto vazio, pode ser implementado futuramente
    
    # Buscar todos os planos do usuário e seus créditos se estiver logado
    user_plans_credits = {}
    if "user_id" in session and memorial["user_id"] == session["user_id"]:
        user_plans_credits = db.get_all_user_plans(session["user_id"])
    
    # Gerar QR Code para este memorial
    memorial_url = f"http://localhost:5000/memorial/{memorial_id}"
    qr_code_data = generate_qr_code(memorial_url)
    
    return render_template("view_memorial.html", 
                         memorial=memorial, 
                         photos=photos, 
                         shared_photos=shared_photos,
                         qr_code=qr_code_data,
                         user_plans_credits=user_plans_credits)

@memorial_bp.route("/memorial/edit/<int:memorial_id>", methods=["GET", "POST"])
def edit_memorial(memorial_id):
    print(f"DEBUG: Acessando edit_memorial para memorial_id: {memorial_id}")
    if "user_id" not in session:
        flash("Você precisa fazer login para acessar esta página.", "warning")
        return redirect(url_for("accounts.login"))

    memorial = db.get_memorial_by_id(memorial_id)
    if not memorial or memorial["user_id"] != session["user_id"]:
        flash("Memorial não encontrado ou você não tem permissão para editá-lo.", "danger")
        return redirect(url_for("memorial.memorial_home"))

    if request.method == "POST":
        name = request.form["name"]
        biography = request.form.get("biography")
        family_message = request.form.get("family_message")
        birth_date = request.form.get("birth_date")
        death_date = request.form.get("death_date")
        timeline_events = request.form.get("timeline_events")
        music_embed_url = request.form.get("music_embed_url")
        featured_testimonials = request.form.get("featured_testimonials")
        burial_location = request.form.get("burial_location")
        donation_link = request.form.get("donation_link")
        quotes_values = request.form.get("quotes_values")
        
        # Processar upload da foto de perfil
        profile_photo_path = memorial["profile_photo_path"]  # Manter a foto atual se não houver nova
        if "profile_photo" in request.files:
            profile_file = request.files["profile_photo"]
            if profile_file and profile_file.filename != "" and allowed_file(profile_file.filename):
                filename = secure_filename(profile_file.filename)
                # Criar diretório se não existir
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                # Salvar o caminho correto no banco (relativo à pasta media)
                profile_photo_path = f"uploads/{memorial_id}_profile_{filename}"
                full_path = os.path.join(UPLOAD_FOLDER, f"{memorial_id}_profile_{filename}")
                profile_file.save(full_path)
        # Processar upload da foto de capa
        cover_photo_path = memorial["cover_photo_path"] if memorial and "cover_photo_path" in memorial.keys() else None  # Manter a foto atual se não houver nova
        if "cover_photo" in request.files:
            cover_file = request.files["cover_photo"]
            if cover_file and cover_file.filename != "" and allowed_file(cover_file.filename):
                filename = secure_filename(cover_file.filename)
                # Criar diretório se não existir
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                # Salvar o caminho correto no banco (relativo à pasta media)
                cover_photo_path = f"uploads/{memorial_id}_cover_{filename}"
                full_path = os.path.join(UPLOAD_FOLDER, f"{memorial_id}_cover_{filename}")
                cover_file.save(full_path)
        
        db.update_memorial(memorial_id, name, biography, family_message, birth_date, death_date, profile_photo_path, cover_photo_path, timeline_events, music_embed_url, featured_testimonials, burial_location, donation_link, quotes_values)
        flash("Memorial atualizado com sucesso!", "success")

        # Processar uploads de fotos da galeria
        print(f"DEBUG: Processando fotos da galeria para memorial_id: {memorial_id}")
        print(f"DEBUG: request.files keys: {list(request.files.keys())}")
        
        for i in range(1, 11):
            photo_field = f"photo_{i}"
            print(f"DEBUG: Verificando campo {photo_field}")
            
            if photo_field in request.files:
                file = request.files[photo_field]
                print(f"DEBUG: Arquivo encontrado para {photo_field}: filename='{file.filename}', content_type='{file.content_type}'")
                
                if file and file.filename != "" and allowed_file(file.filename):
                    try:
                        filename = secure_filename(file.filename)
                        # Criar diretório se não existir
                        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                        # Salvar o caminho correto no banco (relativo à pasta media)
                        file_path = f"uploads/{memorial_id}_{filename}"
                        full_path = os.path.join(UPLOAD_FOLDER, f"{memorial_id}_{filename}")
                        print(f"DEBUG: Salvando arquivo em: {full_path}")
                        
                        # Salvar o arquivo
                        file.save(full_path)
                        print(f"DEBUG: Arquivo salvo fisicamente com sucesso")
                        
                        # Verificar se o arquivo foi salvo
                        if os.path.exists(full_path):
                            print(f"DEBUG: Arquivo confirmado no sistema de arquivos: {full_path}")
                            file_size = os.path.getsize(full_path)
                            print(f"DEBUG: Tamanho do arquivo: {file_size} bytes")
                        else:
                            print(f"ERROR: Arquivo não encontrado após salvamento: {full_path}")
                            continue
                        
                        # Adicionar ao banco de dados
                        print(f"DEBUG: Adicionando foto ao banco: memorial_id={memorial_id}, file_path={file_path}")
                        db.add_memorial_photo(memorial_id, file_path)
                        print(f"DEBUG: Foto {photo_field} salva com sucesso no banco!")
                        
                        # Verificar se foi salvo no banco
                        saved_photos = db.get_memorial_photos(memorial_id)
                        print(f"DEBUG: Total de fotos no banco após inserção: {len(saved_photos)}")
                        
                    except Exception as e:
                        print(f"ERROR: Erro ao processar {photo_field}: {str(e)}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"DEBUG: Arquivo {photo_field} inválido ou vazio - filename: '{file.filename if file else 'None'}'")
            else:
                print(f"DEBUG: Campo {photo_field} não encontrado nos arquivos enviados")
        
        return redirect(url_for("memorial.view_memorial", memorial_id=memorial_id))

    photos = db.get_memorial_photos(memorial_id)
    return render_template("edit_memorial.html", memorial=memorial, photos=photos)

@memorial_bp.route("/memorial/generate_memorial_action/<int:memorial_id>", methods=["POST"])
def generate_memorial_action(memorial_id):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Usuário não autenticado."}), 401

    user_id = session["user_id"]
    memorial = db.get_memorial_by_id(memorial_id)

    if not memorial or memorial["user_id"] != user_id:
        return jsonify({"success": False, "message": "Memorial não encontrado ou você não tem permissão."}), 403

    # Verificar se o memorial já foi gerado (e o crédito consumido)
    if memorial["generated"] == 1:
        return jsonify({"success": True, "message": "Memorial já foi gerado. Nenhum crédito foi deduzido."})

    # Lógica para determinar o plan_type do memorial, ou o primeiro plano com créditos disponíveis
    user_plans_credits = db.get_all_user_plans(user_id)
    plan_type_to_decrement = None
    for p_type, credits in user_plans_credits.items():
        if credits > 0:
            plan_type_to_decrement = p_type
            break

    if plan_type_to_decrement:
        if db.get_user_plan_credits(user_id, plan_type_to_decrement) > 0:
            db.decrement_memorial_usage(user_id, plan_type_to_decrement)
            db.mark_memorial_as_generated(memorial_id) # Nova função para marcar como gerado
            return jsonify({"success": True, "message": "Crédito deduzido e memorial marcado como gerado!"})
        else:
            return jsonify({"success": False, "message": "Você não tem créditos suficientes para gerar o memorial."}), 400
    else:
        return jsonify({"success": False, "message": "Nenhum plano com créditos disponível para gerar o memorial."}), 400


@memorial_bp.route("/memorial/generate/<int:memorial_id>")
def generate_memorial(memorial_id):
    """Gera a página pública do memorial com perfil e comentários"""
    memorial = db.get_memorial_by_id(memorial_id)
    
    if not memorial:
        flash("Memorial não encontrado.", "danger")
        return redirect(url_for("memorial.memorial_home"))
    
    photos = db.get_memorial_photos(memorial_id)
    comments = db.get_memorial_comments(memorial_id)
    
    # Gerar QR Code para este memorial
    memorial_url = f"http://localhost:5000/memorial/generate/{memorial_id}"
    qr_code_data = generate_qr_code(memorial_url)
    
    shared_photos = []  # Por enquanto vazio, pode ser implementado futuramente
    
    return render_template("generate_memorial.html", 
                         memorial=memorial, 
                         photos=photos, 
                         shared_photos=shared_photos,
                         comments=comments,
                         qr_code=qr_code_data)

@memorial_bp.route("/memorial/add_comment/<int:memorial_id>", methods=["POST"])
def add_comment(memorial_id):
    """Adiciona um comentário ao memorial"""
    memorial = db.get_memorial_by_id(memorial_id)
    
    if not memorial:
        flash("Memorial não encontrado.", "danger")
        return redirect(url_for("memorial.memorial_home"))
    
    author_name = request.form.get("author_name")
    comment_text = request.form.get("comment_text")
    
    if author_name and comment_text:
        db.add_memorial_comment(memorial_id, author_name, comment_text)
        flash("Comentário adicionado com sucesso!", "success")
    else:
        flash("Por favor, preencha todos os campos.", "warning")
    
    return redirect(url_for("memorial.generate_memorial", memorial_id=memorial_id))

@memorial_bp.route("/memorial/delete_photo/<int:photo_id>", methods=["POST", "DELETE"])
def delete_photo(photo_id):
    if "user_id" not in session:
        flash("Você precisa fazer login para acessar esta página.", "warning")
        return redirect(url_for("accounts.login"))

    photo = db.get_memorial_photo_by_id(photo_id)
    if not photo:
        flash("Foto não encontrada.", "danger")
        return redirect(url_for("memorial.memorial_home"))

    memorial = db.get_memorial_by_id(photo["memorial_id"])
    if not memorial or memorial["user_id"] != session["user_id"]:
        flash("Você não tem permissão para deletar esta foto.", "danger")
        return redirect(url_for("memorial.memorial_home"))

    # Deletar o arquivo
    if os.path.exists(photo["photo_path"]):
        os.remove(photo["photo_path"])

    db.delete_memorial_photo(photo_id)
    flash("Foto deletada com sucesso!", "success")
    return redirect(url_for("memorial.edit_memorial", memorial_id=photo["memorial_id"]))





@memorial_bp.route("/memorial/delete_gallery_photo/<int:photo_id>", methods=["POST"])
def delete_gallery_photo(photo_id):
    """Deleta uma foto da galeria via AJAX"""
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Usuário não autenticado."}), 401

    photo = db.get_memorial_photo_by_id(photo_id)
    if not photo:
        return jsonify({"success": False, "message": "Foto não encontrada."}), 404

    memorial = db.get_memorial_by_id(photo["memorial_id"])
    if not memorial or memorial["user_id"] != session["user_id"]:
        return jsonify({"success": False, "message": "Você não tem permissão para deletar esta foto."}), 403

    try:
        # Deletar o arquivo físico
        full_path = os.path.join(UPLOAD_FOLDER, os.path.basename(photo["photo_path"]))
        if os.path.exists(full_path):
            os.remove(full_path)
            print(f"DEBUG: Arquivo físico removido: {full_path}")
        else:
            print(f"DEBUG: Arquivo físico não encontrado: {full_path}")

        # Deletar do banco de dados
        db.delete_memorial_photo(photo_id)
        print(f"DEBUG: Foto removida do banco de dados: photo_id={photo_id}")
        
        return jsonify({"success": True, "message": "Foto excluída com sucesso!"})
    
    except Exception as e:
        print(f"ERROR: Erro ao excluir foto: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"Erro ao excluir foto: {str(e)}"}), 500

