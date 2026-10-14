from app.models.cliente import Cliente

def test_listar_clientes_retorna_200(cliente):

    resposta = cliente.get('/clientes/')

    assert resposta.status_code == 200

# Teste a tela de produtos sem o login 
def test_listagem_clientes_sem_login():
    from fastapi.testclient import TestClient
    from app.main import app

    cliente_sem_login = TestClient(app)

    resposta = cliente_sem_login.get("/clientes/")
    resposta2 = cliente_sem_login.get("/clientes/novo")

    assert resposta.status_code == 401
    assert resposta2.status_code ==401


