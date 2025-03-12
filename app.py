from flask import Flask, render_template, send_file

app = Flask(__name__)

# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para gerar o PDF
@app.route('/gerar_ebook')
def gerar_ebook():
    # Chama a função para criar o PDF
    criar_pdf()
    # Envia o PDF para o usuário
    return send_file('prova.pdf', as_attachment=True)

# Função para criar o PDF
def criar_pdf():
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    # Cria o PDF
    c = canvas.Canvas("prova.pdf", pagesize=letter)
    width, height = letter

    # Configurações iniciais
    titulo = "Ebook de Questões para Estudo"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, height - 40, titulo)
    c.setFont("Helvetica", 12)

    # Posição inicial do texto
    y = height - 80

    # Questões pré-definidas
    questoes = [
        "1. Qual é a fórmula para calcular a área de um círculo?",
        "2. Explique o Teorema de Pitágoras.",
        "3. Quais foram as causas da Revolução Francesa?",
        "4. Descreva o processo de fotossíntese.",
        "5. O que é a Lei de Newton?"
    ]

    # Adiciona as questões ao PDF
    for questao in questoes:
        c.drawString(60, y, questao)
        y -= 20
        if y < 40:  # Nova página se o texto ultrapassar o limite
            c.showPage()
            y = height - 40

    # Salva o PDF
    c.save()

# Inicia o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)