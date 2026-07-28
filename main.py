from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio
import requests
from bs4 import BeautifulSoup
import os

# ==========================================
# 1. SUAS CHAVES DO TELEGRAM
# ==========================================
# Substitua pelos seus dados reais do my.telegram.org
API_ID = 38969303         # Ex: 1234567 (Apenas números, sem aspas)
API_HASH = '8948ebc80c092365ff2cc0560a3cde56'   # Ex: 'a1b2c3d4e5f6g7h8' (Sempre entre aspas)

BOT_USERNAME = '@SantSearchhBot'

# Puxa a chave de sessão gigante que você salvou no Environment do Render
CHAVE_FIXA = os.environ.get('CHAVE_TELEGRAM', '')

app = FastAPI()

# Libera o acesso para o seu Google Sites
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicia o Telegram usando a Chave Fixa (o que impede ele de deslogar)
client = TelegramClient(StringSession(CHAVE_FIXA), API_ID, API_HASH)

# ==========================================
# 2. O MOTOR DE BUSCA (A ROTA PRINCIPAL)
# ==========================================
@app.get("/consultar/{cpf}")
async def consultar_cpf(cpf: str):
    # Garante que o cliente está conectado
    if not client.is_connected():
        await client.connect()
    
    # Verifica se a sessão é válida
    if not await client.is_user_authorized():
        return {"sucesso": False, "erro": "Sessão inválida ou não autorizada. Verifique a CHAVE_TELEGRAM no Render."}

    try:
        # Passo A: Manda a mensagem para o bot
        await client.send_message(BOT_USERNAME, f'/cpf {cpf}')
        
        # Passo B: Aguarda 5 segundos (tempo para o bot processar)
        await asyncio.sleep(5)
        
        # Passo C: Puxa as últimas mensagens para ler a resposta
        messages = await client.get_messages(BOT_USERNAME, limit=2)
        target_url = None
        
        # Passo D: Varre a mensagem procurando o botão de resultado
        for msg in messages:
            if msg.reply_markup and hasattr(msg.reply_markup, 'rows'):
                for row in msg.reply_markup.rows:
                    for button in row.buttons:
                        if 'RESULTADO AQUI' in button.text.upper():
                            target_url = button.url
                            break
            if target_url:
                break
                        
        if not target_url:
            return {"sucesso": False, "erro": "Botão 'RESULTADO AQUI' não encontrado. O bot do Telegram pode estar lento."}
            
        # Passo E: Acessa o site final que estava no botão
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        resposta = requests.get(target_url, headers=headers)
        
        # Passo F: Raspa e limpa o texto do site
        soup = BeautifulSoup(resposta.text, 'html.parser')
        texto_limpo = soup.get_text(separator='\n', strip=True)
        
        return {"sucesso": True, "dados": texto_limpo}

    except Exception as e:
        return {"sucesso": False, "erro": f"Erro interno no servidor: {str(e)}"}

# Conecta ao Telegram assim que o Render ligar o servidor
@app.on_event("startup")
async def startup_event():
    await client.connect()
