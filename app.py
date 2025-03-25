from flask import Flask, send_file, request
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)

# Pasta para salvar os PDFs temporariamente
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Função para gerar o PDF
def gerar_pdf(nome_arquivo, perguntas):
    caminho = os.path.join(DOWNLOAD_FOLDER, nome_arquivo)
    c = canvas.Canvas(caminho, pagesize=letter)
    c.setFont("Helvetica", 12)
    
    # Título do questionário
    c.drawString(100, 750, "Questionário para Prova")
    
    # Adicionar perguntas ao PDF
    y = 720  # Posição vertical inicial
    for i, pergunta in enumerate(perguntas, 1):
        c.drawString(100, y, f"{i}. {pergunta}")
        y -= 20  # Espaço entre perguntas
    
    c.save()
    return caminho

# Rota principal da API
@app.route('/gerar-pdf', methods=['GET', 'POST'])
def gerar_pdf_endpoint():
    # Lista de perguntas (pode vir de um formulário ou ser fixa)
    perguntas = [
        "Qual é a capital do Brasil?",
        "Quanto é 2 + 2?",
        "Quem descobriu a América?"
    ]
    
    # Se vierem perguntas personalizadas via POST, usar isso
    if request.method == 'POST':
        dados = request.json
        if dados and 'perguntas' in dados:
            perguntas = dados['perguntas']
    
    nome_arquivo = "questionario.pdf"
    caminho_pdf = gerar_pdf(nome_arquivo, perguntas)
    
    # Enviar o PDF para download
    return send_file(caminho_pdf, as_attachment=True)

# Rodar o servidor
if __name__ == '__main__':
    app.run(debug=True)