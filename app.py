from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os
import pytesseract
from PIL import Image
import random

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Atualize esse caminho se necessário

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extrair_nomes_da_imagem(caminho):
    try:
        img = Image.open(caminho)
        texto = pytesseract.image_to_string(img, lang='eng')
        linhas = [linha.strip() for linha in texto.split('\n') if linha.strip()]
        nomes = list(set(linhas))  # remove duplicados
        return nomes
    except Exception as e:
        print(f"Erro ao ler imagem: {e}")
        return []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nomes_texto = request.form.get("nomes", "")
        jogadores = [n.strip() for n in nomes_texto.splitlines() if n.strip()]

        imagem_filename = None
        if 'imagem' in request.files:
            imagem = request.files['imagem']
            if imagem and allowed_file(imagem.filename):
                filename = secure_filename(imagem.filename)
                imagem.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                imagem_filename = filename

                jogadores_img = extrair_nomes_da_imagem(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                jogadores.extend(j for j in jogadores_img if j not in jogadores)

        if not jogadores:
            return render_template('index.html', erro="Nenhum jogador foi identificado.")

        return redirect(url_for('resultado', nomes="|".join(jogadores)))

    return render_template('index.html')

@app.route('/resultado')
def resultado():
    nomes_str = request.args.get("nomes", "")
    jogadores = nomes_str.split("|") if nomes_str else []

    random.shuffle(jogadores)
    meio = len(jogadores) // 2
    time1 = jogadores[:meio]
    time2 = jogadores[meio:]

    return render_template("resultado.html", time1=time1, time2=time2, nomes="|".join(jogadores))

if __name__ == '__main__':
    app.run(debug=True)
