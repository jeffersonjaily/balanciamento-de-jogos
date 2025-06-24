from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os
import pytesseract
from PIL import Image
import random
import requests
import base64
from io import BytesIO
import re

# === CONFIGURAÇÕES ===
API_KEY = 'RGAPI-55d9d231-a982-4c48-afc2-489f4b98042b'  # Substitua pela sua chave válida
REGION = 'br1'
pytesseract.pytesseract.tesseract_cmd = r"E:\\balanciamento-de-jogos\\static\\tesseract-5.5.1\\tesseract.exe"

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# === INICIALIZAÇÃO ===
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# === DICIONÁRIO DE ELOS PARA CÁLCULO DE MMR ===
tiers = {
    'IRON': 1, 'BRONZE': 2, 'SILVER': 3, 'GOLD': 4,
    'PLATINUM': 5, 'EMERALD': 6, 'DIAMOND': 7,
    'MASTER': 8, 'GRANDMASTER': 9, 'CHALLENGER': 10
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calcular_mmr_manual(elo):
    if not elo:
        return 0
    partes = elo.strip().upper().split()
    tier = partes[0] if partes else ''
    return tiers.get(tier, 0) * 100

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nomes_texto = request.form.get("nomes", "")
        jogadores = []

        erro = None
        separadores = r'[|\-_/.,]'  # todos os separadores permitidos

        for linha in nomes_texto.splitlines():
            partes = re.split(separadores, linha)
            partes = [p.strip() for p in partes if p.strip()]
            if len(partes) >= 2:
                nome, elo = partes[0], partes[1]
                jogadores.append({
                    'nome': nome,
                    'elo': elo,
                    'vitorias': 0,
                    'mmr': calcular_mmr_manual(elo)
                })
            elif len(partes) == 1:
                jogadores.append({
                    'nome': partes[0],
                    'elo': 'Desconhecido',
                    'vitorias': 0,
                    'mmr': 0
                })

        if not jogadores:
            erro = "Nenhum jogador foi identificado via texto ou imagem."

        return redirect(url_for('resultado', nomes="|".join([f"{j['nome']}|{j['elo']}" for j in jogadores]), erro=erro or ""))

    return render_template('index.html')

@app.route('/resultado')
def resultado():
    nomes_str = request.args.get("nomes", "")
    erro = request.args.get("erro", "")
    nomes_elo = nomes_str.split("|")
    jogadores = []

    if erro:
        return render_template("resultado.html", erro=erro, time1=[], time2=[], nomes="")

    # Monta pares (nome, elo)
    for i in range(0, len(nomes_elo), 2):
        if i + 1 < len(nomes_elo):
            nome = nomes_elo[i]
            elo = nomes_elo[i+1]
            jogadores.append({
                'nome': nome,
                'elo': elo,
                'vitorias': 0,
                'mmr': calcular_mmr_manual(elo)
            })

    jogadores.sort(key=lambda j: j['mmr'], reverse=True)
    time1, time2 = [], []
    soma1 = soma2 = 0

    for jogador in jogadores:
        if soma1 <= soma2:
            time1.append(jogador)
            soma1 += jogador['mmr']
        else:
            time2.append(jogador)
            soma2 += jogador['mmr']

    return render_template("resultado.html", time1=time1, time2=time2, nomes=nomes_str, erro="")

if __name__ == '__main__':
    app.run(debug=True)
