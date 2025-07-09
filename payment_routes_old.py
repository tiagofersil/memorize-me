from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from mercadopago_service import get_mercadopago_service

# Carregar variáveis de ambiente
load_dotenv()

# Criar blueprint
payments_bp = Blueprint('payments', __name__, url_prefix='/payments')

@payments_bp.route('/create-payment', methods=['GET', 'POST'])
def create_payment():
    """Página de seleção de planos e criação de pagamento"""
    if request.method == 'POST':
        plan_type = request.form.get('plan_type')
        
        # Definir dados dos planos
        plans = {
            'basic': {
                'name': 'Plano Básico',
                'price': 29.00,
                'description': 'Ideal para memoriais simples e pessoais'
            },
            'premium': {
                'name': 'Plano Premium', 
                'price': 59.00,
                'description': 'Perfeito para famílias que querem mais recursos'
            },
            'family': {
                'name': 'Plano Família',
                'price': 99.00,
                'description': 'Solução completa para grandes famílias'
            },
            'pet_basic': {
                'name': 'Pet Básico',
                'price': 19.90,
                'description': 'Memorial especial para seu companheiro de quatro patas'
            },
            'pet_premium': {
                'name': 'Pet Premium',
                'price': 29.90,
                'description': 'Memorial completo para seu pet com galeria de fotos e vídeos'
            }
        }
        
        if plan_type in plans:
            # Salvar plano selecionado na sessão
            session['selected_plan'] = plan_type
            session['plan_data'] = plans[plan_type]
            
            # Redirecionar para checkout
            return redirect(url_for('payments.checkout', plan=plan_type))
        else:
            flash('Plano inválido selecionado', 'error')
    
    return render_template('create_payment.html')

@payments_bp.route('/checkout')
def checkout():
    """Página de checkout transparente"""
    plan_type = request.args.get('plan') or session.get('selected_plan')
    
    if not plan_type:
        flash('Nenhum plano selecionado', 'error')
        return redirect(url_for('payments.create_payment'))
    
    # Obter chave pública do Mercado Pago
    public_key = os.getenv('PUBLIC_KEY')
    
    return render_template('checkout.html', 
                         plan_type=plan_type,
                         public_key=public_key)

@payments_bp.route('/api/process_payment', methods=['POST'])
def process_payment():
    """API para processar pagamentos via Mercado Pago"""
    try:
        payment_data = request.get_json()
        mp_service = get_mercadopago_service()
        
        if not mp_service:
            return jsonify({"error": "Serviço de pagamento indisponível"}), 500
        
        # Adicionar dados do plano selecionado
        payment_data['plan_type'] = session.get('selected_plan')
        payment_data['user_id'] = current_user.id if current_user.is_authenticated else None
        preference_data = {
            "items": [
                {
                    "title": payment_data.get('description', 'Memorial Online'),
                    "quantity": 1,
                    "unit_price": payment_data.get('transaction_amount')
                }
            ],
            "payer": payment_data.get('payer', {}),
            "payment_methods": {
                "excluded_payment_methods": [],
                "excluded_payment_types": [],
                "installments": payment_data.get('installments', 1)
            },
            "back_urls": {
                "success": request.url_root + "payments/success",
                "failure": request.url_root + "payments/failure", 
                "pending": request.url_root + "payments/pending"
            },
            "auto_return": "approved"
        }
        
        # Se for cartão de crédito/débito
        if payment_data.get('token'):
            payment_request = {
                "transaction_amount": payment_data.get('transaction_amount'),
                "token": payment_data.get('token'),
                "description": payment_data.get('description'),
                "installments": payment_data.get('installments', 1),
                "payment_method_id": payment_data.get('payment_method_id'),
                "issuer_id": payment_data.get('issuer_id'),
                "payer": payment_data.get('payer')
            }
            
            payment_response = sdk.payment().create(payment_request)
            payment = payment_response["response"]
            
        # Se for PIX
        elif payment_data.get('payment_method_id') == 'pix':
            payment_request = {
                "transaction_amount": payment_data.get('transaction_amount'),
                "description": payment_data.get('description'),
                "payment_method_id": "pix",
                "payer": payment_data.get('payer')
            }
            
            payment_response = sdk.payment().create(payment_request)
            payment = payment_response["response"]
            
        # Se for boleto
        elif payment_data.get('payment_method_id') in ['bolbradesco', 'boletofacil']:
            payment_request = {
                "transaction_amount": payment_data.get('transaction_amount'),
                "description": payment_data.get('description'),
                "payment_method_id": payment_data.get('payment_method_id'),
                "payer": payment_data.get('payer')
            }
            
            payment_response = sdk.payment().create(payment_request)
            payment = payment_response["response"]
        
        else:
            return jsonify({"error": "Método de pagamento não suportado"}), 400
        
        # Salvar dados do pagamento na sessão
        session['payment_id'] = payment.get('id')
        session['payment_status'] = payment.get('status')
        
        # Salvar no banco de dados (implementar conforme necessário)
        save_payment_to_database(payment, session.get('selected_plan'))
        
        return jsonify(payment)
        
    except Exception as e:
        print(f"Erro ao processar pagamento: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@payments_bp.route('/shipping-address')
def shipping_address():
    """Página de endereço de entrega"""
    payment_id = request.args.get('payment_id') or session.get('payment_id')
    
    if not payment_id:
        flash('Pagamento não encontrado', 'error')
        return redirect(url_for('payments.create_payment'))
    
    return render_template('shipping_address.html', payment_id=payment_id)

@payments_bp.route('/save-shipping-address', methods=['POST'])
def save_shipping_address():
    """Salvar endereço de entrega"""
    try:
        # Obter dados do formulário
        shipping_data = {
            'payment_id': request.form.get('payment_id'),
            'full_name': request.form.get('full_name'),
            'phone': request.form.get('phone'),
            'email': request.form.get('email'),
            'document': request.form.get('document'),
            'cep': request.form.get('cep'),
            'state': request.form.get('state'),
            'city': request.form.get('city'),
            'neighborhood': request.form.get('neighborhood'),
            'street': request.form.get('street'),
            'number': request.form.get('number'),
            'complement': request.form.get('complement'),
            'reference': request.form.get('reference'),
            'memorial_name': request.form.get('memorial_name'),
            'birth_date': request.form.get('birth_date'),
            'death_date': request.form.get('death_date'),
            'memorial_message': request.form.get('memorial_message'),
            'plate_color': request.form.get('plate_color'),
            'observations': request.form.get('observations'),
            'newsletter': request.form.get('newsletter') == 'on',
            'created_at': datetime.now().isoformat()
        }
        
        # Salvar no banco de dados
        save_shipping_to_database(shipping_data)
        
        # Redirecionar para página de confirmação
        return redirect(url_for('payments.confirmation', payment_id=shipping_data['payment_id']))
        
    except Exception as e:
        print(f"Erro ao salvar endereço: {e}")
        flash('Erro ao salvar endereço de entrega', 'error')
        return redirect(url_for('payments.shipping_address'))

@payments_bp.route('/confirmation')
def confirmation():
    """Página de confirmação do pedido"""
    payment_id = request.args.get('payment_id')
    
    if not payment_id:
        flash('Pagamento não encontrado', 'error')
        return redirect(url_for('payments.create_payment'))
    
    # Buscar dados do pagamento e endereço
    payment_data = get_payment_from_database(payment_id)
    shipping_data = get_shipping_from_database(payment_id)
    
    return render_template('confirmation.html', 
                         payment_data=payment_data,
                         shipping_data=shipping_data)

@payments_bp.route('/success')
def success():
    """Página de sucesso do pagamento"""
    payment_id = request.args.get('payment_id')
    return render_template('payment_success.html', payment_id=payment_id)

@payments_bp.route('/failure')
def failure():
    """Página de falha do pagamento"""
    return render_template('payment_failure.html')

@payments_bp.route('/pending')
def pending():
    """Página de pagamento pendente"""
    payment_id = request.args.get('payment_id')
    return render_template('payment_pending.html', payment_id=payment_id)

@payments_bp.route('/webhook', methods=['POST'])
def webhook():
    """Webhook para receber notificações do Mercado Pago"""
    try:
        data = request.get_json()
        
        if data.get('type') == 'payment':
            payment_id = data.get('data', {}).get('id')
            
            if payment_id:
                # Buscar dados do pagamento
                payment_response = sdk.payment().get(payment_id)
                payment = payment_response["response"]
                
                # Atualizar status no banco de dados
                update_payment_status(payment_id, payment.get('status'))
                
                # Processar ações baseadas no status
                if payment.get('status') == 'approved':
                    # Pagamento aprovado - enviar email de confirmação
                    send_payment_confirmation_email(payment)
                elif payment.get('status') == 'rejected':
                    # Pagamento rejeitado - enviar email de falha
                    send_payment_failure_email(payment)
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        print(f"Erro no webhook: {e}")
        return jsonify({"error": "Erro interno"}), 500

# Funções auxiliares para banco de dados
def save_payment_to_database(payment_data, plan_type):
    """Salvar dados do pagamento no banco de dados"""
    try:
        # Implementar salvamento no banco
        # Por enquanto, salvar em arquivo JSON para teste
        payments_file = 'payments.json'
        
        if os.path.exists(payments_file):
            with open(payments_file, 'r') as f:
                payments = json.load(f)
        else:
            payments = []
        
        payment_record = {
            'id': payment_data.get('id'),
            'status': payment_data.get('status'),
            'amount': payment_data.get('transaction_amount'),
            'plan_type': plan_type,
            'created_at': datetime.now().isoformat(),
            'payment_data': payment_data
        }
        
        payments.append(payment_record)
        
        with open(payments_file, 'w') as f:
            json.dump(payments, f, indent=2)
            
    except Exception as e:
        print(f"Erro ao salvar pagamento: {e}")

def save_shipping_to_database(shipping_data):
    """Salvar dados de entrega no banco de dados"""
    try:
        # Implementar salvamento no banco
        # Por enquanto, salvar em arquivo JSON para teste
        shipping_file = 'shipping.json'
        
        if os.path.exists(shipping_file):
            with open(shipping_file, 'r') as f:
                shipping_records = json.load(f)
        else:
            shipping_records = []
        
        shipping_records.append(shipping_data)
        
        with open(shipping_file, 'w') as f:
            json.dump(shipping_records, f, indent=2)
            
    except Exception as e:
        print(f"Erro ao salvar endereço: {e}")

def get_payment_from_database(payment_id):
    """Buscar dados do pagamento no banco de dados"""
    try:
        payments_file = 'payments.json'
        if os.path.exists(payments_file):
            with open(payments_file, 'r') as f:
                payments = json.load(f)
            
            for payment in payments:
                if str(payment.get('id')) == str(payment_id):
                    return payment
        
        return None
    except Exception as e:
        print(f"Erro ao buscar pagamento: {e}")
        return None

def get_shipping_from_database(payment_id):
    """Buscar dados de entrega no banco de dados"""
    try:
        shipping_file = 'shipping.json'
        if os.path.exists(shipping_file):
            with open(shipping_file, 'r') as f:
                shipping_records = json.load(f)
            
            for record in shipping_records:
                if str(record.get('payment_id')) == str(payment_id):
                    return record
        
        return None
    except Exception as e:
        print(f"Erro ao buscar endereço: {e}")
        return None

def update_payment_status(payment_id, status):
    """Atualizar status do pagamento no banco de dados"""
    try:
        payments_file = 'payments.json'
        if os.path.exists(payments_file):
            with open(payments_file, 'r') as f:
                payments = json.load(f)
            
            for payment in payments:
                if str(payment.get('id')) == str(payment_id):
                    payment['status'] = status
                    payment['updated_at'] = datetime.now().isoformat()
                    break
            
            with open(payments_file, 'w') as f:
                json.dump(payments, f, indent=2)
                
    except Exception as e:
        print(f"Erro ao atualizar status: {e}")

def send_payment_confirmation_email(payment_data):
    """Enviar email de confirmação de pagamento"""
    # Implementar envio de email
    print(f"Enviando email de confirmação para pagamento {payment_data.get('id')}")

def send_payment_failure_email(payment_data):
    """Enviar email de falha no pagamento"""
    # Implementar envio de email
    print(f"Enviando email de falha para pagamento {payment_data.get('id')}")

