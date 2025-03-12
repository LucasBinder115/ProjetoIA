from flask import Flask, render_template, send_file, request
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Image, PageBreak
from reportlab.lib.units import inch
from docx import Document
from ebooklib import epub

# Cria uma instância do Flask
app = Flask(__name__)

# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para a página de escolha de formato
@app.route('/escolher_formato')
def escolher_formato():
    return render_template('escolher_formato.html')

# Rota para gerar o ebook
@app.route('/gerar_ebook', methods=['POST'])
def gerar_ebook():
    formato = request.form.get('formato')  # Obtém o formato escolhido

    if formato == "pdf":
        criar_pdf()
        return send_file('prova.pdf', as_attachment=True)
    elif formato == "docx":
        criar_docx()
        return send_file('prova.docx', as_attachment=True)
    elif formato == "epub":
        criar_epub()
        return send_file('prova.epub', as_attachment=True)
    else:
        return "Formato inválido."

# Função para criar o PDF
def criar_pdf():
    pdf = SimpleDocTemplate("prova.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    conteudo = []

    titulo = Paragraph("Ebook de Questões para Estudo", styles['Title'])
    conteudo.append(titulo)
    conteudo.append(Spacer(1, 12))

    questoes_por_tema = {
        "Matemática": {
            "imagem": "imagens/matematica.jpg",
            "questoes": [
                "1. Qual é a fórmula para calcular a área de um círculo?",
                "2. Explique o Teorema de Pitágoras."
            ]
        },
        "História": {
            "imagem": "imagens/historia.jpg",
            "questoes": [
                "1. Quais foram as causas da Revolução Francesa?",
                "2. Descreva o período da Revolução Industrial."
            ]
        },
        "Biologia": {
            "imagem": "imagens/biologia.jpg",
            "questoes": [
                "1. O que é fotossíntese e qual a sua importância?",
                "2. Explique a estrutura do DNA."
            ]
        }
    }

    for tema, dados in questoes_por_tema.items():
        tema_formatado = Paragraph(f"<b>Tema: {tema}</b>", styles['Heading2'])
        conteudo.append(tema_formatado)
        conteudo.append(Spacer(1, 12))

        imagem = Image(dados["imagem"], width=4*inch, height=3*inch)
        conteudo.append(imagem)
        conteudo.append(Spacer(1, 12))

        for questao in dados["questoes"]:
            questao_formatada = Paragraph(questao, styles['BodyText'])
            conteudo.append(questao_formatada)
            conteudo.append(Spacer(1, 12))

        conteudo.append(PageBreak())

    pdf.build(conteudo)

# Função para criar o DOCX
def criar_docx():
    doc = Document()
    doc.add_heading('Ebook de Questões para Estudo', 0)

    questoes_por_tema = {
        "Matemática": [
            "1. Qual é a fórmula para calcular a área de um círculo?",
            "2. Explique o Teorema de Pitágoras."
        ],
        "História": [
            "1. Quais foram as causas da Revolução Francesa?",
            "2. Descreva o período da Revolução Industrial."
        ],
        "Biologia": [
            "1. O que é fotossíntese e qual a sua importância?",
            "2. Explique a estrutura do DNA."
        ]
    }

    for tema, questoes in questoes_por_tema.items():
        doc.add_heading(f'Tema: {tema}', level=1)
        for questao in questoes:
            doc.add_paragraph(questao)
        doc.add_page_break()

    doc.save('prova.docx')

# Função para criar o EPUB
def criar_epub():
    livro = epub.EpubBook()

    # Metadados do livro
    livro.set_title('Ebook de Questões para Estudo')
    livro.set_language('pt-BR')

    # Adiciona capítulos
    questoes_por_tema = {
        "Matemática": [
            "1. Qual é a fórmula para calcular a área de um círculo?",
            "2. Explique o Teorema de Pitágoras."
        ],
        "História": [
            "1. Quais foram as causas da Revolução Francesa?",
            "2. Descreva o período da Revolução Industrial."
        ],
        "Biologia": [
            "1. O que é fotossíntese e qual a sua importância?",
            "2. Explique a estrutura do DNA."
        ]
    }

    for tema, questoes in questoes_por_tema.items():
        capitulo = epub.EpubHtml(title=tema, file_name=f'{tema}.xhtml', lang='pt-BR')
        capitulo.content = f"<h1>{tema}</h1><ul>"
        for questao in questoes:
            capitulo.content += f"<li>{questao}</li>"
        capitulo.content += "</ul>"
        livro.add_item(capitulo)

    # Define a estrutura do livro
    livro.toc = tuple(questoes_por_tema.keys())
    livro.add_item(epub.EpubNav())
    livro.add_item(epub.EpubNcx())

    # Salva o EPUB
    epub.write_epub('prova.epub', livro)

# Inicia o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)