import sys
import os

# Adiciona o diretório pai (onde manage.py está) ao sys.path
sys.path.insert(0, os.path.abspath(os.path.abspath(os.path.dirname(__file__))))

from meumemorial.app import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


