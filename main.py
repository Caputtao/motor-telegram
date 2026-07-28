# Arquivo: main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from telethon import TelegramClient
import asyncio
import requests
from bs4 import BeautifulSoup
import os

# ==========================================
# 1. COLOQUE SUAS CHAVES DO TELEGRAM AQUI
# ==========================================
API_ID = 38969303  # Exemplo: 1234567 (Sem aspas)
API_HASH = '8948ebc80c092365ff2cc0560a3cde56'  # Exemplo: 'a1b2c3d4e5f6g7h8' (Com aspas)
BOT_USERNAME = '@SantSearchhBot'

# ==========================================
# 2. CONFIGURAÇÃO DO SERVIDOR E TELEGRAM
# ==========================================
app = FastAPI()

# Libera o acesso para o seu Google Sites conseguir ler os dados
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cria a conexão do Telegram
client = TelegramClient('sessao_vendas', API_ID, API_HASH)

# ==========================================
# 3. O MOTOR DE BUSCA (A ROTA PRINCIPAL)
# ==========================================
@app.get("/consultar/{cpf}")
async def consultar_cpf(cpf: str):
    # Conecta ao Telegram
    await client.connect()
    
    # Verifica se a conta já foi validada no painel do Render
    if not await client.is_user_authorized():
        return {"sucesso": False, "erro": "Telegram não conectado. Acesse a aba 'Logs' no Render para digitar o código de verificação."}

    try:
        # Passo A: Manda a mensagem para o bot
        await client.send_message(BOT_USERNAME, f'/cpf {cpf}')
        
        # Passo B: Aguarda 5 segundos (tempo para o bot pensar e gerar o link)
        await asyncio.sleep(5)
        
        # Passo C: Puxa as últimas mensagens para ler a resposta
        messages = await client.get_messages(BOT_USERNAME, limit=2)
        
        target_url = None
        
        # Passo D: Varre a mensagem procurando o botão "RESULTADO AQUI"
        for msg in messages:
            if msg.reply_markup and hasattr(msg.reply_markup, 'rows'):
                for row in msg.reply_markup.rows:
                    for button in row.buttons:
                        # Procura o botão independente de letras maiúsculas/minúsculas
                        if 'RESULTADO AQUI' in button.text.upper():
                            target_url = button.url
                            break
            if target_url:
                break
                        
        if not target_url:
            return {"sucesso": False, "erro": "Botão 'RESULTADO AQUI' não encontrado. O sistema pode estar lento."}
            
        # Passo E: Acessa o site que estava escondido no botão
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        resposta = requests.get(target_url, headers=headers)
        
        # Passo F: Raspa o texto puro do site (como se fosse um "Copiar Tudo")
        soup = BeautifulSoup(resposta.text, 'html.parser')
        texto_limpo = soup.get_text(separator='\n', strip=True)
        
        # Retorna o texto extraído com sucesso
        return {"sucesso": True, "dados": texto_limpo}

    except Exception as e:
        return {"sucesso": False, "erro": f"Falha interna no motor: {str(e)}"}

# Para manter a conexão do Telethon viva no Render
@app.on_event("startup")
async def startup_event():
    await client.connect()
