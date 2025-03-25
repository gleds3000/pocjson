from flask import Flask, jsonify
from flask import render_template
from flask import request
import json

app = Flask(__name__)

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
    return render_template('start.html')

##Rota calcula IMC
@app.route('/api', methods=['POST'])
def valida_imc():
    print("rota imc")
    resp = request.get_json()
    peso = resp["peso"]
    altura = resp["altura"]
    resultado =  round(peso / altura ** 2,2)
    return jsonify({"resultado": resultado})


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
    app.run(debug=True)
