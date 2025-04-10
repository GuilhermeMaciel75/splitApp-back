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

def add_group_to_user(user_login, new_group):
    users_db = client['Users']  # Substitua pelo nome do seu banco de dados de usuários
    users_collection = users_db['Users']  # Substitua pelo nome da sua coleção de usuários

    # Encontra o usuário pelo login
    print("Busca Pelo login")
    user = users_collection.find_one({'login': user_login})

    if user is None:
        print("Erro: Usuário não encontrado!")
        return False
    
    if user['groups'] == new_group:
        return True
    

    print(user)
    # Atualiza o documento do usuário adicionando o grupo
    users_collection.update_one(
        {'login': user_login},
        {'$push': {'groups': new_group}}  # Adiciona o grupo à lista de grupos do usuário
    )
    
    print("Grupo associado ao usuário")
    return True



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
        'email': email,
        'groups' : []
    }
    
    collection.insert_one(new_user)
    
    print("Usuário Inserido")
    return jsonify({"message": "Usuário registrado com sucesso!"}), 201

@app.route('/register/group', methods=['POST'])
def register_group():
    db = client['groups']  # Substitua pelo nome do seu banco de dados
    collection = db['groups']   # Substitua pelo nome da sua coleção

    data = request.get_json()
    name = data.get('group_name')
    user_login = data.get('login')
    description = data.get('group_description')
    pwd = data.get('pwd')
    n_participants = data.get('group_number_participants')
    
    unique_id = generate_identifier()
    print(unique_id)
    while collection.find_one({'unique_id': unique_id}) != None:
        unique_id = generate_identifier()
        print(unique_id)
    
    print("Recebi uma requisição")

    # Verifica se o grupo com o mesmo nome já existe
    if collection.find_one({'name': name}):
        print("Erro: Grupo já existe!")
        return jsonify({"message": "Grupo com esse nome já existe!"}), 400
    
    group_participants = []

    for i in range(int(n_participants)):
        group_participants.append('User ' + str(i + 1))

    group_participants[0] = user_login

    # Cria o novo grupo
    new_group = {
        'id': unique_id,
        'name': name,
        'description': description,
        'pwd': pwd,
        'n_participants': n_participants,
        'participants' : group_participants
    }

    # Chama a função que associa o grupo ao usuário
    if not(add_group_to_user(user_login, unique_id)):
        return jsonify({"message": "Erro ao associar grupo ao usuário."}), 400
    
    # Insere o novo grupo no banco de dados
    collection.insert_one(new_group)
    print("Grupo Criado")

    return jsonify({"message": "Grupo registrado com sucesso!", "id_group": unique_id}), 200
        
@app.route('/login/group', methods=['GET'])
def login_group():
    db = client['groups']  # Substitua pelo nome do seu banco de dados
    collection = db['groups']

    db_users = client['Users']  # Substitua pelo nome do seu banco de dados
    collection_users = db_users['Users']  # Substitua pelo nome da sua coleção

    # Recebe o login, senha do grupo e login do usuário
    name = request.args.get('login')
    password = request.args.get('pwd')
    login_user = request.args.get('loginUser')

    print(name)
    print(password)
    print(login_user)
    
    # Verifica se o grupo existe pela ID
    group = collection.find_one({'id': name})
    
    print("Antes group: ", group)

    if group:
        # Se o grupo existir, verifica a senha
        if group['pwd'] == password:
                print("PAssei aqui")
                # Procura por um usuário disponível para substituir
                for i, user in enumerate(group['participants']):
                    user_db = collection_users.find_one({'login': user})
                    print(user_db)
                    if user_db is None:
                        
                        break

                    if login_user in group['participants']:
                        return jsonify({"message": "Usuário já associado ao grupo"}), 400

                group['participants'][i] = login_user  # Substitui o primeiro usuário disponível pelo login_user
                    
            
                # Atualiza o grupo com o novo usuário na lista de participantes
                collection.update_one(
                    {'id': group['id']},  # Atualiza o grupo com base no ID
                    {'$set': {'participants': group['participants']}}  # Atualiza a lista de participantes
                )
                
                # Adiciona o grupo ao usuário
                if not add_group_to_user(login_user, group['id']):
                    print("Erro ao associar grupo ao usuário.")
                    return jsonify({"message": "Erro ao associar grupo ao usuário."}), 400

                return jsonify({"group_name": group['name'], 'group_description': group['description'], 'group_number_participants': group['n_participants'], 'login' : group['id']}), 200
        else:
            print("Senha inválida!")
            return jsonify({"message": "Senha inválida!", "flag": False}), 400
        
    else:
        # Verifica o grupo pelo nome caso a busca por ID não tenha funcionado
        group = collection.find_one({'login': name})
        
        if group:
            if group['pwd'] == password:
                
                # Procura por um usuário disponível para substituir
                for i, user in enumerate(group['participants']):
                    user_db = collection_users.find_one({'nome': user})


                    if user_db is None:
                        break

                    if user_db['nome'] in group['participants']:
                        return jsonify({"message": "Usuário já associado ao grupo"}), 400

                group['participants'][i] = login_user  # Substitui o primeiro usuário disponível pelo login_user
                    
            
                # Atualiza o grupo com o novo usuário na lista de participantes
                collection.update_one(
                    {'id': group['id']},  # Atualiza o grupo com base no ID
                    {'$set': {'participants': group['participants']}}  # Atualiza a lista de participantes
                )
                
                # Adiciona o grupo ao usuário
                if not add_group_to_user(login_user, group['id']):
                    return jsonify({"message": "Erro ao associar grupo ao usuário."}), 400

                return jsonify({"message": "Login bem-sucedido!", "flag": True}), 200

        else:
            return jsonify({"message": "Login ou senha inválidos!", "flag": False}), 401

        
@app.route('/groups/all', methods=['GET'])
def get_all_groups():
    db = client['groups']  # Substitua pelo nome do seu banco de dados
    collection = db['groups']  # Substitua pelo nome da sua coleção
    
    # Recupera todos os grupos da coleção
    groups = collection.find()  # find() retorna um cursor com todos os documentos

    # Converte os resultados para uma lista e filtra os campos que deseja mostrar (por exemplo, sem o campo '_id')
    groups_list = []
    for group in groups:
        group_data = {
            'id': group['id'],
            'name': group['name'],
            'description': group['description'],
            'n_participants': group['n_participants']
        }
        groups_list.append(group_data)

    return jsonify({"groups": groups_list}), 200

@app.route('/groups', methods=['GET'])
def get_groups_from_user():
    db = client['groups']  # Substitua pelo nome do seu banco de dados
    collection = db['groups']  # Substitua pelo nome da sua coleção

    login_user = request.args.get('loginUser')
    print(login_user)
    db_users = client['Users']  # Substitua pelo nome do seu banco de dados
    collection_users = db_users['Users']  # Substitua pelo nome da sua coleção

    user_db = collection_users.find_one({'login': login_user})
    print(user_db)

    if user_db is None:
        return jsonify({"message": "Usuário não possui grupos Cadastrados"}), 404

    groups_list = []

    for group_user in user_db['groups']:
        print(group_user)
        # Recupera todos os grupos da coleção
        groups = collection.find_one({'id': group_user})  # find() retorna um cursor com todos os documentos

        # Converte os resultados para uma lista e filtra os campos que deseja mostrar (por exemplo, sem o campo '_id')
        group_data = {
            'id': groups['id'],
            'name': groups['name'],
            'description': groups['description'],
            'n_participants': groups['n_participants'],
            'participants': groups['participants']
        }
        groups_list.append(group_data)

    return jsonify({"groups": groups_list}), 200

@app.route('/spent/register', methods=['POST'])
def register_spent():
    db = client['spents']  # Substitua pelo nome do seu banco de dados
    collection = db['spents']  # Substitua pelo nome da sua coleção

    # Recebe os dados enviados no corpo da requisição
    data = request.get_json()
    
    id_group = data.get('id_group')
    type_spent = data.get('type_spent')
    login_user = data.get('login_user')
    spent_description = data.get('spent_description')
    spent_value = data.get('spent_value')
    participants_spent = data.get('participants_spent')

    print("Registro de gasto recebido")
    print(data)

    
    # Cria o documento para inserir no MongoDB
    expense_data = {
        'id_group': id_group,
        'type_spent': type_spent,
        'spent_description': spent_description,
        'spent_value': spent_value,
        'paied_by': login_user,
        'participants_spent': participants_spent
    }

    # Insere o documento na coleção 'group_expenses'
    collection.insert_one(expense_data)

    # Retorna sucesso
    return jsonify({"message": "Gasto registrado com sucesso!"}), 200

@app.route('/extract', methods=['GET'])
def get_statement():
    db = client['spents']
    collection = db['spents']

    login = request.args.get('loginUser')
    id_group = request.args.get('id_group')

    if not login or not id_group:
        return jsonify({"message": "Parâmetros 'loginUser' e 'id_group' são obrigatórios."}), 400

    # Busca as transações do grupo no banco "spents"
    transactions = collection.find({'id_group': id_group})
    
    # Dicionários para acumular os valores:
    # owes_user: valores que os outros devem para o usuário (créditos)
    # user_owes: valores que o usuário deve para os outros (débitos)
    owes_user = {}
    user_owes = {}
    
    # Variável para acumular o total gasto pelo usuário (a soma das partes dele em todas as transações)
    total_spent = 0.0

    for tx in transactions:
        payer = tx['paied_by']
        spent_value = float(tx['spent_value'])
        ps = tx['participants_spent']
        
        # Monta o dicionário "split" a partir do array de participantes,
        # onde cada objeto contém: name, percentage, value
        split = {}
        if isinstance(ps, list) and len(ps) > 0:
            for participant_obj in ps:
                participant_name = participant_obj['name']
                participant_value = participant_obj['value']
                # Se 'value' for None, utiliza 0
                if participant_value is None:
                    participant_value = 0
                else:
                    participant_value = float(participant_value)
                split[participant_name] = participant_value
        elif isinstance(ps, dict):
            split = ps  # Caso já venha no formato dict
        
        # Acumula o valor da parte do usuário para o total gasto
        if login in split:
            total_spent += split[login]

        # Se o usuário for o pagador, os demais participantes devem pagar para ele
        if login == payer:
            for participant, amount in split.items():
                if participant == login:
                    continue
                owes_user[participant] = owes_user.get(participant, 0) + amount
        else:
            # Se o usuário participou e não é o pagador, ele deve pagar ao pagador
            if login in split:
                amount = split[login]
                user_owes[payer] = user_owes.get(payer, 0) + amount

    # Calcula o saldo líquido para cada participante:
    # Saldo positivo: o outro usuário deve para você
    # Saldo negativo: você deve para o outro usuário
    net_balances = {}
    all_participants = set(owes_user.keys()) | set(user_owes.keys())
    for participant in all_participants:
        net = owes_user.get(participant, 0) - user_owes.get(participant, 0)
        net_balances[participant] = net

    # Formata os saldos em uma lista de dicionários
    participants_list = []
    for participant, amount in net_balances.items():
        rounded_amount = round(amount, 2)
        if rounded_amount > 0:
            balance_str = f"+{rounded_amount}"
        elif rounded_amount < 0:
            balance_str = f"{rounded_amount}"  # Já contém o sinal negativo
        else:
            balance_str = "0"
        participants_list.append({
            "participant_name": participant,
            "participant_balance": balance_str
        })

    extrato = {
        "user_login": login,
        "id_group": id_group,
        "total_spent": round(total_spent, 2),
        "participants": participants_list
    }

    print(extrato)
    return jsonify(extrato), 200


@app.route('/group/info', methods=['GET'])
def get_info_group_from_user():
    db = client['groups']  # Substitua pelo nome do seu banco de dados
    collection = db['groups']  # Substitua pelo nome da sua coleção

    login_user = request.args.get('loginUser')
    id_group = request.args.get('id_group')

    print(login_user)
    db_users = client['Users']  # Substitua pelo nome do seu banco de dados
    collection_users = db_users['Users']  # Substitua pelo nome da sua coleção

    user_db = collection_users.find_one({'login': login_user})
    print(user_db)

    if user_db is None:
        return jsonify({"message": "Usuário não possui grupos Cadastrados"}), 404

    groups_list = []
    if id_group in user_db['groups']:
        groups = collection.find_one({'id': id_group})  # find() retorna um cursor com todos os documentos

        # Converte os resultados para uma lista e filtra os campos que deseja mostrar (por exemplo, sem o campo '_id')
        group_data = {
            'id': groups['id'],
            'name': groups['name'],
            'description': groups['description'],
            'n_participants': groups['n_participants'],
            'participants': groups['participants']
        }
        groups_list.append(group_data)

    return jsonify({"groups": groups_list}), 200


if __name__ == '__main__':
    app.run(debug=True)