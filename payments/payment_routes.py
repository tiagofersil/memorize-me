from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from mercadopago_service import MercadoPagoService
from database_enhanced import DatabaseEnhanced
import os

payment_bp = Blueprint('payment', __name__, url_prefix='/payment')

# Inicializa o serviço do Mercado Pago
mp_service = MercadoPagoService()

# Inicializa o banco de dados
db = DatabaseEnhanced(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'meumemorial.db'))

@payment_bp.route('/select_plan')
@login_required
def select_plan():
    plans = mp_service.get_payment_plans()
    return render_template('payment/select_plan.html', plans=plans)

@payment_bp.route('/create_preference', methods=['POST'])
@login_required
def create_preference():
    plan_id = request.form.get('plan_id')
    plans = mp_service.get_payment_plans()

    if plan_id not in plans:
        flash('Plano inválido.', 'danger')
        return redirect(url_for('payment.select_plan'))

    selected_plan = plans[plan_id]
    memorial_id = current_user.id # Usar o ID do usuário como referência externa

    preference_response = mp_service.create_memorial_payment_preference(
        memorial_name=selected_plan['name'],
        amount=selected_plan['amount'],
        user_email=current_user.email,
        memorial_id=memorial_id
    )

    if 'error' in preference_response:
        flash(f"Erro ao criar preferência de pagamento: {preference_response['error']}", 'danger')
        return redirect(url_for('payment.select_plan'))

    preference_id = preference_response['response']['id']
    init_point = preference_response['response']['init_point']

    # Salvar informações da preferência na sessão para uso posterior
    session['mp_preference_id'] = preference_id
    session['mp_external_reference'] = str(memorial_id)
    session['mp_plan_id'] = plan_id

    return redirect(init_point)

@payment_bp.route('/success')
def success():
    payment_id = request.args.get('payment_id')
    status = request.args.get('status')
    preference_id = request.args.get('preference_id')
    external_reference = request.args.get('external_reference')

    if status == 'approved':
        flash('Pagamento aprovado com sucesso! Agora, por favor, informe seu endereço para o envio da placa.', 'success')
        return redirect(url_for('payment.address_form'))
    else:
        flash(f'Pagamento {status}. Por favor, tente novamente.', 'warning')
        return redirect(url_for('payment.select_plan'))

@payment_bp.route('/failure')
def failure():
    flash('O pagamento falhou. Por favor, tente novamente.', 'danger')
    return redirect(url_for('payment.select_plan'))

@payment_bp.route('/pending')
def pending():
    flash('O pagamento está pendente. Assim que for aprovado, você será notificado.', 'info')
    return redirect(url_for('payment.select_plan'))

@payment_bp.route('/webhook', methods=['POST'])
def webhook():
    # Implementar a lógica do webhook para processar notificações do Mercado Pago
    # Isso é crucial para atualizar o status do pagamento no seu sistema
    # e acionar o formulário de endereço quando o pagamento for aprovado via webhook
    data = request.json
    print(f"[WEBHOOK] Dados recebidos: {data}")

    if data and data['type'] == 'payment':
        payment_id = data['data']['id']
        payment_info = mp_service.get_payment_info(payment_id)
        
        if payment_info and payment_info['response']['status'] == 'approved':
            external_reference = payment_info['response']['external_reference']
            # Aqui você pode associar o pagamento aprovado ao usuário/memorial
            # e talvez marcar que o endereço precisa ser coletado
            print(f"[WEBHOOK] Pagamento {payment_id} aprovado para referência externa {external_reference}")
            # TODO: Atualizar o status do pagamento no banco de dados e acionar a coleta de endereço
            # Para este MVP, vamos focar no fluxo de retorno direto do navegador

    return '', 200

@payment_bp.route('/address_form')
@login_required
def address_form():
    # Verificar se o usuário tem um pagamento aprovado recente para preencher o endereço
    # Isso pode ser feito verificando a sessão ou o banco de dados
    if 'mp_preference_id' not in session or 'mp_external_reference' not in session:
        flash('Você precisa ter um pagamento aprovado para acessar esta página.', 'warning')
        return redirect(url_for('payment.select_plan'))

    return render_template('payment/address_form.html')

@payment_bp.route('/submit_address', methods=['POST'])
@login_required
def submit_address():
    if 'mp_preference_id' not in session or 'mp_external_reference' not in session:
        flash('Sessão de pagamento inválida.', 'danger')
        return redirect(url_for('payment.select_plan'))

    # Coletar dados do formulário
    address_data = {
        'street': request.form.get('street'),
        'number': request.form.get('number'),
        'complement': request.form.get('complement'),
        'neighborhood': request.form.get('neighborhood'),
        'city': request.form.get('city'),
        'state': request.form.get('state'),
        'zip_code': request.form.get('zip_code')
    }

    # Validar dados (exemplo simples)
    if not all([address_data['street'], address_data['number'], address_data['neighborhood'],
                address_data['city'], address_data['state'], address_data['zip_code']]):
        flash('Por favor, preencha todos os campos obrigatórios do endereço.', 'danger')
        return redirect(url_for('payment.address_form'))

    # Salvar endereço no banco de dados associado ao usuário ou ao pagamento
    # Para este MVP, vamos associar ao usuário logado
    user_id = current_user.id
    db.save_user_address(user_id, address_data)

    # Limpar dados da sessão
    session.pop('mp_preference_id', None)
    session.pop('mp_external_reference', None)
    session.pop('mp_plan_id', None)

    flash('Endereço salvo com sucesso! Seu QR Code será enviado em breve.', 'success')
    return redirect(url_for('index'))



