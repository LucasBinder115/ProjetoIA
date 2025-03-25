from flask import Flask, send_file, request, render_template
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def gerar_pdf(nome_arquivo, perguntas):
    caminho = os.path.join(DOWNLOAD_FOLDER, nome_arquivo)
    c = canvas.Canvas(caminho, pagesize=letter)
    c.setFont("Helvetica", 12)
    c.drawString(100, 750, "Questionário para Prova")
    y = 720
    for i, pergunta in enumerate(perguntas, 1):
        c.drawString(100, y, f"{i}. {pergunta}")
        y -= 20
    c.save()
    return caminho

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

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
        elif request.json and 'perguntas' in request.json:
            perguntas = request.json['perguntas']
    
    nome_arquivo = "questionario.pdf"
    caminho_pdf = gerar_pdf(nome_arquivo, perguntas)
    return send_file(caminho_pdf, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)