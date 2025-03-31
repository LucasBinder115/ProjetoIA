import os
import sys
import requests
from datetime import datetime
from configparser import ConfigParser
from flask import Flask, send_file, request, render_template_string
from pathlib import Path
import logging

# ==============================================
# Configurações Globais
# ==============================================
class Colors:
    SUCCESS = '\033[92m'
    ERROR = '\033[91m'
    WARNING = '\033[93m'
    END = '\033[0m'

CONFIG_DIR = Path.home() / ".pdf_generator"
CONFIG_FILE = CONFIG_DIR / "config.ini"
API_SECTION = "PDFco"
API_KEY = "binderlucas356@gmail.com_NynT0l2XTk63SvUrUUkl9ACgaHni4C4rczFVNWSnsUObBXNLSghhdKegpbbmiosr"  # Using the provided key
PDF_CO_ENDPOINT = "https://api.pdf.co/v1/pdf/convert/from/html"

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==============================================
# Funções de Configuração
# ==============================================
def ensure_config_directory():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_config():
    ensure_config_directory()
    config = ConfigParser()
    if CONFIG_FILE.exists():
        config.read(CONFIG_FILE)
    return config

def save_config(api_key):
    config = ConfigParser()
    config[API_SECTION] = {"api_key": api_key}
    ensure_config_directory()
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)
    logger.info("API key saved successfully")

def get_api_key():
    config = load_config()
    return config.get(API_SECTION, "api_key", fallback=API_KEY)

# ==============================================
# Funções de Geração de PDF
# ==============================================
def generate_pdf(api_key, content, title=None, is_html=False):
    payload = {
        "name": title or f"Document_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "html" if is_html else "text": content,
        "margins": "20px 20px 20px 20px",
        "paperSize": "A4",
        "orientation": "portrait",
        "async": False
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }

    try:
        response = requests.post(PDF_CO_ENDPOINT, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if result.get('error'):
            raise ValueError(result['message'])
        
        pdf_url = result['url']
        pdf_response = requests.get(pdf_url, timeout=30)
        pdf_response.raise_for_status()
        
        filename = f"{payload['name']}.pdf"
        return filename, pdf_response.content
        
    except requests.Timeout:
        raise Exception("Request timed out")
    except requests.RequestException as e:
        raise Exception(f"Connection error: {str(e)}")
    except Exception as e:
        raise Exception(f"PDF generation failed: {str(e)}")

# ==============================================
# Aplicação Flask
# ==============================================
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>PDF Generator</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        textarea { width: 100%; height: 200px; }
        input[type="text"] { width: 100%; margin: 10px 0; }
        button { padding: 10px 20px; background: #4CAF50; color: white; border: none; }
    </style>
</head>
<body>
    <h1>PDF Generator</h1>
    <form action="/gerar-pdf" method="post">
        <input type="text" name="titulo" placeholder="Título do documento">
        <textarea name="perguntas" placeholder="Digite suas perguntas (uma por linha)"></textarea>
        <button type="submit">Gerar PDF</button>
    </form>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/gerar-pdf', methods=['POST'])
def gerar_pdf_endpoint():
    try:
        api_key = get_api_key()
        perguntas = request.form['perguntas'].splitlines()
        titulo = request.form.get('titulo', 'Questionário Personalizado')
        
        perguntas = [p.strip() for p in perguntas if p.strip()] or ["Nenhuma pergunta fornecida"]
        
        html_content = f"""
        <html>
        <body>
            <h1>{titulo}</h1>
            <p>Gerado em: {datetime.now().strftime('%d/%m/%Y')}</p>
            <ol>
                {"".join(f"<li>{p}</li>" for p in perguntas)}
            </ol>
        </body>
        </html>
        """

        filename, pdf_content = generate_pdf(api_key, html_content, titulo, is_html=True)
        
        downloads_dir = Path("downloads")
        downloads_dir.mkdir(exist_ok=True)
        temp_path = downloads_dir / filename
        
        with open(temp_path, "wb") as f:
            f.write(pdf_content)
        
        return send_file(temp_path, as_attachment=True, download_name=filename)
    except Exception as e:
        return f"Erro: {str(e)}", 500

# ==============================================
# Interface CLI
# ==============================================
def display_header():
    print(f"\n{Colors.SUCCESS}=== PDF Generator v2.1 ===")
    print("Transforme suas ideias em documentos profissionais!")
    print(f"Comandos: /config, /web, /exit{Colors.END}")

def run_cli_interface():
    api_key = get_api_key()
    display_header()

    while True:
        try:
            user_input = input(f"\n{Colors.SUCCESS}Texto ou comando:{Colors.END} ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() == '/exit':
                print(f"{Colors.SUCCESS}Até logo!{Colors.END}")
                break
                
            if user_input.lower() == '/config':
                new_key = input("Nova chave API: ").strip()
                save_config(new_key)
                continue
                
            if user_input.lower() == '/web':
                logger.info("Starting web interface at http://localhost:5000")
                app.run(host='0.0.0.0', port=5000, debug=False)
                continue

            title = input("Título (opcional): ").strip() or None
            filename, pdf_content = generate_pdf(api_key, user_input, title)
            
            with open(filename, 'wb') as f:
                f.write(pdf_content)
            
            print(f"{Colors.SUCCESS}PDF gerado: {os.path.abspath(filename)}{Colors.END}")
            
        except Exception as e:
            print(f"{Colors.ERROR}Erro: {str(e)}{Colors.END}")

# ==============================================
# Ponto de Entrada
# ==============================================
if __name__ == "__main__":
    save_config(API_KEY)  # Save the provided API key initially
    if len(sys.argv) > 1 and sys.argv[1] == 'web':
        logger.info("Starting web interface")
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        run_cli_interface()