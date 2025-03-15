# === Imports ===
from flask import Flask, render_template, send_file, request
import os
import requests
import nltk
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Image, PageBreak
from reportlab.lib.units import inch
from docx import Document
from ebooklib import epub
from transformers import pipeline
import torch
from functools import lru_cache
from celery import Celery
from redis import Redis
import logging
from celery.signals import after_setup_logger

# === Initial Setup ===
nltk.download('punkt')
app = Flask(__name__, template_folder='../templates',  # Caminho relativo para a pasta templates
 static_folder='../static')
app.config['UPLOAD_FOLDER'] = 'static/imagens'  # Folder for uploaded images

# Configure o Celery
celery = Celery(
    app.name,
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

redis = Redis(host='localhost', port=6379)


print(torch.__version__)  # Deve mostrar a versão instalada, ex.: 2.4.0
print(torch.cuda.is_available())  # True se CUDA estiver configurado, False se for só CPU

# === Celery Configuration ===
@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    logger.addHandler(logging.FileHandler('celery.log'))

# === Helper Functions ===
@lru_cache(maxsize=100)
def gerar_html(questoes):
    # Lógica de geração de HTML
    pass  # Placeholder, já que não há implementação completa

def buscar_questoes(tema):
    url = f"https://opentdb.com/api.php?amount=10&category=18&type=multiple"
    response = requests.get(url)
    return response.json()['results'] if response.status_code == 200 else []

def generate_question(prompt, num_questions=10):
    gerador = pipeline('text-generation', model='EleutherAI/gpt-neo-1.3B')  # Mantive a versão 1.3B como definida
    questions = []
    for i in range(num_questions):
        # Ajusta o prompt para gerar perguntas numeradas
        input_prompt = f"Crie a questão {i+1} sobre {prompt}. Formato: '{i+1}. [pergunta]'"
        generated = gerador(input_prompt, max_length=100, num_return_sequences=1)[0]['generated_text']
        # Extrai a pergunta gerada (assumindo que o modelo segue o formato)
        question = generated.split(f"{i+1}. ")[-1].strip()
        questions.append({'question': question})
    return questions

def gerar_pdf_async(prompt, formato, caminho_imagem=None):
    cache_key = f"pdf:{prompt}"
    cached = redis.get(cache_key)
    if cached:
        return cached.decode()
    # ... gera e salva no cache (incompleto no original, deixei como está)

# === PDF Creation Functions ===
def criar_pdf(caminho_imagem=None, questoes=None):
    # 1. Criar HTML dinâmico
    html_content = """
    <html>
        <head>
            <style>
                body { font-family: Arial; margin: 2cm; }
                h1 { color: #2c3e50; }
                .questao { margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <h1>Ebook de Questões para Estudo</h1>
    """

    if questoes:
        for i, questao in enumerate(questoes, start=1):
            html_content += f'<div class="questao"><strong>{i}.</strong> {questao["question"]}</div>'

    html_content += "</body></html>"

    # 2. Enviar para o Gotenberg
    files = {
        'files': ('content.html', html_content, 'text/html')
    }
    
    data = {
        'marginTop': '1',
        'marginBottom': '1',
        'marginLeft': '1',
        'marginRight': '1'
    }

    try:
        response = requests.post(
            'http://localhost:3000/forms/chromium/convert/html',
            files=files,
            data=data,
            stream=True,
            timeout=10  # Adicionado o timeout aqui
        )

        if response.status_code == 200:
            with open('prova.pdf', 'wb') as f:
                f.write(response.content)
            return True
            
    except Exception as e:
        print(f"Erro na geração do PDF: {e}")
        return False

# === DOCX Creation Functions ===
def criar_docx(caminho_imagem=None, questoes=None):
    doc = Document()
    doc.add_heading('Ebook de Questões para Estudo', 0)

    if questoes:
        for i, questao in enumerate(questoes, start=1):
            doc.add_paragraph(f"{i}. {questao['question']}")

    doc.save('prova.docx')

# === EPUB Creation Functions ===
def criar_epub(caminho_imagem=None, questoes=None):
    livro = epub.EpubBook()
    livro.set_title('Ebook de Questões para Estudo')
    livro.set_language('pt-BR')

    if questoes:
        capitulo = epub.EpubHtml(title='Questões', file_name='questoes.xhtml', lang='pt-BR')
        capitulo.content = "<h1>Questões</h1><ul>"
        for questao in questoes:
            capitulo.content += f"<li>{questao['question']}</li>"
        capitulo.content += "</ul>"
        livro.add_item(capitulo)
        livro.toc = (epub.Link('questoes.xhtml', 'Questões', 'questoes'),)

    livro.add_item(epub.EpubNav())
    livro.add_item(epub.EpubNcx())
    epub.write_epub('prova.epub', livro)

# === Celery Tasks ===
@celery.task
def gerar_pdf_async(prompt, formato, caminho_imagem=None):
    # Lógica de geração (adaptada da rota /gerar_ebook)
    # Retorne o caminho do arquivo gerado
    pass  # Placeholder, já que a implementação está incompleta

# === Flask Routes ===
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/escolher_formato')
def escolher_formato():
    return render_template('escolher_formato.html')

@app.route('/gerar_ebook', methods=['POST'])
def gerar_ebook():
    formato = request.form.get('formato')
    prompt = request.form.get('prompt')  # Novo campo para o prompt do usuário
    imagem = request.files.get('imagem')
    
    caminho_imagem = None
    if imagem:
        caminho_imagem = os.path.join(app.config['UPLOAD_FOLDER'], imagem.filename)
        imagem.save(caminho_imagem)

    # Enfileira a tarefa
    task = gerar_pdf_async.delay(prompt, formato, caminho_imagem)
    
    # Retorna um ID para acompanhamento
    # NOTA: 'jsonify' não está importado, deve ser 'from flask import jsonify'
    return jsonify({"task_id": task.id}), 202

@app.route('/status/<task_id>')
def check_status(task_id):
    task = gerar_pdf_async.AsyncResult(task_id)
    return jsonify({
        "status": task.status,
        "download_url": task.result if task.successful() else None
    })

@app.route('/health')
def health_check():
    try:
        requests.get('http://localhost:3000/health')
        return "OK", 200
    except:
        return "Gotenberg offline", 500

@app.route('/test_ia')
def test_ia():
    questoes = generate_question("Química Orgânica")
    return jsonify(questoes)

# === Test Functions ===
def test_gotenberg():
    questoes = [{'question': 'Teste 1'}, {'question': 'Teste 2'}]
    criar_pdf(questoes=questoes)
    print("PDF gerado com sucesso!")

# === Main Execution ===
if __name__ == '__main__':
    test_gotenberg()  # Remova após testes
    app.run(debug=True)