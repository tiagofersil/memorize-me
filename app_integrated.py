from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, send_from_directory, request, session
from flask_login import LoginManager, current_user
import os
import sys

# Define o caminho absoluto para o diretório onde o app.py está localizado
APP_DIR = os.path.abspath(os.path.dirname(__file__))

# Adiciona o diretório atual ao sys.path
sys.path.insert(0, APP_DIR)

# Importações dos serviços e rotas
try:
    from database_enhanced import DatabaseEnhanced
    from auth_service import User, AuthService
    from cloudinary_service import CloudinaryService
    from security_service import SecurityService
    
    # Importar blueprints
    from auth_routes import auth_bp
    from memorial_routes import memorial_bp
    from image_routes import image_bp
    from privacy_routes import privacy_bp
<<<<<<< HEAD
<<<<<<< HEAD
    from payments.payment_routes import payment_bp
=======
    from payment_routes import payments_bp
>>>>>>> f66989d (hg)
=======
    from payment_routes import payments_bp
>>>>>>> afe9238 (fg)
    
    print("Todos os módulos importados com sucesso!")
except ImportError as e:
    print(f"Erro na importação: {e}")
    sys.exit(1)

# Criar aplicação Flask
app = Flask(__name__,
            template_folder=os.path.join(APP_DIR, 'templates'),
            static_folder=os.path.join(APP_DIR, 'static'))

# Configurações
app.config["SECRET_KEY"] = os.getenv('SECRET_KEY', 'your_secret_key_here_change_in_production')
app.config["UPLOAD_FOLDER"] = os.path.join(APP_DIR, 'media', 'uploads')

# Configurações do Cloudinary
app.config["CLOUDINARY_CLOUD_NAME"] = os.getenv('CLOUDINARY_CLOUD_NAME')
app.config["CLOUDINARY_API_KEY"] = os.getenv('CLOUDINARY_API_KEY')
app.config["CLOUDINARY_API_SECRET"] = os.getenv('CLOUDINARY_API_SECRET')

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Você precisa fazer login para acessar esta página.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Inicializar serviços
try:
    db = DatabaseEnhanced(os.path.join(APP_DIR, 'meumemorial.db'))
    auth_service = AuthService()
    security_service = SecurityService()
    
    # Verificar se Cloudinary está configurado
    if all([app.config["CLOUDINARY_CLOUD_NAME"], app.config["CLOUDINARY_API_KEY"], app.config["CLOUDINARY_API_SECRET"]]):
        cloudinary_service = CloudinaryService()
        print("Cloudinary configurado com sucesso!")
    else:
        print("AVISO: Cloudinary não configurado. Verifique o arquivo .env")
        
except Exception as e:
    print(f"Erro ao inicializar serviços: {e}")

# Função para servir arquivos da pasta 'media'
@app.route('/media/<path:filename>')
def serve_media(filename):
    return send_from_directory(os.path.join(APP_DIR, 'media'), filename)

# Registrar blueprints
try:
    app.register_blueprint(auth_bp)
    app.register_blueprint(memorial_bp)
    app.register_blueprint(image_bp)
    app.register_blueprint(privacy_bp)
<<<<<<< HEAD
<<<<<<< HEAD
    app.register_blueprint(payment_bp)
=======
    app.register_blueprint(payments_bp)
>>>>>>> f66989d (hg)
=======
    app.register_blueprint(payments_bp)
>>>>>>> afe9238 (fg)
    print("Blueprints registrados com sucesso!")
except Exception as e:
    print(f"Erro ao registrar blueprints: {e}")

# Rotas principais
@app.route("/")
def index():
    """Página inicial"""
    return render_template("index.html")

@app.route("/about")
def about():
    """Página sobre"""
    return render_template("about.html")

@app.route("/contact")
def contact():
    """Página de contato"""
    return render_template("contact.html")

@app.route("/features")
def features():
    """Página de funcionalidades"""
    return render_template("features.html")

@app.route("/pricing")
def pricing():
    """Página de preços"""
    return render_template("pricing.html")

# Rota de teste para verificar se o Flask está funcionando
@app.route("/test")
def test():
    return "Flask está funcionando!"

@app.route("/test-db")
def test_db():
    """Teste de conexão com banco de dados"""
    try:
        # Testar criação de usuário
        result = db.criar_usuario(
            username="test_user",
            email="test@example.com",
            password="test123",
            nome_completo="Usuário Teste"
        )
        
        if result:
            return f"Banco de dados funcionando! Usuário criado com ID: {result}"
        else:
            return "Banco de dados funcionando, mas usuário já existe ou erro na criação"
    except Exception as e:
        return f"Erro no banco de dados: {str(e)}"

@app.route("/test-cloudinary")
def test_cloudinary():
    """Teste de conexão com Cloudinary"""
    try:
        if 'cloudinary_service' in globals():
            # Testar configuração
            import cloudinary
            config = cloudinary.config()
            return f"Cloudinary configurado: {config.cloud_name}"
        else:
            return "Cloudinary não configurado"
    except Exception as e:
        return f"Erro no Cloudinary: {str(e)}"

# Context processors para templates
@app.context_processor
def inject_user():
    """Injeta informações do usuário nos templates"""
    return dict(current_user=current_user)

@app.context_processor
def inject_security():
    """Injeta funções de segurança nos templates"""
    return dict(
        csrf_token=security_service.generate_csrf_token() if 'security_service' in globals() else None
    )

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def forbidden(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

# Middleware de segurança
@app.before_request
def security_middleware():
    """Middleware de segurança executado antes de cada request"""
    # Rate limiting para IPs
    if 'security_service' in globals():
        rate_result = security_service.check_rate_limit(request.remote_addr, 'api')
        if not rate_result['allowed']:
            return {'error': rate_result['error']}, 429
    
    # Log de acesso para rotas sensíveis
    sensitive_routes = ['/auth/', '/memorial/', '/images/', '/privacy/']
    if any(request.path.startswith(route) for route in sensitive_routes):
        if 'security_service' in globals():
            security_service.log_security_event(
                event_type='route_access',
                user_id=int(current_user.id) if current_user.is_authenticated else None,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                details=f'Acesso à rota: {request.path}'
            )

# Configurações de segurança HTTP
@app.after_request
def security_headers(response):
    """Adiciona headers de segurança"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # CORS para desenvolvimento
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    
    return response

if __name__ == "__main__":
    # Verificar se os diretórios necessários existem
    template_dir = os.path.join(APP_DIR, 'templates')
    static_dir = os.path.join(APP_DIR, 'static')
    media_dir = os.path.join(APP_DIR, 'media')
    
    print(f"Diretório de templates: {template_dir}")
    print(f"Existe: {os.path.exists(template_dir)}")
    print(f"Diretório de arquivos estáticos: {static_dir}")
    print(f"Existe: {os.path.exists(static_dir)}")
    print(f"Diretório de media: {media_dir}")
    print(f"Existe: {os.path.exists(media_dir)}")
    
    # Criar diretórios se não existirem
    os.makedirs(media_dir, exist_ok=True)
    os.makedirs(os.path.join(media_dir, 'uploads'), exist_ok=True)
    
    # Listar templates disponíveis
    if os.path.exists(template_dir):
        templates = []
        for root, dirs, files in os.walk(template_dir):
            for file in files:
                if file.endswith('.html'):
                    rel_path = os.path.relpath(os.path.join(root, file), template_dir)
                    templates.append(rel_path)
        print(f"Templates disponíveis: {templates}")
    
    with app.test_request_context():
        print("DEBUG: Rotas registradas:")
        for rule in app.url_map.iter_rules():
            print(f"  Endpoint: {rule.endpoint}, Methods: {rule.methods}, Rule: {rule.rule}")
    
    print("" + "="*50)
    print("MEMORIAL DIGITAL - SISTEMA INTEGRADO")
    print("="*50)
    print("✅ Autenticação de usuários")
    print("✅ Integração com Cloudinary")
    print("✅ Banco de dados estruturado")
    print("✅ Sistema de segurança e privacidade")
    print("✅ Upload e gerenciamento de imagens")
    print("✅ Textos personalizados e homenagens")
    print("="*50)
    print(f"Servidor rodando em: http://0.0.0.0:5000")
    print("="*50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)


