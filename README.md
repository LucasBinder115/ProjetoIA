# Projeto de Conexão com API de Geração de PDF

Este projeto implementa uma aplicação em Python que:
Recebe uma pergunta ou comando do usuário via terminal.
Envia a entrada para a API da PDF.co, que gera um PDF com o texto.
Salva o PDF localmente e exibe o caminho do arquivo ao usuário.

## Requisitos
- Python 3.8 ou superior
- Biblioteca `requests` (instale com `pip install requests`)

## Como configurar
1. **Obtenha uma chave API da PDF.co**:
   - Crie uma conta em [PDF.co](https://pdf.co/).
   - No dashboard, gera uma chave API (plano gratuito dá 300 créditos/mês) uso limitado, mas para testes ja supriu a necessidade !!

2. **Instale as dependências**:
   ```bash
   pip install requests