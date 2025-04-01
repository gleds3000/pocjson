from flask import Flask, jsonify, redirect, url_for
from flask import render_template
from flask import request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy



import json

app = Flask(__name__)
CORS(app)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Meublog.sqlite3"

db = SQLAlchemy(app)

class Post(db.Model): 
    id = db.Column(db.Integer, primary_key=True) 
    
    peso = db.Column(db.String())
    altura = db.Column(db.String())
    

@app.route('/validajson', methods=['POST'])
def valida_json():
    # Obtém os dados brutos da requisição
    dados = request.get_data(as_text=True)
    
    if not dados:
        return jsonify({
            "status": "erro",
            "mensagem": "Nenhum dado foi enviado",
            "json_valido": False
        }), 400
    
    try:
        # Tenta fazer o parse do JSON
        json.loads(dados)
        return jsonify({
            "status": "sucesso",
            "mensagem": "O conteúdo é um JSON válido",
            "json_valido": True
        })
    except json.JSONDecodeError as e:
        return jsonify({
            "status": "erro",
            "mensagem": f"O conteúdo não é um JSON válido: {str(e)}",
            "json_valido": False
        }), 400


# Rota para a página inicial
@app.route("/")
def home():
    return render_template('index.html')


db.create_all()

#app.run(debug=True)

@app.route('/post/add/', methods='POST')
def add_post():
    try:
        form = request.form
        post = Post(title=form['altura'], name=form['peso'])
        db.session.add(post)
        db.session.commit()
    except:
        print('erro')
    return redirect(url_for("home"))

@app.route('/')
def home():
    posts = Post.query.all()
    return render_template("home.html", posts=posts)

##Rota calcula IMC
#@app.route('/api', methods=['POST'])
# def valida_imc():
    
#     print("rota imc")
#     form = request.form
#     post = Post(title=form['peso'], name=form['altura'])
#     print(post)
#     resp = request.get_json()
#     peso = resp["peso"]
#     altura = resp["altura"]
#     resultado =  round(peso / altura ** 2,2)
#     response = jsonify({"resultado": resultado})
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     return response

@app.route('/api', methods=['POST'])  # Garanta que aceita POST
def calcular_imc():
    dados = request.get_json()  # Pega os dados JSON enviados
    peso = dados.get('peso')
    altura = dados.get('altura')
    
    if peso is None or altura is None:
        return jsonify({"erro": "Dados incompletos"}), 400
    
    imc = peso / (altura ** 2)
    return jsonify({"resultado": round(imc, 2)})  # Retorna o IMC com 2 casas decimais

## Rota para validar JSON
@app.route("/valida", methods=['POST'])
def valida_json2():
      print("iniciando")
      try:
          
# #         # Obtém o JSON da requisição
          json_data = request.get_json()
          print("acesso try")
# #         # Verifica se o JSON é válido
          if isinstance(json_data, dict):
              return {"status": "sucesso", "mensagem": "JSON válido"}, 200
          else:
              return {"status": "erro", "mensagem": "JSON inválido"}, 400
      except Exception as e:
          return {"status": "erro", "mensagem": str(e)}, 400

## Rota para teste de validação
# @app.route("/valida/<string:json>")
# def testa_json(json):
#     try:
#         # Converte a string JSON em um dicionário
#         import json as json_parser
#         teste = request.form
#         json_data = json_parser.loads(json)
#         return {"status": "sucesso", "mensagem": "JSON válido"}, 200
#     except Exception as e:
#         return {"status": "erro", "mensagem": str(e)}, 400

if __name__ == "__main__":
    #app.run(debug=True)
    app.run(port=8000)  # Roda na porta 8000 (igual ao frontend)
