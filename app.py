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

# === Initial Setup ===
nltk.download('punkt')
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/imagens'  # Folder for uploaded images

# === Helper Functions ===
def buscar_questoes(tema):
    url = f"https://opentdb.com/api.php?amount=10&category=18&type=multiple"
    response = requests.get(url)
    return response.json()['results'] if response.status_code == 200 else []

def generate_question(prompt, num_questions=10):
    gerador = pipeline('text-generation', model='EleutherAI/gpt-neo-1.3B')
    questions = []
    for i in range(num_questions):
        # Ajusta o prompt para gerar perguntas numeradas
        input_prompt = f"Crie a questão {i+1} sobre {prompt}. Formato: '{i+1}. [pergunta]'"
        generated = gerador(input_prompt, max_length=100, num_return_sequences=1)[0]['generated_text']
        # Extrai a pergunta gerada (assumindo que o modelo segue o formato)
        question = generated.split(f"{i+1}. ")[-1].strip()
        questions.append({'question': question})
    return questions

# === PDF Creation Functions ===
def criar_pdf(caminho_imagem=None, questoes=None):
    pdf = SimpleDocTemplate("prova.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    conteudo = []

    conteudo.append(Paragraph("Ebook de Questões para Estudo", styles['Title']))
    conteudo.append(Spacer(1, 12))

    if caminho_imagem:
        try:
            imagem = Image(caminho_imagem, width=4*inch, height=3*inch)
            conteudo.append(imagem)
            conteudo.append(Spacer(1, 12))
        except Exception as e:
            print(f"Erro ao carregar a imagem: {e}")
            conteudo.append(Paragraph("<i>Imagem não disponível</i>", styles['Italic']))
            conteudo.append(Spacer(1, 12))

    if questoes:
        for i, questao in enumerate(questoes, start=1):
            questao_formatada = Paragraph(f"{i}. {questao['question']}", styles['BodyText'])
            conteudo.append(questao_formatada)
            conteudo.append(Spacer(1, 12))

    pdf.build(conteudo)

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

    # Se o usuário fornecer um prompt, gerar questões personalizadas
    if prompt:
        questoes = generate_question(prompt)
    else:
        questoes = buscar_questoes("default")  # Fallback para API ou questões padrão

    if formato == "pdf":
        criar_pdf(caminho_imagem, questoes)
        return send_file('prova.pdf', as_attachment=True)
    elif formato == "docx":
        criar_docx(caminho_imagem, questoes)
        return send_file('prova.docx', as_attachment=True)
    elif formato == "epub":
        criar_epub(caminho_imagem, questoes)
        return send_file('prova.epub', as_attachment=True)
    else:
        return "Formato inválido."

# === Main Execution ===
if __name__ == '__main__':
    app.run(debug=True)