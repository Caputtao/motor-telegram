from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio
import requests
from bs4 import BeautifulSoup
import os
import datetime

# ==========================================
# 1. SUAS CHAVES DO TELEGRAM
# ==========================================
API_ID = 38969303         # Apenas números, sem aspas
API_HASH = '8948ebc80c092365ff2cc0560a3cde56'   # Com aspas

BOT_USERNAME = '@SantSearchhBot'
CHAVE_FIXA = os.environ.get('CHAVE_TELEGRAM', '')
LIMITE_DIARIO = 25

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

client = TelegramClient(StringSession(CHAVE_FIXA), API_ID, API_HASH)

# ==========================================
# FUNÇÃO: CONTAR CONSULTAS DO DIA
# ==========================================
async def contar_consultas_hoje():
    # Pega a data de hoje no fuso horário do Brasil (UTC-3)
    fuso_br = datetime.timezone(datetime.timedelta(hours=-3))
    hoje = datetime.datetime.now(fuso_br).date()
    
    contador = 0
    # Lê o histórico recente com o bot
    async for msg in client.iter_messages(BOT_USERNAME):
        data_msg = msg.date.astimezone(fuso_br).date()
        
        # Se a mensagem for de ontem para trás, para de contar
        if data_msg < hoje:
            break
            
        # Conta apenas as mensagens que nós enviamos e que começam com /cpf
        if msg.out and msg.text and msg.text.startswith('/cpf'):
            contador += 1
            
    return contador

# ==========================================
# ROTA: VERIFICAR PLACAR
# ==========================================
@app.get("/status")
async def verificar_status():
    if not client.is_connected():
        await client.connect()
    
    try:
        usadas = await contar_consultas_hoje()
        return {"sucesso": True, "usadas": usadas, "limite": LIMITE_DIARIO}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

# ==========================================
# 2. O MOTOR DE BUSCA (A ROTA PRINCIPAL)
# ==========================================
@app.get("/consultar/{cpf}")
async def consultar_cpf(cpf: str):
    if not client.is_connected():
        await client.connect()
    
    if not await client.is_user_authorized():
        return {"sucesso": False, "erro": "Sessão inválida."}

    # VERIFICA O LIMITE ANTES DE PESQUISAR
    usadas = await contar_consultas_hoje()
    if usadas >= LIMITE_DIARIO:
        return {"sucesso": False, "erro": f"LIMITE ATINGIDO! Você já fez {usadas} consultas hoje. Volte amanhã."}

    try:
        await client.send_message(BOT_USERNAME, f'/cpf {cpf}')
        await asyncio.sleep(5)
        
        messages = await client.get_messages(BOT_USERNAME, limit=2)
        target_url = None
        
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
            return {"sucesso": False, "erro": "Botão não encontrado. Bot lento."}
            
        headers = {'User-Agent': 'Mozilla/5.0'}
        resposta = requests.get(target_url, headers=headers)
        
        soup = BeautifulSoup(resposta.text, 'html.parser')
        texto_limpo = soup.get_text(separator='\n', strip=True)
        
        return {"sucesso": True, "dados": texto_limpo}

    except Exception as e:
        return {"sucesso": False, "erro": f"Erro interno: {str(e)}"}

@app.on_event("startup")
async def startup_event():
    await client.connect()
