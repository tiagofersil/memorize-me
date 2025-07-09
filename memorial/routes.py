from dotenv import load_dotenv
load_dotenv()

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from database import Database
from mercadopago_service import MercadoPagoService
from cloudinary_service import CloudinaryService

memorial_bp = Blueprint("memorial", __name__)

# Instanciar o serviço do Mercado Pago
# mp_service = MercadoPagoService()
cloudinary_service = CloudinaryService()

# Função auxiliar para verificar extensões permitidas
def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1][1].lower() in ["png", "jpg", "jpeg", "gif"]

@memorial_bp.before_request
def before_request():
    global mp_service
    mp_service = MercadoPagoService()

@memorial_bp.route("/create_memorial", methods=["GET", "POST"])
@login_required
def create_memorial():
    if request.method == "POST":
        name = request.form["name"]
        birth_date = request.form["birth_date"]
        death_date = request.form["death_date"]
        description = request.form["description"]
        
        # Processar upload da foto
        photo_url = None
        if "photo" in request.files:
            photo = request.files["photo"]
            if photo.filename != "" and allowed_file(photo.filename):
                try:
                    upload_result = cloudinary.uploader.upload(photo)
                    photo_url = upload_result["secure_url"]
                except Exception as e:
                    flash(f"Erro ao fazer upload da foto: {e}", "danger")
                    return render_template("create_memorial.html")

        db = Database(current_app.config["DATABASE_PATH"])
        db.add_memorial(current_user.id, name, birth_date, death_date, description, photo_url)
        flash("Memorial criado com sucesso!", "success")
        return redirect(url_for("memorial.list_memorials"))
    return render_template("create_memorial.html")

@memorial_bp.route("/memorials")
@login_required
def list_memorials():
    db = Database(current_app.config["DATABASE_PATH"])
    memorials = db.get_user_memorials(current_user.id)
    return render_template("list_memorials.html", memorials=memorials)

@memorial_bp.route("/memorial/<int:memorial_id>")
def view_memorial(memorial_id):
    db = Database(current_app.config["DATABASE_PATH"])
    memorial = db.get_memorial(memorial_id)
    if memorial:
        return render_template("view_memorial.html", memorial=memorial)
    flash("Memorial não encontrado.", "danger")
    return redirect(url_for("memorial.list_memorials"))

@memorial_bp.route("/memorial/<int:memorial_id>/edit", methods=["GET", "POST"])
@login_required
def edit_memorial(memorial_id):
    db = Database(current_app.config["DATABASE_PATH"])
    memorial = db.get_memorial(memorial_id)

    if not memorial or memorial["user_id"] != current_user.id:
        flash("Memorial não encontrado ou você não tem permissão para editá-lo.", "danger")
        return redirect(url_for("memorial.list_memorials"))

    if request.method == "POST":
        name = request.form["name"]
        birth_date = request.form["birth_date"]
        death_date = request.form["death_date"]
        description = request.form["description"]
        
        photo_url = memorial["photo_url"]
        if "photo" in request.files:
            photo = request.files["photo"]
            if photo.filename != "" and allowed_file(photo.filename):
                try:
                    upload_result = cloudinary.uploader.upload(photo)
                    photo_url = upload_result["secure_url"]
                except Exception as e:
                    flash(f"Erro ao fazer upload da foto: {e}", "danger")
                    return render_template("edit_memorial.html", memorial=memorial)

        db.update_memorial(memorial_id, name, birth_date, death_date, description, photo_url)
        flash("Memorial atualizado com sucesso!", "success")
        return redirect(url_for("memorial.view_memorial", memorial_id=memorial_id))

    return render_template("edit_memorial.html", memorial=memorial)

@memorial_bp.route("/memorial/<int:memorial_id>/delete", methods=["POST"])
@login_required
def delete_memorial(memorial_id):
    db = Database(current_app.config["DATABASE_PATH"])
    memorial = db.get_memorial(memorial_id)

    if not memorial or memorial["user_id"] != current_user.id:
        flash("Memorial não encontrado ou você não tem permissão para excluí-lo.", "danger")
        return redirect(url_for("memorial.list_memorials"))

    db.delete_memorial(memorial_id)
    flash("Memorial excluído com sucesso!", "success")
    return redirect(url_for("memorial.list_memorials"))

@memorial_bp.route("/memorial/<int:memorial_id>/add_tribute", methods=["GET", "POST"])
@login_required
def add_tribute(memorial_id):
    db = Database(current_app.config["DATABASE_PATH"])
    memorial = db.get_memorial(memorial_id)

    if not memorial:
        flash("Memorial não encontrado.", "danger")
        return redirect(url_for("memorial.list_memorials"))

    if request.method == "POST":
        message = request.form["message"]
        tribute_type = request.form["tribute_type"]
        db.add_tribute(memorial_id, current_user.id, message, tribute_type)
        flash("Homenagem adicionada com sucesso!", "success")
        return redirect(url_for("memorial.view_memorial", memorial_id=memorial_id))

    return render_template("add_tribute.html", memorial=memorial)

@memorial_bp.route("/memorial/<int:memorial_id>/tributes")
def list_tributes(memorial_id):
    db = Database(current_app.config["DATABASE_PATH"])
    memorial = db.get_memorial(memorial_id)
    if not memorial:
        flash("Memorial não encontrado.", "danger")
        return redirect(url_for("memorial.list_memorials"))
    
    tributes = db.get_memorial_tributes(memorial_id)
    return render_template("list_tributes.html", memorial=memorial, tributes=tributes)

@memorial_bp.route("/tribute/<int:tribute_id>/delete", methods=["POST"])
@login_required
def delete_tribute(tribute_id):
    db = Database(current_app.config["DATABASE_PATH"])
    tribute = db.get_tribute(tribute_id)

    if not tribute or tribute["user_id"] != current_user.id:
        flash("Homenagem não encontrada ou você não tem permissão para excluí-la.", "danger")
        return redirect(url_for("memorial.list_memorials"))

    db.delete_tribute(tribute_id)
    flash("Homenagem excluída com sucesso!", "success")
    return redirect(url_for("memorial.view_memorial", memorial_id=tribute["memorial_id"]))


