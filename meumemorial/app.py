from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, send_from_directory
import os
import sys

# Define o caminho absoluto para o diretório onde o app.py está localizado
APP_DIR = os.path.abspath(os.path.dirname(__file__))

# Adiciona o diretório pai (onde estão accounts, memorial, payments) ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(APP_DIR, '..')))

from accounts.routes import accounts_bp
from memorial.routes import memorial_bp
from memorial.tributes_routes import tributes_bp
from payments.routes import payments_bp
from database import Database
from tribute_scheduler import start_tribute_scheduler
import atexit

app = Flask(__name__,
            template_folder=os.path.join(APP_DIR, '..', 'templates'),
            static_folder=os.path.join(APP_DIR, '..', 'static'))

app.config["SECRET_KEY"] = "your_secret_key_here_change_in_production"  # CHANGE THIS IN PRODUCTION
app.config["UPLOAD_FOLDER"] = os.path.join(APP_DIR, '..', 'media', 'uploads')

# Configurações do Mercado Pago (adicione suas credenciais)
app.config["MERCADOPAGO_ACCESS_TOKEN"] = os.getenv('MERCADOPAGO_ACCESS_TOKEN', 'YOUR_ACCESS_TOKEN_HERE')

# Inicializar banco de dados
db = Database(os.path.join(APP_DIR, '..', 'meumemorial.db'))

# Nova função para servir arquivos da pasta 'media'
@app.route('/media/<path:filename>')
def serve_media(filename):
    return send_from_directory(os.path.join(APP_DIR, '..', 'media'), filename)

# Registrar blueprints
app.register_blueprint(accounts_bp)
app.register_blueprint(memorial_bp)
app.register_blueprint(tributes_bp)
app.register_blueprint(payments_bp)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    # Inicializar agendador de homenagens
    start_tribute_scheduler()
    
    # Registrar função de parada no encerramento
    from tribute_scheduler import stop_tribute_scheduler
    atexit.register(stop_tribute_scheduler)
    
    with app.test_request_context():
        print("DEBUG: Rotas registradas:")
        for rule in app.url_map.iter_rules():
            print(f"  Endpoint: {rule.endpoint}, Methods: {rule.methods}, Rule: {rule.rule}")
    app.run(debug=True, host='0.0.0.0')


