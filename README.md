Instruções para Configuração do ProjetoIA

Pré-requisitos
Antes de começar, certifique-se de ter os seguintes programas instalados:

Python 3.9+: Download Python
Docker: Download Docker Desktop
Docker Compose: Normalmente vem com o Docker Desktop, mas confira a versão com docker-compose --version. Caso precise, veja Docker Compose Install.
Git: Para clonar o repositório (opcional) - Download Git.
Passo 1: Clonar o Repositório (Opcional)
Se o projeto estiver em um repositório Git, clone-o:

bash

Recolher

Encapsular

Copiar
git clone <https://github.com/LucasBinder115/ProjetoIA.git>
cd <ProjetoIA>
Caso contrário, apenas coloque os arquivos na pasta do projeto.

Passo 2: Instalar Dependências Python
O projeto usa várias bibliotecas Python listadas no requirements.txt. Para instalá-las:

Crie um ambiente virtual (opcional, mas recomendado):
bash

Recolher

Encapsular

Copiar
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
Instale as dependências:
bash

Recolher

Encapsular

Copiar
pip install -r requirements.txt
Aqui está a lista de pacotes principais que você precisa (caso não tenha um requirements.txt pronto):

flask
celery
redis
requests
nltk
reportlab
python-docx
ebooklib
Você pode instalá-los manualmente com:

bash

Recolher

Encapsular

Copiar
pip install flask celery redis requests nltk reportlab python-docx ebooklib
Baixe os dados do NLTK (necessário para tokenização):
bash

Recolher

Encapsular

Copiar
python -c "import nltk; nltk.download('punkt')"
Passo 3: Configurar Redis
O projeto usa Redis como broker para o Celery. Você pode instalá-lo localmente ou usar Docker:

Localmente:
Baixe e instale o Redis: Redis Downloads
Inicie o servidor Redis:
bash

Recolher

Encapsular

Copiar
redis-server
Com Docker (recomendado):
Puxe a imagem oficial do Redis:
bash

Recolher

Encapsular

Copiar
docker pull redis:7-alpine
Rode o Redis em um contêiner:
bash

Recolher

Encapsular

Copiar
docker run -d -p 6379:6379 --name redis redis:7-alpine
Passo 4: Configurar o Docker para o Projeto
O projeto pode ser executado com Docker Compose para gerenciar Flask, Celery e Redis juntos.

Certifique-se de ter um arquivo docker-compose.yml. Um exemplo básico seria:
yaml

Recolher

Encapsular

Copiar
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - .:/app
    depends_on:
      - redis
  worker:
    build: .
    command: celery -A app:celery worker --loglevel=info
    volumes:
      - .:/app
    depends_on:
      - redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
Crie um Dockerfile na raiz do projeto (se não tiver um):
dockerfile

Recolher

Encapsular

Copiar
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["flask", "run", "--host=0.0.0.0"]
Construa e inicie os contêineres:
bash

Recolher

Encapsular

Copiar
docker-compose build
docker-compose up
Para rodar em background: docker-compose up -d.
Para parar: docker-compose down.
Passo 5: Configurar o Gotenberg (Opcional)
O projeto usa Gotenberg para converter HTML em PDF. Para configurá-lo com Docker:

Puxe a imagem do Gotenberg:
bash

Recolher

Encapsular

Copiar
docker pull gotenberg/gotenberg:7
Rode o Gotenberg:
bash

Recolher

Encapsular

Copiar
docker run -d -p 3000:3000 --name gotenberg gotenberg/gotenberg:7
Passo 6: Executar o Projeto
Sem Docker:
Ative o ambiente virtual (se criado): source venv/bin/activate.
Inicie o Flask:
bash

Recolher

Encapsular

Copiar
flask run
Em outro terminal, inicie o Celery:
bash

Recolher

Encapsular

Copiar
celery -A app:celery worker --loglevel=info
Com Docker: Use o docker-compose up como descrito acima.
Notas Finais
O Flask estará disponível em http://127.0.0.1:5000.
Certifique-se de que Redis e Gotenberg (se usado) estejam rodando antes de iniciar o Flask e o Celery.
Se houver erros, verifique os logs com docker logs <nome_do_container> (ex.: docker logs redis).
Qualquer dúvida, é só perguntar!

Explicação
Dependências: Listei as bibliotecas principais que aparecem no seu app.py (Flask, Celery, Redis, etc.).
Docker: Incluí instruções básicas para configurar Flask, Celery e Redis com Docker Compose, além do Gotenberg, que você usa para PDFs.
Simplicidade: Mantive curto e direto, só com o que o professor precisa para rodar.
