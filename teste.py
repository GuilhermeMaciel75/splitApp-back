import requests

BASE_URL = 'http://127.0.0.1:5000'  # URL da sua API Flask local

# Função para testar o registro de um novo usuário
def test_register():
    url = f"{BASE_URL}/register"
    data = {
        'login': 'user5',
        'password': 'password123'
    }

    # Envia a requisição POST para registrar o usuário
    response = requests.post(url, json=data)
    
    # Verifica se o registro foi bem-sucedido
    if response.status_code == 201:
        print("Registro bem-sucedido!")
        print(response.json())
    else:
        print(f"Erro ao registrar usuário: {response.json()}")

# Função para testar o login de um usuário
def test_login():
    url = f"{BASE_URL}/login"
    params = {
        'login': 'gg@gmail.com',
        'pwd': '123'
    }

    # Envia a requisição GET para fazer login
    response = requests.get(url, params=params)
    
    # Verifica se o login foi bem-sucedido
    if response.status_code == 200:
        print("Login bem-sucedido!")
        print(response.json())
    else:
        print(f"Erro no login: {response.json()}")

# Função para testar o login com senha incorreta
def test_login_invalid_password():
    url = f"{BASE_URL}/login"
    params = {
        'login': 'user5',
        'password': 'wrongpassword'
    }

    # Envia a requisição GET para fazer login
    response = requests.get(url, params=params)
    
    # Verifica se o login falhou com a senha incorreta
    if response.status_code == 401:
        print("Login com senha incorreta falhou, como esperado.")
        print(response.json())
    else:
        print(f"Erro inesperado no login: {response.json()}")

# Função para testar o login com um usuário não registrado
def test_login_user_not_found():
    url = f"{BASE_URL}/login"
    params = {
        'login': 'nonexistentuser',
        'password': 'password123'
    }

    # Envia a requisição GET para fazer login
    response = requests.get(url, params=params)
    
    # Verifica se o login falhou devido ao usuário não encontrado
    if response.status_code == 401:
        print("Login com usuário não encontrado falhou, como esperado.")
        print(response.json())
    else:
        print(f"Erro inesperado no login: {response.json()}")

# Função para testar o registro de um grupo
def test_register_group():
    data = {
        'group_name': 'Grupo Teste',
        'group_description': 'Este é um grupo de teste',
        'pwd': 'senha123',
        'group_number_participants': 10
        }

    url = f"{BASE_URL}/register/group"


    try:
        # Enviando a requisição POST para a API
        response = requests.post(url, json=data, verify=False)  # `verify=False` é usado para ignorar erros de SSL em localhost

        # Verificando o status code da resposta
        if response.status_code == 200:
            print("Grupo criado com sucesso!")
            print("Resposta:", response.json())
        else:
            print(f"Erro ao criar grupo: {response.status_code}")
            print("Mensagem de erro:", response.json())
    except Exception as e:
        print(f"Erro ao fazer a requisição: {str(e)}")

# Função para testar o login do grupo
def test_login_group():
    data = {
        'login': 'a',  # Substitua com o id do grupo que você quer testar
        'pwd': 'a'
    }

    url = f"{BASE_URL}/login/group"

    try:
        # Enviando a requisição GET para a API
        response = requests.get(url, params=data, verify=False)  # `verify=False` é usado para ignorar erros de SSL em localhost

        # Verificando o status code da resposta
        if response.status_code == 200:
            print("Login bem-sucedido!")
            print("Resposta:", response.json())
        else:
            print(f"Erro ao fazer login: {response.status_code}")
            print("Mensagem de erro:", response.json())
    except Exception as e:
        print(f"Erro ao fazer a requisição: {str(e)}")

# Executa os testes
if __name__ == '__main__':
    #print("Testando registro...")
    #test_register()
    
    #print("\nTestando login...")
    #test_login()
    
    #print("\nTestando login com senha incorreta...")
    #test_login_invalid_password()
    
    #print("\nTestando login com usuário não registrado...")
    #test_login_user_not_found()

    #print("\nTestando a criacao de um novo grupo")
    #test_register_group()

    print("\nTestando login de um grupo")
    test_login_group()
