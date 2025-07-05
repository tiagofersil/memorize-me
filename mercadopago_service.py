import mercadopago
from flask import current_app, request
import os

class MercadoPagoService:
    def __init__(self, access_token=None):
        self.access_token = access_token or os.getenv("MERCADOPAGO_ACCESS_TOKEN")
        if self.access_token:
            self.sdk = mercadopago.SDK(self.access_token)
    
    def create_preference(self, items, payer_email, external_reference=None):
        """
        Cria uma preferência de pagamento no Mercado Pago
        
        Args:
            items: Lista de itens para pagamento
            payer_email: Email do pagador
            external_reference: Referência externa (opcional)
        
        Returns:
            dict: Resposta da API do Mercado Pago
        """
        if not self.access_token:
            return {"error": "Access token do Mercado Pago não configurado"}
        
        # Obter URL base dinamicamente ou usar configuração
        base_url = self._get_base_url()

        preference_data = {
            "items": items,
            "payer": {
                "email": payer_email
            },
            "back_urls": {
                "success": f"{base_url}/payments/success",
                "failure": f"{base_url}/payments/failure",
                "pending": f"{base_url}/payments/pending"
            },

            "notification_url": f"{base_url}/payments/webhook"
        }
        
        if external_reference:
            preference_data["external_reference"] = external_reference
        
        try:
            preference_response = self.sdk.preference().create(preference_data)
            print(f"[DEBUG] Mercado Pago API Response: {preference_response}")
            return preference_response
        except Exception as e:
            print(f"[ERROR] Erro ao criar preferência: {e}")
            return {"error": str(e)}
    
    def _get_base_url(self):
        """
        Obtém a URL base da aplicação dinamicamente
        Prioriza variável de ambiente, depois ngrok, depois localhost
        """
        # 1. Verificar se há uma URL configurada via variável de ambiente
        base_url = os.getenv("BASE_URL")
        if base_url:
            return base_url.rstrip("/")
        
        # 2. Verificar se há uma URL do ngrok configurada
        ngrok_url = os.getenv("NGROK_URL")
        if ngrok_url:
            return ngrok_url.rstrip("/")
        
        # 3. Tentar obter da requisição atual (se disponível)
        try:
            if request:
                return request.url_root.rstrip("/")
        except:
            pass
        
        # 4. Fallback para localhost (desenvolvimento)
        return "http://localhost:5000"
    
    def get_payment_info(self, payment_id):
        """
        Busca informações de um pagamento específico
        
        Args:
            payment_id: ID do pagamento no Mercado Pago
        
        Returns:
            dict: Informações do pagamento
        """
        if not self.access_token:
            return {"error": "Access token do Mercado Pago não configurado"}
        
        try:
            payment_response = self.sdk.payment().get(payment_id)
            print(f"[DEBUG] Payment info response: {payment_response}")
            return payment_response
        except Exception as e:
            print(f"[ERROR] Erro ao buscar informações do pagamento: {e}")
            return {"error": str(e)}
    
    def create_memorial_payment_preference(self, memorial_name, amount, user_email, memorial_id):
        """
        Cria uma preferência específica para pagamento de memorial
        VERSÃO CORRIGIDA: Funciona com o novo fluxo de planos
        
        Args:
            memorial_name: Nome do memorial/plano
            amount: Valor do pagamento
            user_email: Email do usuário
            memorial_id: Referência única do pagamento
        
        Returns:
            dict: Resposta da API do Mercado Pago
        """
        items = [
            {
                "title": memorial_name,
                "description": "Plano Memorial Digital com QR Code personalizado",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": float(amount)
            }
        ]
        
        print(f"[DEBUG] Criando preferência para: {memorial_name}, Valor: R$ {amount}, Email: {user_email}")
        
        return self.create_preference(
            items=items,
            payer_email=user_email,
            external_reference=str(memorial_id)
        )

    def get_payment_plans(self):
        """Retorna os planos de pagamento disponíveis"""
        return {
            "basic": {
                "name": "Plano Básico",
                "description": "Ideal para memoriais simples e pessoas",
                "amount": 29.0,
                "currency": "BRL"
            },
            "premium": {
                "name": "Plano Premium", 
                "description": "Perfeito para famílias que querem mais recursos",
                "amount": 59.0,
                "currency": "BRL"
            },
            "family": {
                "name": "Plano Família",
                "description": "Memorial familiar com recursos ilimitados e árvore genealógica",
                "amount": 99.0,
                "currency": "BRL"
            },
            "pet_basic": {
                "name": "Plano Pet Básico",
                "description": "Memorial especial para seu companheiro de quatro patas",
                "amount": 19.90,
                "currency": "BRL"
            },
            "pet_premium": {
                "name": "Plano Pet Premium",
                "description": "Memorial completo para seu pet com galeria de fotos e vídeos",
                "amount": 29.90,
                "currency": "BRL"
            }
        }

