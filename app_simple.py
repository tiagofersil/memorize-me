from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, send_from_directory
import os

# Criar aplicação Flask
app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configurações
app.config["SECRET_KEY"] = os.getenv('SECRET_KEY', 'your_secret_key_here_change_in_production')

# Importar e registrar blueprint de pagamentos
try:
    from payment_routes import payments_bp
    app.register_blueprint(payments_bp)
    print("Blueprint de pagamentos registrado com sucesso!")
except ImportError as e:
    print(f"Erro ao importar payment_routes: {e}")

# Função para servir arquivos da pasta 'media'
@app.route('/media/<path:filename>')
def serve_media(filename):
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'media'), filename)

# Rotas principais
@app.route("/")
def index():
    """Página inicial"""
    return render_template("index.html")

@app.route("/pricing")
def pricing():
    """Página de preços"""
    return render_template("pricing.html")

# Configurações de segurança HTTP
@app.after_request
def security_headers(response):
    """Adiciona headers de segurança"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # CORS para desenvolvimento
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    
    return response

if __name__ == "__main__":
    print("" + "="*50)
    print("MEMORIAL DIGITAL - SISTEMA DE PAGAMENTOS")
    print("="*50)
    print("✅ Checkout transparente Mercado Pago")
    print("✅ Página de endereço de entrega")
    print("✅ Integração completa com API")
    print("="*50)
    print(f"Servidor rodando em: http://0.0.0.0:5000")
    print("="*50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

