import pytest
from app.models.produto import Produto
from app.models.movimentacao import Movimentacao, TipoMovimentacao


# ==============================================================================
# BLOCO 1: CARREGAR HISTÓRICO GERAL (GET /movimentacoes/)


def test_1_listar_movimentacoes_retorna_200(cliente):

    #OBJETIVO: Carregar o relatório geral de movimentações de estoque (status 200).
    # 1. PREPARAR & 2. EXECUTAR
    resposta = cliente.get("/movimentacoes/")

    # 3. CONFERIR
    assert resposta.status_code == 200


# ==============================================================================
# BLOCO 2: REGISTRAR ENTRADA E SUMAR ESTOQUE (POST /movimentacoes/nova)


def test_2_registrar_entrada_estoque(cliente, db_session_test):
    #"""OBJETIVO: Dar entrada de itens e validar o aumento automático do saldo do produto."""
    # 1. PREPARAR
    produto = Produto(nome="Mouse Gamer", preco=100.0, estoque_atual=10, ativo=True)
    db_session_test.add(produto)
    db_session_test.commit()

    dados = {
        "produto_id": produto.id,
        "tipo": "entrada",
        "quantidade": 5,
        "preco_unitario": 80.0,
        "observacao": "Reposição"
    }

    # 2. EXECUTAR
    resposta = cliente.post("/movimentacoes/nova", data=dados, follow_redirects=False)

    # 3. CONFERIR
    assert resposta.status_code == 302
    db_session_test.refresh(produto)
    assert produto.estoque_atual == 15


# =================================================================
# BLOCO 3: REGISTRAR SAÍDA E SUBTRAIR ESTOQUE (POST /movimentacoes/nova)

def test_3_registrar_saida_estoque(cliente, db_session_test):
    #"""OBJETIVO: Registrar saída e confirmar a diminuição da quantidade em estoque."""
    # 1. PREPARAR
    produto = Produto(nome="Teclado", preco=150.0, estoque_atual=20, ativo=True)
    db_session_test.add(produto)
    db_session_test.commit()

    dados = {
        "produto_id": produto.id,
        "tipo": "saida",
        "quantidade": 3,
        "preco_unitario": 150.0,
        "observacao": "Venda"
    }

    # 2. EXECUTAR
    resposta = cliente.post("/movimentacoes/nova", data=dados, follow_redirects=False)

    # 3. CONFERIR
    assert resposta.status_code == 302
    db_session_test.refresh(produto)
    assert produto.estoque_atual == 17


# ==============================================================================
# BLOCO 4: BLOQUEAR QUANTIDADE INVÁLIDA (POST /movimentacoes/nova)


def test_4_bloquear_quantidade_zerada_ou_negativa(cliente, db_session_test):
   # """OBJETIVO: Bloquear lançamentos com quantidade igual a zero ou menor (erro 400)."""
    # 1. PREPARAR
    produto = Produto(nome="Headset", preco=200.0, estoque_atual=10, ativo=True)
    db_session_test.add(produto)
    db_session_test.commit()

    dados = {"produto_id": produto.id, "tipo": "entrada", "quantidade": 0, "preco_unitario": 200.0}

    # 2. EXECUTAR
    resposta = cliente.post("/movimentacoes/nova", data=dados, follow_redirects=False)

    # 3. CONFERIR
    assert resposta.status_code == 400


# ==============================================================================
# BLOCO 5: IMPEDIR SAÍDA MAIOR QUE ESTOQUE (POST /movimentacoes/nova)


def test_5_bloquear_saida_acima_do_estoque(cliente, db_session_test):
   # """OBJETIVO: Barrar retiradas maiores que o saldo atual do produto (erro 400)."""
    # 1. PREPARAR
    produto = Produto(nome="Webcam", preco=300.0, estoque_atual=2, ativo=True)
    db_session_test.add(produto)
    db_session_test.commit()

    dados = {"produto_id": produto.id, "tipo": "saida", "quantidade": 10, "preco_unitario": 300.0}

    # 2. EXECUTAR
    resposta = cliente.post("/movimentacoes/nova", data=dados, follow_redirects=False)

    # 3. CONFERIR
    assert resposta.status_code == 400
    db_session_test.refresh(produto)
    assert produto.estoque_atual == 2