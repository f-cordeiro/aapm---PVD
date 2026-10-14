import pytest
from app.models.categoria import Categoria


# ==============================================================================
# BLOCO 1: CARREGAR LISTAGEM DE CATEGORIAS (GET /categorias/)

def test_listar_categorias_retorna_200(cliente):

   # OBJETIVO: Garantir que a página principal de categorias abra com sucesso (200).
    # 1. PREPARAR & 2. EXECUTAR
    resposta = cliente.get("/categorias/")

    # 3. CONFERIR
    assert resposta.status_code == 200


# ==============================================================================
# BLOCO 2: CADASTRAR NOVA CATEGORIA COM SUCESSO (POST /categorias/nova)


def test_criar_categoria_com_sucesso(cliente, db_session_test):
    # OBJETIVO: Criar uma categoria via formulário, redirecionar (302) e salvar no banco.
    # 1. PREPARAR
    dados = {"nome": "Periféricos"}

    # 2. EXECUTAR
    resposta = cliente.post("/categorias/nova", data=dados, follow_redirects=False)

    # 3. CONFERIR
    assert resposta.status_code == 302
    cat_banco = db_session_test.query(Categoria).filter(Categoria.nome == "Periféricos").first()
    assert cat_banco is not None
    assert cat_banco.nome == "Periféricos"


# ==============================================================================
# BLOCO 3: BLOQUEAR CATEGORIA COM NOME DUPLICADO (POST /categorias/nova)

def test_bloquear_categoria_duplicada_retorna_400(cliente, db_session_test):
   # OBJETIVO: Impedir o cadastro de categorias com nomes repetidos (erro 400).
    # 1. PREPARAR
    db_session_test.add(Categoria(nome="Hardware"))
    db_session_test.commit()

    # 2. EXECUTAR
    resposta = cliente.post("/categorias/nova", data={"nome": "Hardware"}, follow_redirects=False)

    # 3. CONFERIR
    assert resposta.status_code == 400


# ==============================================================================
# BLOCO 4: EDITAR NOME DA CATEGORIA (POST /categorias/{id}/editar)


def test_4_editar_categoria_com_sucesso(cliente, db_session_test):

    #OBJETIVO: Alterar o nome de uma categoria e verificar a gravação no banco.
    # 1. PREPARAR
    cat = Categoria(nome="Placa de Video")
    db_session_test.add(cat)
    db_session_test.commit()

    # 2. EXECUTAR
    resposta = cliente.post(f"/categorias/{cat.id}/editar", data={"nome": "Placas de Vídeo"}, follow_redirects=False)

    # 3. CONFERIR
    assert resposta.status_code == 302
    db_session_test.refresh(cat)
    assert cat.nome == "Placas de Vídeo"


# ==============================================================================
# BLOCO 5: ALTERAR STATUS ATIVO/INATIVO (POST /categorias/{id}/toggle-ativo)

def test_alternar_status_categoria(cliente, db_session_test):
    
   # OBJETIVO: Inverter a situação da categoria de Ativa para Inativa no banco.
    # 1. PREPARAR
    cat = Categoria(nome="Acessórios", ativo=True)
    db_session_test.add(cat)
    db_session_test.commit()

    # 2. EXECUTAR
    resposta = cliente.post(f"/categorias/{cat.id}/toggle-ativo", follow_redirects=False)

    # 3. CONFERIR
    assert resposta.status_code == 302
    db_session_test.refresh(cat)
    assert cat.ativo is False