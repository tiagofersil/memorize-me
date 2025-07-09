<<<<<<< HEAD
import mercadopago
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class MercadoPagoService:
    """Serviço para integração com Mercado Pago"""
    
    def __init__(self):
        """Inicializar o serviço do Mercado Pago"""
        self.access_token = os.getenv("ACCESS_TOKEN")
        self.public_key = os.getenv("PUBLIC_KEY")
        
        if not self.access_token:
            raise ValueError("ACCESS_TOKEN não encontrado nas variáveis de ambiente")
        
        self.sdk = mercadopago.SDK(self.access_token)
        
        # Configurações padrão
        self.webhook_url = os.getenv("WEBHOOK_URL", "https://seu-dominio.com/payments/webhook")
        
    def create_credit_card_payment(self, payment_data):
        """Criar pagamento com cartão de crédito"""
        try:
            payment_request = {
                "transaction_amount": float(payment_data.get("transaction_amount")),
                "token": payment_data.get("token"),
                "description": payment_data.get("description", "Memorial Online - Plano"),
                "installments": int(payment_data.get("installments", 1)),
                "payment_method_id": payment_data.get("payment_method_id"),
                "issuer_id": payment_data.get("issuer_id"),
                "payer": {
                    "email": payment_data.get("payer", {}).get("email"),
                    "identification": {
                        "type": payment_data.get("payer", {}).get("identification", {}).get("type"),
                        "number": payment_data.get("payer", {}).get("identification", {}).get("number")
                    }
                },
                "notification_url": self.webhook_url,
                "metadata": {
                    "plan_type": payment_data.get("plan_type"),
                    "user_id": payment_data.get("user_id"),
                    "created_at": datetime.now().isoformat()
                }
            }
            
            payment_response = self.sdk.payment().create(payment_request)
            
            if payment_response["status"] == 201:
                return {
                    "success": True,
                    "payment": payment_response["response"]
                }
            else:
                return {
                    "success": False,
                    "error": payment_response.get("response", {}).get("message", "Erro desconhecido")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao processar pagamento: {str(e)}"
            }
    
    def create_pix_payment(self, payment_data):
        """Criar pagamento via PIX"""
        try:
            payment_request = {
                "transaction_amount": float(payment_data.get("transaction_amount")),
                "description": payment_data.get("description", "Memorial Online - Plano"),
                "payment_method_id": "pix",
                "payer": {
                    "email": payment_data.get("payer", {}).get("email"),
                    "identification": {
                        "type": payment_data.get("payer", {}).get("identification", {}).get("type"),
                        "number": payment_data.get("payer", {}).get("identification", {}).get("number")
                    }
                },
                "notification_url": self.webhook_url,
                "date_of_expiration": (datetime.now() + timedelta(minutes=30)).isoformat(),
                "metadata": {
                    "plan_type": payment_data.get("plan_type"),
                    "user_id": payment_data.get("user_id"),
                    "created_at": datetime.now().isoformat()
                }
            }
            
            payment_response = self.sdk.payment().create(payment_request)
            
            if payment_response["status"] == 201:
                return {
                    "success": True,
                    "payment": payment_response["response"]
                }
            else:
                return {
                    "success": False,
                    "error": payment_response.get("response", {}).get("message", "Erro desconhecido")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao processar PIX: {str(e)}"
            }
    
    def create_boleto_payment(self, payment_data):
        """Criar pagamento via boleto"""
        try:
            payment_request = {
                "transaction_amount": float(payment_data.get("transaction_amount")),
                "description": payment_data.get("description", "Memorial Online - Plano"),
                "payment_method_id": "bolbradesco",
                "payer": {
                    "email": payment_data.get("payer", {}).get("email"),
                    "identification": {
                        "type": payment_data.get("payer", {}).get("identification", {}).get("type"),
                        "number": payment_data.get("payer", {}).get("identification", {}).get("number")
                    }
                },
                "notification_url": self.webhook_url,
                "date_of_expiration": (datetime.now() + timedelta(days=3)).isoformat(),
                "metadata": {
                    "plan_type": payment_data.get("plan_type"),
                    "user_id": payment_data.get("user_id"),
                    "created_at": datetime.now().isoformat()
                }
            }
            
            payment_response = self.sdk.payment().create(payment_request)
            
            if payment_response["status"] == 201:
                return {
                    "success": True,
                    "payment": payment_response["response"]
                }
            else:
                return {
                    "success": False,
                    "error": payment_response.get("response", {}).get("message", "Erro desconhecido")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao processar boleto: {str(e)}"
            }
    
    def create_debit_card_payment(self, payment_data):
        """Criar pagamento com cartão de débito"""
        try:
            payment_request = {
                "transaction_amount": float(payment_data.get("transaction_amount")),
                "token": payment_data.get("token"),
                "description": payment_data.get("description", "Memorial Online - Plano"),
                "payment_method_id": payment_data.get("payment_method_id"),
                "issuer_id": payment_data.get("issuer_id"),
                "payer": {
                    "email": payment_data.get("payer", {}).get("email"),
                    "identification": {
                        "type": payment_data.get("payer", {}).get("identification", {}).get("type"),
                        "number": payment_data.get("payer", {}).get("identification", {}).get("number")
                    }
                },
                "notification_url": self.webhook_url,
                "metadata": {
                    "plan_type": payment_data.get("plan_type"),
                    "user_id": payment_data.get("user_id"),
                    "created_at": datetime.now().isoformat()
                }
            }
            
            payment_response = self.sdk.payment().create(payment_request)
            
            if payment_response["status"] == 201:
                return {
                    "success": True,
                    "payment": payment_response["response"]
                }
            else:
                return {
                    "success": False,
                    "error": payment_response.get("response", {}).get("message", "Erro desconhecido")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao processar débito: {str(e)}"
            }
    
    def get_payment(self, payment_id):
        """Buscar informações de um pagamento"""
        try:
            payment_response = self.sdk.payment().get(payment_id)
            
            if payment_response["status"] == 200:
                return {
                    "success": True,
                    "payment": payment_response["response"]
                }
            else:
                return {
                    "success": False,
                    "error": "Pagamento não encontrado"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao buscar pagamento: {str(e)}"
            }
    
    def get_payment_methods(self):
        """Obter métodos de pagamento disponíveis"""
        try:
            payment_methods_response = self.sdk.payment_methods().list_all()
            
            if payment_methods_response["status"] == 200:
                return {
                    "success": True,
                    "payment_methods": payment_methods_response["response"]
                }
            else:
                return {
                    "success": False,
                    "error": "Erro ao obter métodos de pagamento"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao obter métodos de pagamento: {str(e)}"
            }
    
    def get_installments(self, payment_method_id, amount, issuer_id=None):
        """Obter opções de parcelamento"""
        try:
            params = {
                "payment_method_id": payment_method_id,
                "amount": amount
            }
            
            if issuer_id:
                params["issuer_id"] = issuer_id
            
            installments_response = self.sdk.payment_methods().installments(params)
            
            if installments_response["status"] == 200:
                return {
                    "success": True,
                    "installments": installments_response["response"]
                }
            else:
                return {
                    "success": False,
                    "error": "Erro ao obter parcelamento"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao obter parcelamento: {str(e)}"
            }
    
    def create_preference(self, preference_data):
        """Criar preferência de pagamento"""
        try:
            preference_request = {
                "items": [
                    {
                        "title": preference_data.get("title", "Memorial Online"),
                        "description": preference_data.get("description", "Plano Memorial Online"),
                        "quantity": 1,
                        "currency_id": "BRL",
                        "unit_price": float(preference_data.get("amount"))
                    }
                ],
                "payer": {
                    "email": preference_data.get("payer_email")
                },
                "back_urls": {
                    "success": preference_data.get("success_url", "https://seu-site.com/success"),
                    "failure": preference_data.get("failure_url", "https://seu-site.com/failure"),
                    "pending": preference_data.get("pending_url", "https://seu-site.com/pending")
                },
                "auto_return": "approved",
                "notification_url": self.webhook_url,
                "metadata": {
                    "plan_type": preference_data.get("plan_type"),
                    "user_id": preference_data.get("user_id")
                }
            }
            
            preference_response = self.sdk.preference().create(preference_request)
            
            if preference_response["status"] == 201:
                return {
                    "success": True,
                    "preference": preference_response["response"]
                }
            else:
                return {
                    "success": False,
                    "error": preference_response.get("response", {}).get("message", "Erro desconhecido")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao criar preferência: {str(e)}"
            }
    
    def process_webhook_notification(self, notification_data):
        """Processar notificação do webhook"""
        try:
            notification_type = notification_data.get("type")
            
            if notification_type == "payment":
                payment_id = notification_data.get("data", {}).get("id")
                
                if payment_id:
                    # Buscar dados atualizados do pagamento
                    payment_result = self.get_payment(payment_id)
                    
                    if payment_result["success"]:
                        payment = payment_result["payment"]
                        
                        return {
                            "success": True,
                            "payment_id": payment_id,
                            "status": payment.get("status"),
                            "payment_data": payment
                        }
                    else:
                        return {
                            "success": False,
                            "error": "Erro ao buscar dados do pagamento"
                        }
                else:
                    return {
                        "success": False,
                        "error": "ID do pagamento não encontrado na notificação"
                    }
            else:
                return {
                    "success": False,
                    "error": f"Tipo de notificação não suportado: {notification_type}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao processar webhook: {str(e)}"
            }
    
    def validate_payment_status(self, payment_id):
        """Validar status atual de um pagamento"""
        try:
            payment_result = self.get_payment(payment_id)
            
            if payment_result["success"]:
                payment = payment_result["payment"]
                status = payment.get("status")
                
                status_info = {
                    "approved": {
                        "message": "Pagamento aprovado",
                        "action": "activate_service"
                    },
                    "pending": {
                        "message": "Pagamento pendente",
                        "action": "wait_confirmation"
                    },
                    "rejected": {
                        "message": "Pagamento rejeitado",
                        "action": "retry_payment"
                    },
                    "cancelled": {
                        "message": "Pagamento cancelado",
                        "action": "retry_payment"
                    },
                    "refunded": {
                        "message": "Pagamento estornado",
                        "action": "deactivate_service"
                    }
                }
                
                return {
                    "success": True,
                    "status": status,
                    "info": status_info.get(status, {"message": "Status desconhecido", "action": "contact_support"}),
                    "payment_data": payment
                }
            else:
                return payment_result
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao validar status: {str(e)}"
            }
    
    def get_public_key(self):
        """Obter chave pública para uso no frontend"""
        return self.public_key
    
    def format_payment_for_frontend(self, payment_data):
        """Formatar dados do pagamento para o frontend"""
        try:
            formatted_data = {
                "id": payment_data.get("id"),
                "status": payment_data.get("status"),
                "status_detail": payment_data.get("status_detail"),
                "transaction_amount": payment_data.get("transaction_amount"),
                "currency_id": payment_data.get("currency_id"),
                "payment_method_id": payment_data.get("payment_method_id"),
                "payment_type_id": payment_data.get("payment_type_id"),
                "date_created": payment_data.get("date_created"),
                "date_approved": payment_data.get("date_approved"),
                "installments": payment_data.get("installments"),
                "description": payment_data.get("description")
            }
            
            # Adicionar dados específicos do PIX
            if payment_data.get("point_of_interaction"):
                formatted_data["point_of_interaction"] = payment_data.get("point_of_interaction")
            
            # Adicionar dados específicos do boleto
            if payment_data.get("transaction_details"):
                formatted_data["transaction_details"] = payment_data.get("transaction_details")
            
            return formatted_data
            
        except Exception as e:
            return {
                "error": f"Erro ao formatar dados: {str(e)}"
            }

    def create_memorial_payment_preference(self, memorial_name, amount, user_email, memorial_id):
        """Criar preferência de pagamento para memorial"""
        try:
            preference_request = {
                "items": [
                    {
                        "title": memorial_name,
                        "description": f"Pagamento para o memorial: {memorial_name}",
                        "quantity": 1,
                        "currency_id": "BRL",
                        "unit_price": float(amount)
                    }
                ],
                "payer": {
                    "email": user_email
                },
                "back_urls": {
                    "success": os.getenv("BASE_URL") + "/payments/success",
                    "failure": os.getenv("BASE_URL") + "/payments/failure",
                    "pending": os.getenv("BASE_URL") + "/payments/pending"
                },
                "auto_return": "approved",
                "notification_url": self.webhook_url,
                "external_reference": memorial_id,
                "metadata": {
                    "memorial_id": memorial_id,
                    "memorial_name": memorial_name
                }
            }
            
            preference_response = self.sdk.preference().create(preference_request)
            
            if preference_response["status"] == 201:
                return {
                    "success": True,
                    "response": preference_response["response"],
                    "status": 201
                }
            else:
                return {
                    "success": False,
                    "error": preference_response.get("response", {}).get("message", "Erro desconhecido"),
                    "status": preference_response["status"]
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao criar preferência de memorial: {str(e)}",
                "status": 500
            }

# Instância global do serviço
mercadopago_service = None

def get_mercadopago_service():
    """Obter instância do serviço MercadoPago"""
    global mercadopago_service
    
    if mercadopago_service is None:
        try:
            mercadopago_service = MercadoPagoService()
        except Exception as e:
            print(f"Erro ao inicializar MercadoPagoService: {e}")
            return None
    
    return mercadopago_service


=======
from dotenv import load_dotenv
load_dotenv()

import os
import mercadopago
import qrcode
from io import BytesIO
import base64
import json

class MercadoPagoService:
    def __init__(self):
        self.access_token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
        self.public_key = os.getenv("MERCADOPAGO_PUBLIC_KEY")
        if not self.access_token:
            raise ValueError("MERCADOPAGO_ACCESS_TOKEN não encontrado nas variáveis de ambiente")
        if not self.public_key:
            raise ValueError("MERCADOPAGO_PUBLIC_KEY não encontrado nas variáveis de ambiente")
        self.sdk = mercadopago.SDK(self.access_token)

    def create_payment(self, payment_data):
        try:
            payment_response = self.sdk.payment().create(payment_data)
            return payment_response
        except Exception as e:
            print(f"Erro ao criar pagamento: {e}")
            return None

    def get_payment_methods(self):
        try:
            payment_methods = self.sdk.payment_methods().get()
            return payment_methods
        except Exception as e:
            print(f"Erro ao obter métodos de pagamento: {e}")
            return None

    def get_installments(self, amount, payment_method_id, issuer_id=None):
        try:
            installments = self.sdk.installments().get(
                amount=amount,
                payment_method_id=payment_method_id,
                issuer_id=issuer_id
            )
            return installments
        except Exception as e:
            print(f"Erro ao obter parcelamento: {e}")
            return None

    def create_preference(self, preference_data):
        try:
            preference_response = self.sdk.preference().create(preference_data)
            return preference_response["response"]
        except Exception as e:
            print(f"Erro ao criar preferência: {e}")
            return None

    def process_webhook(self, data):
        # Implementar lógica de processamento de webhook
        print(f"Webhook recebido: {json.dumps(data, indent=2)}")
        # Exemplo: Atualizar status do pedido no banco de dados
        return {"status": "success"}

    def generate_qr_code(self, data):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return img_str

    def get_payment_status(self, payment_id):
        try:
            payment_info = self.sdk.payment().get(payment_id)
            return payment_info
        except Exception as e:
            print(f"Erro ao obter status do pagamento: {e}")
            return None
>>>>>>> afe9238 (fg)


