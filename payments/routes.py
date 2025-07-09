from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from mercadopago_service import MercadoPagoService
from database import Database
import json
import os

payments_bp = Blueprint("payments", __name__)

# Instanciar o serviço do Mercado Pago
# mp_service = MercadoPagoService()

@payments_bp.before_request
def before_request():
    global mp_service
    mp_service = MercadoPagoService()

@payments_bp.route("/create-payment", methods=["GET", "POST"])
def create_payment():
    if request.method == "POST":
        # Obter o tipo de plano do formulário
        plan_type = request.form.get('plan_type', 'premium')
        
        # Definir os planos disponíveis
        plans = {
            "basico": {"name": "Básico", "amount": 29.00},
            "premium": {"name": "Premium", "amount": 59.00},
            "familia": {"name": "Família", "amount": 99.00},
            "pet_basico": {"name": "Pet Básico", "amount": 19.90},
            "pet_premium": {"name": "Pet Premium", "amount": 29.90}
        }
        
        plan = plans.get(plan_type, plans["premium"])
        
        try:
            # Criar preferência de pagamento
            preference_data = {
                "items": [
                    {
                        "title": f"Plano {plan['name']} - Memorial Online",
                        "quantity": 1,
                        "unit_price": plan['amount']
                    }
                ],
                "back_urls": {
                    "success": url_for('payments.success', _external=True),
                    "failure": url_for('payments.failure', _external=True),
                    "pending": url_for('payments.pending', _external=True)
                },
                "auto_return": "approved"
            }
            
            preference = mp_service.create_preference(preference_data)
            
            if preference and 'id' in preference:
                return jsonify({"preference_id": preference['id']})
            else:
                return jsonify({"error": "Erro ao criar preferência"}), 400
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return render_template("create_payment.html")

@payments_bp.route("/checkout")
def checkout():
    public_key = os.getenv("MERCADOPAGO_PUBLIC_KEY", "TEST-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
    return render_template("checkout.html", public_key=public_key)

@payments_bp.route("/checkout-demo")
def checkout_demo():
    return render_template("checkout_demo.html")

@payments_bp.route("/api/process_payment", methods=["POST"])
def process_payment():
    data = request.get_json()
    payment_data = {
        "transaction_amount": float(data["transaction_amount"]),
        "token": data["token"],
        "description": data["description"],
        "installments": int(data["installments"]),
        "payment_method_id": data["payment_method_id"] if "payment_method_id" in data else None,
        "issuer_id": int(data["issuer_id"]) if "issuer_id" in data else None,
        "payer": {
            "email": data["payer_email"],
            "first_name": data["payer_first_name"],
            "last_name": data["payer_last_name"],
            "identification": {
                "type": data["payer_identification_type"],
                "number": data["payer_identification_number"]
            }
        }
    }

    payment_response = mp_service.create_payment(payment_data)

    if payment_response and payment_response["status"] == "approved":
        return jsonify({"status": "success", "message": "Pagamento aprovado!"})
    else:
        return jsonify({"status": "error", "message": "Falha no pagamento.", "details": payment_response}), 400

@payments_bp.route("/shipping-address")
def shipping_address():
    return render_template("shipping_address.html")

@payments_bp.route("/save-shipping-address", methods=["POST"])
def save_shipping_address():
    # Lógica para salvar o endereço de entrega
    flash("Endereço de entrega salvo com sucesso!", "success")
    return redirect(url_for("payments.confirmation"))

@payments_bp.route("/confirmation")
def confirmation():
    return render_template("confirmation.html")

@payments_bp.route("/payments/webhook", methods=["POST"])
def mercadopago_webhook():
    data = request.json
    mp_service.process_webhook(data)
    return "OK", 200

@payments_bp.route("/success")
def success():
    return render_template("success.html")

@payments_bp.route("/failure")
def failure():
    return render_template("failure.html")

@payments_bp.route("/pending")
def pending():
    return render_template("pending.html")


