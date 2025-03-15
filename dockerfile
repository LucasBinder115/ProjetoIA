# Use uma imagem base do Python para Linux (recomendado)
FROM python:3.10-slim

# Instale dependências do sistema (opcional, mas útil para bibliotecas como transformers)
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Defina o diretório de trabalho
WORKDIR /app

# Copie os arquivos do projeto
COPY . .

# Instale as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponha a porta do Flask
EXPOSE 5000

# Comando para iniciar a aplicação
CMD ["python", "backend/app.py"]