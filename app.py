from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

@app.route('/')
def home():
    return app.send_static_file('index.html')

# Rota para POST /api
@app.route('/api', methods=['POST'])  
def calcular_imc():
    dados = request.get_json()
    peso = dados.get('peso')
    altura = dados.get('altura')

    if not peso or not altura:
        return jsonify({"erro": "Dados incompletos"}), 400

    imc = peso / (altura ** 2)
    return jsonify({"resultado": round(imc, 2)})

if __name__ == '__main__':
    app.run(port=8000, debug=True)  

