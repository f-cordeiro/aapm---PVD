import pytest
from app.models.produto import Produto


# ==============================================================================
# BLOCO 1: TESTE DE CRIAÇÃO DO PRODUTO (DADOS BÁSICOS)
# ==============================================================================
def test_1_criar_produto_com_sucesso(db_session_test):
    

# Verificar se o Produto salva corretamente o nome, preço e estoque na memória e no banco.
    
    # 1. PREPARAR (Dados do produto e gravação no banco)
    produto = Produto(
        nome="Teclado Mecânico",
        preco=250.00,
        estoque_atual=15,
        ativo=True
    )
    db_session_test.add(produto)
    db_session_test.commit()

    # 2. EXECUTAR (Buscar no banco de dados o produto que foi criado utilizando filtro)
    produto_encontrado = db_session_test.query(Produto).filter(Produto.nome == "Teclado Mecânico").first()

    # 3. CONFERIR (Validar os dados retornados do filtro)
    assert produto_encontrado is not None
    assert produto_encontrado.nome == "Teclado Mecânico"
    assert produto_encontrado.preco == 250.00
    assert produto_encontrado.estoque_atual == 15
    assert produto_encontrado.ativo is True