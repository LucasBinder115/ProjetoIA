from flask import Flask, send_file, request, render_template
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from datetime import datetime

app = Flask(__name__)

# Pasta de downloads
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Função para gerar PDF
def gerar_pdf(nome_arquivo, perguntas, titulo="Questionário Personalizado"):
    caminho = os.path.join(DOWNLOAD_FOLDER, nome_arquivo)
    c = canvas.Canvas(caminho, pagesize=letter)
    
    # Cabeçalho
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 780, titulo)
    c.setFont("Helvetica", 10)
    c.drawString(100, 760, f"Gerado em: {datetime.now().strftime('%d/%m/%Y')}")
    
    # Perguntas
    c.setFont("Helvetica", 12)
    y = 730
    for i, pergunta in enumerate(perguntas, 1):
        c.drawString(100, y, f"{i}. {pergunta}")
        y -= 20
        if y < 50:  # Nova página se necessário
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 750
    c.save()
    return caminho

# Rota principal
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Rota para gerar o PDF
@app.route('/gerar-pdf', methods=['POST'])
def gerar_pdf_endpoint():
    perguntas = request.form.get('perguntas', "").splitlines()
    titulo = request.form.get('titulo', 'Questionário Personalizado')  # Título padrão se não for fornecido

    # Se as perguntas estiverem vazias, adiciona uma mensagem padrão
    if not perguntas or all(p.strip() == "" for p in perguntas):
        perguntas = ["Nenhuma pergunta fornecida. Exemplo: Qual é 1 + 1?"]
    
    nome_arquivo = "questionario.pdf"
    caminho_pdf = gerar_pdf(nome_arquivo, perguntas, titulo)
    return send_file(caminho_pdf, as_attachment=True)

# Inicia o servidor
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
