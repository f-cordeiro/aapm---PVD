import json
import pytest
from app.models.produto import Produto
from app.models.cliente import Cliente
from app.models.venda import Venda, ItemVenda


# ==============================================================================
# BLOCO 1: CARREGAR A TELA DO CAIXA PDV (GET /pdv/)


def test_carregar_frente_de_caixa_pdv(cliente):
    """OBJETIVO: Verificar se a interface de vendas do caixa abre com sucesso (200)."""
    # 1. PREPARAR & 2. EXECUTAR
    resposta = cliente.get("/pdv/")

    # 3. CONFERIR
    assert resposta.status_code == 200


# ==============================================================================
# BLOCO 2: FINALIZAR VENDA E BAIXAR ESTOQUE (POST /pdv/finalizar)


def test_finalizar_venda_com_sucesso(cliente, db_session_test):
    """OBJETIVO: Processar a venda, registrar os itens e dar baixa automática no estoque."""
    # 1. PREPARAR
    produto = Produto(nome="Caderno", preco=20.0, estoque_atual=10, ativo=True)
    db_session_test.add(produto)
    db_session_test.commit()

    carrinho = [{"produto_id": produto.id, "nome": produto.nome, "preco": produto.preco, "quantidade": 2}]
    dados = {"carrinho_json": json.dumps(carrinho), "cliente_id": 0}

    # 2. EXECUTAR
    resposta = cliente.post("/pdv/finalizar", data=dados, follow_redirects=False)

    # 3. CONFERIR
    assert resposta.status_code == 302
    db_session_test.refresh(produto)
    assert produto.estoque_atual == 8
    assert db_session_test.query(Venda).first() is not None

# ==============================================================================
# BLOCO 3: BARRAR VENDA SEM ESTOQUE DISPONÍVEL (POST /pdv/finalizar)


def test_bloquear_venda_estoque_insuficiente(cliente, db_session_test):
    """OBJETIVO: Rejeitar a venda se a quantidade solicitada for maior que o estoque."""
    # 1. PREPARAR
    produto = Produto(nome="Caneta", preco=5.0, estoque_atual=1, ativo=True)
    db_session_test.add(produto)
    db_session_test.commit()

    carrinho = [{"produto_id": produto.id, "nome": produto.nome, "preco": produto.preco, "quantidade": 5}]
    dados = {"carrinho_json": json.dumps(carrinho), "cliente_id": 0}

    # 2. EXECUTAR
    resposta = cliente.post("/pdv/finalizar", data=dados, follow_redirects=False)

    # 3. CONFERIR
    assert resposta.status_code == 302
    assert "/pdv?erro=estoque" in resposta.headers["location"]


# ==============================================================================
# BLOCO 4: CONSULTAR COMPROVANTE DE VENDA (GET /pdv/venda/{id})


def test_exibir_comprovante_venda_retorna_200(cliente, db_session_test):
    """OBJETIVO: Abrir o comprovante com o detalhamento do cupom emitido."""
    # 1. PREPARAR
    venda = Venda(total_bruto=50.0, total_liquido=50.0)
    db_session_test.add(venda)
    db_session_test.commit()

    # 2. EXECUTAR
    resposta = cliente.get(f"/pdv/venda/{venda.id}")

    # 3. CONFERIR
    assert resposta.status_code == 200