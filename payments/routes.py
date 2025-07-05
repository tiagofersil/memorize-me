from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from database import Database
from mercadopago_service import MercadoPagoService
import json

payments_bp = Blueprint("payments", __name__)
db = Database()
mp_service = MercadoPagoService()

# Definir os planos de pagamento atualizados
PAYMENT_PLANS = {
    "basic": {
        "name": "Plano Básico",
        "description": "Memorial básico com até 20 fotos e QR Code personalizado",
        "amount": 29.00,
        "currency": "BRL"
    },
    "premium": {
        "name": "Plano Premium", 
        "description": "Memorial premium com fotos ilimitadas, vídeos e galeria avançada",
        "amount": 59.00,
        "currency": "BRL"
    },
    "family": {
        "name": "Plano Família",
        "description": "Memorial familiar com recursos ilimitados e árvore genealógica",
        "amount": 99.00,
        "currency": "BRL"
    },
    "pet_basic": {
        "name": "Pet Básico",
        "description": "Memorial especial para seu companheiro de quatro patas",
        "amount": 19.90,
        "currency": "BRL"
    },
    "pet_premium": {
        "name": "Pet Premium",
        "description": "Memorial completo para seu pet com galeria de fotos e vídeos",
        "amount": 29.90,
        "currency": "BRL"
    }
}

@payments_bp.route("/payments")
def payments_home():
    """Redireciona para a página de criação de pagamentos"""
    return redirect(url_for("payments.show_payment_plans"))

@payments_bp.route("/payments/create", methods=["GET"])
def show_payment_plans():
    """
    Exibe a página de seleção de planos (create_payment.html)
    """
    if 'user_id' not in session:
        flash('Você precisa fazer login para acessar esta página.', 'warning')
        return redirect(url_for('accounts.login'))
    
    return render_template("create_payment.html", payment_plans=PAYMENT_PLANS)

@payments_bp.route("/payments/create", methods=["POST"])
def create_payment():
    """
    ROTA PRINCIPAL CORRIGIDA: Processa a seleção do plano e redireciona para o Mercado Pago
    Remove a necessidade de selecionar memorial - vai direto para o pagamento
    """
    if 'user_id' not in session:
        flash('Você precisa fazer login para acessar esta página.', 'warning')
        return redirect(url_for('accounts.login'))
    
    user_id = session['user_id']
    
    # Obter o plano selecionado do formulário
    plan_type = request.form.get('plan_type')
    
    print(f"[DEBUG] Usuário {user_id} selecionou plano: {plan_type}")
    
    # Validar se o plano é válido
    if not plan_type or plan_type not in PAYMENT_PLANS:
        flash('Plano inválido selecionado.', 'error')
        return redirect(url_for('payments.show_payment_plans'))
    
    plan = PAYMENT_PLANS[plan_type]
    amount = plan["amount"]
    
    print(f"[DEBUG] Detalhes do plano: {plan}")
    
    # Buscar informações do usuário
    user = db.get_user_by_username(session['username'])
    
    if not user:
        flash('Erro ao processar pagamento. Usuário não encontrado.', 'danger')
        return redirect(url_for('payments.payments_home'))
    
    # Criar registro de pagamento no banco local (sem memorial_id específico)
    # O memorial será criado APÓS o pagamento ser aprovado
    payment_id = db.create_payment(user_id, None, amount, plan_type)  # memorial_id = None
    
    print(f"[DEBUG] Pagamento criado no banco local: ID {payment_id}")
    
    # Criar preferência no Mercado Pago
    preference_response = mp_service.create_memorial_payment_preference(
        memorial_name=f"{plan['name']} - Memorial Digital",
        amount=amount,
        user_email=user['email'],
        memorial_id=f"user_{user_id}_plan_{plan_type}_payment_{payment_id}"  # Referência única
    )
    
    print(f"[DEBUG] Resposta do Mercado Pago: {preference_response}")
    
    if "error" in preference_response:
        flash(f'Erro ao criar pagamento: {preference_response["error"]}', 'danger')
        return redirect(url_for('payments.show_payment_plans'))
    
    if preference_response["status"] == 201:
        # Obter URL de checkout
        checkout_url = preference_response["response"]["init_point"]
        
        print(f"[DEBUG] URL de checkout criada: {checkout_url}")
        
        # REDIRECIONAMENTO DIRETO PARA O MERCADO PAGO
        return redirect(checkout_url)
    else:
        flash('Erro ao criar preferência de pagamento.', 'danger')
        return redirect(url_for('payments.show_payment_plans'))

@payments_bp.route("/payments/success")
def payment_success():
    """Página de sucesso após pagamento aprovado"""
    payment_id = request.args.get('payment_id')
    status = request.args.get('status')
    external_reference = request.args.get('external_reference')
    
    if payment_id and status == 'approved':
        # Atualizar status do pagamento no banco local
        if external_reference:
            # Extrair informações da referência externa
            # Formato: "user_{user_id}_plan_{plan_type}_payment_{payment_id}"
            try:
                parts = external_reference.split('_')
                if len(parts) >= 6:
                    user_id = parts[1]
                    plan_type_parts = []
                    for i in range(3, len(parts) - 2):
                        plan_type_parts.append(parts[i])
                    plan_type = '_'.join(plan_type_parts)
                    local_payment_id = parts[5]
                    
                    # Atualizar status do pagamento
                    db.update_payment_status(local_payment_id, 'approved')
                    
                    # Ativar plano do usuário (adicionar 1 crédito)
                    db.activate_user_plan(user_id, plan_type, local_payment_id)
                    
                    flash('Pagamento aprovado com sucesso! Seu plano foi ativado.', 'success')
                    print(f"[INFO] Plano {plan_type} ativado para usuário {user_id}")
                else:
                    flash('Pagamento aprovado!', 'success')
            except Exception as e:
                print(f"[ERROR] Erro ao processar referência externa: {e}")
                flash('Pagamento aprovado!', 'success')
        else:
            flash('Pagamento aprovado!', 'success')
    
    return render_template("payment_success.html")

@payments_bp.route("/payments/failure")
def payment_failure():
    """Página de falha no pagamento"""
    flash('Pagamento não foi aprovado. Tente novamente.', 'danger')
    return render_template("payment_failure.html")

@payments_bp.route("/payments/pending")
def payment_pending():
    """Página de pagamento pendente"""
    flash('Pagamento está pendente. Aguarde a confirmação.', 'warning')
    return render_template("payment_pending.html")

@payments_bp.route("/payments/webhook", methods=["POST"])
def payment_webhook():
    """
    Webhook para receber notificações do Mercado Pago
    sobre mudanças no status do pagamento
    """
    try:
        data = request.get_json()
        print(f"[DEBUG] Webhook recebido: {data}")
        
        if data and data.get('type') == 'payment':
            payment_id = data.get('data', {}).get('id')
            
            if payment_id:
                # Buscar informações do pagamento no Mercado Pago
                payment_info = mp_service.get_payment_info(payment_id)
                
                if payment_info.get('status') == 200:
                    payment_data = payment_info['response']
                    status = payment_data.get('status')
                    external_reference = payment_data.get('external_reference')
                    
                    print(f"[DEBUG] Pagamento {payment_id} - Status: {status}, Ref: {external_reference}")
                    
                    # Atualizar status no banco local
                    if external_reference and status == 'approved':
                        try:
                            if len(parts) >= 6:
                                user_id = parts[1]
                                plan_type_parts = []
                                for i in range(3, len(parts) - 2):
                                    plan_type_parts.append(parts[i])
                                plan_type = '_'.join(plan_type_parts)
                                local_payment_id = parts[5]
                                db.activate_user_plan(user_id, plan_type, local_payment_id)
                                
                                print(f"[INFO] Plano {plan_type} ativado para usuário {user_id}")
                        except Exception as e:
                            print(f"[ERROR] Erro ao processar webhook: {e}")
        
        return jsonify({"status": "ok"}), 200
    
    except Exception as e:
        print(f"[ERROR] Erro no webhook: {e}")
        return jsonify({"error": str(e)}), 400



