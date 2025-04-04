from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import random
import string


# Inicializa o FlasK
app = Flask(__name__)

# Conectar ao MongoDB (substitua pela URL do MongoDB Atlas se necessário)
uri = "mongodb+srv://dbUser:db987654@cluster0.7cnqj43.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))


def generate_identifier():
    # Gera 3 números aleatórios
    numeros = random.choices(string.digits, k=3)
    
    # Gera 3 letras minúsculas aleatórias
    letras = random.choices(string.ascii_lowercase, k=3)
    
    # Junta os números e letras em uma única lista
    identificador_lista = numeros + letras
    
    # Embaralha a lista
    random.shuffle(identificador_lista)
    
    # Junta a lista embaralhada de volta em uma string
    identificador = ''.join(identificador_lista)
    
    return identificador


@app.route('/login', methods=['GET'])
def login():
    db = client['Users']  # Substitua pelo nome do seu banco de dados
    collection = db['Users']   # Substitua pelo nome da sua coleção

    # Recebe o login e senha do usuário
    login = request.args.get('login')
    password = request.args.get('pwd')

    print(login)
    print(password)
    
    # Verifica se o usuário existe
    user = collection.find_one({'login': login})
    
    print("User: ", user)

    if user != None:
        if user['password'] == password:
            return jsonify({"message": "Login bem-sucedido!", "flag": True}), 200
    else:
        user = collection.find_one({'email': login})
        if user != None:
            if user['password'] == password:
                return jsonify({"message": "Login bem-sucedido!", "flag": True}), 200
        else:
            return jsonify({"message": "Login ou senha inválidos!", "flag": False}), 401

@app.route('/register', methods=['POST'])
def register():
    db = client['Users']  # Substitua pelo nome do seu banco de dados
    collection = db['Users']   # Substitua pelo nome da sua coleção

    # Recebe os dados do usuário
    data = request.get_json()
    nome = data.get('nome')
    login = data.get('login')
    password = data.get('pwd')
    email = data.get('email')
    
    print("Recebi uma requisição")

    # Verifica se o login ou email já existem
    if collection.find_one({'login': login}):

        print("Erro: Login já existe!")
        return jsonify({"message": "Login já existe!"}), 400
    if collection.find_one({'email': email}):
        print("Erro: Email já registrado!")
        return jsonify({"message": "Email já registrado!"}), 400
    
    # Cria o novo usuário e insere no banco de dados
    new_user = {
        'nome': nome,
        'login': login,
        'password': password,
        'email': email
    }
    
    collection.insert_one(new_user)
    
    print("Usuário Inserido")
    return jsonify({"message": "Usuário registrado com sucesso!"}), 201

@app.route('/register/group', methods=['POST'])
def register_group():
    db = client['groups']  # Substitua pelo nome do seu banco de dados
    collection = db['groups']   # Substitua pelo nome da sua coleção

    # Recebe os dados do usuário
    data = request.get_json()
    name = data.get('group_name')
    description = data.get('group_description')
    pwd = data.get('pwd')
    n_participants = data.get('group_number_participants')
    
    unique_id = generate_identifier()
    print(unique_id)
    while collection.find_one({'unique_id': unique_id}) != None:
        unique_id = generate_identifier()
        print(unique_id)
    
    print("Recebi uma requisição")

    # Verifica se o login ou email já existem
    if collection.find_one({'name': name}):
        print("Erro: Grupo já existe!")
        return jsonify({"message": "Grupo com esse nome já existe!"}), 400


    
    # Cria o novo usuário e insere no banco de dados
    new_group = {
        'id': unique_id,
        'name': name,
        'description': description,
        'pwd': pwd,
        'n_participants': n_participants
    }
    
    collection.insert_one(new_group)
    
    print("Group Criado")
    return jsonify({"message": "Grupo criado com sucesso!"}), 200

if __name__ == '__main__':
    app.run(debug=True)