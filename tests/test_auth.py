from app.auth import hash_senha, verificar_senha

# Rodar o teste: python -m pytest 
# pip install httpx2
# pip install pytest

#Testar as funções do arquivo auth.py
def test_hash_senha_gera_string_diferente_original():

    senha = "minhasenha"

    hash_gerado = hash_senha(senha)

    # Testar a função
    assert senha != hash_gerado

# Testar a função verificar senha
def test_verificar_senha_aceita_senha_correta():
    senha = "test@123"
    hash_gerado = hash_senha(senha)

    resultado = verificar_senha(senha, hash_gerado)

    #testar a função
    # assert resultado == True
    assert resultado is True

# Testar a fução verificar senha
def test_verificar_senha_rejeita_senha_incorreta():
    senha_correta = "Gustavo10%fsilva"
    senha_incorreta = "outrasenha"
    hash_gerado = hash_senha(senha_correta)

    resultado = verificar_senha(senha_incorreta, hash_gerado)

    assert resultado is False