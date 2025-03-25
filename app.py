from flask import Flask, send_file, request, render_template
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)

# Pasta de downloads
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Função para gerar PDF
def gerar_pdf(nome_arquivo, perguntas, titulo="Questionário para Prova"):
    caminho = os.path.join(DOWNLOAD_FOLDER, nome_arquivo)
    c = canvas.Canvas(caminho, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 780, titulo)  # Título maior
    c.setFont("Helvetica", 12)
    y = 750
    for i, pergunta in enumerate(perguntas, 1):
        c.drawString(100, y, f"{i}. {pergunta}")
        y -= 30  # Mais espaço entre perguntas
    c.save()
    return caminho

# Rota principal
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Rota para gerar o PDF
@app.route('/gerar-pdf', methods=['GET', 'POST'])
def gerar_pdf_endpoint():
    perguntas = [
        "Qual é a capital do Brasil?",
        "Quanto é 2 + 2?",
        "Quem descobriu a América?"
    ]
    
    if request.method == 'POST':
        if 'perguntas' in request.form:
            perguntas = request.form['perguntas'].splitlines()
        elif request.json and isinstance(request.json, dict) and 'perguntas' in request.json:
            perguntas = request.json['perguntas']

    nome_arquivo = "questionario.pdf"
    caminho_pdf = gerar_pdf(nome_arquivo, perguntas)
    return send_file(caminho_pdf, as_attachment=True)

# Inicia o servidor
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
