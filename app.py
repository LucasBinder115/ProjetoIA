from flask import Flask, send_file, request, render_template
import requests
import os

app = Flask(__name__)

# Configuração da API do PDF.co
PDF_CO_API_KEY = "binderlucas356@gmail.com_8oCVJnzbaGKvaF1BQizIYF8x8y2k2rZxFOjfusc9hZcOzA9I5qDFUlcBZVdWlfFt"  # Coloque sua chave da PDF.co
PDF_CO_ENDPOINT = "https://api.pdf.co/v1/pdf/convert/from/html"

# Rota inicial (página web)
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Rota para gerar e baixar o PDF usando a API externa
@app.route('/gerar-pdf', methods=['POST'])
def gerar_pdf_endpoint():
    perguntas = request.form['perguntas'].splitlines()
    titulo = request.form.get('titulo', 'Questionário Personalizado')
    if not perguntas or all(p.strip() == "" for p in perguntas):
        perguntas = ["Nenhuma pergunta fornecida. Exemplo: Qual é 1 + 1?"]

    # Criar o HTML simples para enviar à API
    html_content = f"""
    <html>
    <body>
        <h1>{titulo}</h1>
        <p>Gerado em: 24/03/2025</p>
        <ol>
            {"".join(f"<li>{p}</li>" for p in perguntas)}
        </ol>
    </body>
    </html>
    """

    # Dados para a requisição à API
    payload = {
        "html": html_content,
        "name": "questionario.pdf",
        "async": False  # Geração síncrona pra simplicidade
    }
    headers = {
        "x-api-key": PDF_CO_API_KEY,
        "Content-Type": "application/json"
    }

    # Fazer a requisição à API
    response = requests.post(PDF_CO_ENDPOINT, json=payload, headers=headers)
    
    if response.status_code == 200:
        pdf_url = response.json()["url"]
        pdf_response = requests.get(pdf_url)
        
        # Salvar o PDF temporariamente
        temp_path = "downloads/questionario.pdf"
        os.makedirs("downloads", exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(pdf_response.content)
        
        return send_file(temp_path, as_attachment=True)
    else:
        return f"Erro na API: {response.text}", 500
# Inicia o servidor
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
