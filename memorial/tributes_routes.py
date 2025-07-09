from flask import Blueprint, request, jsonify, session, flash, redirect, url_for
from database_tributes import TributesDatabase
import json
from datetime import datetime

tributes_bp = Blueprint("tributes", __name__)
tributes_db = TributesDatabase()

@tributes_bp.route("/memorial/tribute/add", methods=["POST"])
def add_tribute():
    """Adiciona uma nova homenagem (vela ou flor)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400
        
        memorial_id = data.get('memorial_id')
        tribute_type = data.get('type')
        duration = data.get('duration')
        message = data.get('message', '').strip()
        user_name = data.get('user_name', '').strip()
        flower_type = data.get('flower_type', 'rose')  # padrão: rosa
        
        # Validações
        if not memorial_id or not tribute_type or not duration or not user_name:
            return jsonify({"error": "Campos obrigatórios não preenchidos"}), 400
        
        if tribute_type not in ['candle', 'flower']:
            return jsonify({"error": "Tipo de homenagem inválido"}), 400
        
        if duration not in ['12h', '1d', '7d', 'forever']:
            return jsonify({"error": "Duração inválida"}), 400
        
        if tribute_type == 'flower' and flower_type not in ['rose', 'lotus']:
            flower_type = 'rose'  # fallback para rosa
        
        # Verificar se o memorial existe
        memorial = tributes_db.get_memorial_by_id(memorial_id)
        if not memorial:
            return jsonify({"error": "Memorial não encontrado"}), 404
        
        # Adicionar homenagem
        tribute = tributes_db.add_tribute(
            memorial_id=memorial_id,
            user_name=user_name,
            tribute_type=tribute_type,
            duration=duration,
            message=message if message else None,
            flower_type=flower_type if tribute_type == 'flower' else None
        )
        
        if tribute:
            return jsonify({
                "success": True,
                "message": "Homenagem adicionada com sucesso",
                "tribute": tribute
            }), 201
        else:
            return jsonify({"error": "Erro ao adicionar homenagem"}), 500
            
    except Exception as e:
        print(f"Erro ao adicionar homenagem: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@tributes_bp.route("/memorial/tributes/<int:memorial_id>", methods=["GET"])
def get_memorial_tributes(memorial_id):
    """Busca todas as homenagens ativas de um memorial"""
    try:
        include_expired = request.args.get('include_expired', 'false').lower() == 'true'
        
        tributes = tributes_db.get_memorial_tributes(memorial_id, include_expired=include_expired)
        stats = tributes_db.get_tribute_stats(memorial_id)
        
        return jsonify({
            "success": True,
            "tributes": tributes,
            "stats": stats
        }), 200
        
    except Exception as e:
        print(f"Erro ao buscar homenagens: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@tributes_bp.route("/memorial/tribute/<int:tribute_id>", methods=["DELETE"])
def delete_tribute(tribute_id):
    """Remove uma homenagem"""
    try:
        data = request.get_json() or {}
        user_name = data.get('user_name')
        
        # Se não forneceu user_name, tentar obter da sessão
        if not user_name and 'username' in session:
            user_name = session['username']
        
        success = tributes_db.delete_tribute(tribute_id, user_name)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Homenagem removida com sucesso"
            }), 200
        else:
            return jsonify({"error": "Homenagem não encontrada ou sem permissão"}), 404
            
    except Exception as e:
        print(f"Erro ao remover homenagem: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@tributes_bp.route("/memorial/tributes/cleanup", methods=["POST"])
def cleanup_expired_tributes():
    """Remove homenagens expiradas (endpoint administrativo)"""
    try:
        # Verificar se é admin (implementar conforme necessário)
        # Por enquanto, permitir qualquer usuário logado
        if 'user_id' not in session:
            return jsonify({"error": "Acesso negado"}), 403
        
        affected_rows = tributes_db.cleanup_expired_tributes()
        
        return jsonify({
            "success": True,
            "message": f"{affected_rows} homenagens expiradas foram removidas"
        }), 200
        
    except Exception as e:
        print(f"Erro na limpeza: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@tributes_bp.route("/memorial/tributes/stats/<int:memorial_id>", methods=["GET"])
def get_tribute_stats(memorial_id):
    """Obtém estatísticas das homenagens de um memorial"""
    try:
        stats = tributes_db.get_tribute_stats(memorial_id)
        
        return jsonify({
            "success": True,
            "stats": stats
        }), 200
        
    except Exception as e:
        print(f"Erro ao obter estatísticas: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@tributes_bp.route("/memorial/tributes/user/<user_name>", methods=["GET"])
def get_user_tributes(user_name):
    """Busca todas as homenagens de um usuário"""
    try:
        limit = int(request.args.get('limit', 50))
        tributes = tributes_db.get_user_tributes(user_name, limit)
        
        return jsonify({
            "success": True,
            "tributes": tributes
        }), 200
        
    except Exception as e:
        print(f"Erro ao buscar homenagens do usuário: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@tributes_bp.route("/memorial/tributes/recent", methods=["GET"])
def get_recent_tributes():
    """Busca homenagens recentes de todos os memoriais"""
    try:
        limit = int(request.args.get('limit', 20))
        tributes = tributes_db.get_recent_tributes(limit)
        
        return jsonify({
            "success": True,
            "tributes": tributes
        }), 200
        
    except Exception as e:
        print(f"Erro ao buscar homenagens recentes: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@tributes_bp.route("/memorial/tribute/flower-type", methods=["POST"])
def set_flower_type():
    """Define o tipo de flor para uma homenagem"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400
        
        flower_type = data.get('flower_type', 'rose')
        
        if flower_type not in ['rose', 'lotus']:
            return jsonify({"error": "Tipo de flor inválido"}), 400
        
        # Armazenar na sessão temporariamente
        session['selected_flower_type'] = flower_type
        
        return jsonify({
            "success": True,
            "flower_type": flower_type
        }), 200
        
    except Exception as e:
        print(f"Erro ao definir tipo de flor: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

