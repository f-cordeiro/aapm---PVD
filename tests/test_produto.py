import pytest
from app.models.produto import Produto


# ==============================================================================
# BLOCO 1: CRIAR E FILTRAR PRODUTO NO BANCO DE DADOS


def test_criar_buscar_produto_com_sucesso(db_session_test):
    #"""OBJETIVO: Salvar produto no banco e buscar fazendo filtro pelo nome."""
    # 1. PREPARAR
    produto = Produto(nome="Teclado Mecânico", preco=250.00, estoque_atual=15, ativo=True)
    db_session_test.add(produto)
    db_session_test.commit()

    # 2. EXECUTAR
    encontrado = db_session_test.query(Produto).filter(Produto.nome == "Teclado Mecânico").first()

    # 3. CONFERIR
    assert encontrado is not None
    assert encontrado.nome == "Teclado Mecânico"
    assert encontrado.preco == 250.00


# ==============================================================================
# BLOCO 2: VALIDAR CAMINHO DA IMAGEM DO PRODUTO (PROPRIEDADE)


def test_validar_url_da_imagem_do_produto():
   # """OBJETIVO: Garantir que o produto monte o caminho completo da foto no servidor."""
    # 1. PREPARAR
    produto = Produto(imagem_path="uploads/foto.png")

    # 2. EXECUTAR & 3. CONFERIR
    assert produto.imagem_url == "/static/uploads/foto.png"


# ==============================================================================
# BLOCO 3: IMAGEM PADRÃO QUANDO NÃO HOUVER FOTO CADASTRADA


def test_imagem_placeholder_quando_sem_foto():
   # """OBJETIVO: Exibir a imagem padrão (placeholder) caso o produto esteja sem foto."""
    # 1. PREPARAR
    produto = Produto(imagem_path=None)

    # 2. EXECUTAR & 3. CONFERIR
    assert produto.imagem_url == "/static/img/produto-placeholder.png"


# ==============================================================================
# BLOCO 4: IDENTIFICAR ESTOQUE BAIXO (ALERTA)


def test_alerta_de_estoque_baixo():
   # """OBJETIVO: Sinalizar verdadeiro para estoque baixo quando a quantidade for <= 10."""
    # 1. PREPARAR
    produto = Produto(estoque_atual=5)

    # 2. EXECUTAR & 3. CONFERIR
    assert produto.estoque_baixo is True


# ==============================================================================
# BLOCO 5: FILTRAR PRODUTOS ATIVOS E COM ESTOQUE POSITIVO


def test_filtrar_produtos_disponiveis_no_banco(db_session_test):
  #  """OBJETIVO: Retornar no banco apenas produtos ativos e com saldo em estoque."""
    # 1. PREPARAR
    p1 = Produto(nome="Mouse", preco=50.0, estoque_atual=10, ativo=True)
    p2 = Produto(nome="Teclado", preco=100.0, estoque_atual=0, ativo=True)  # Sem estoque
    db_session_test.add_all([p1, p2])
    db_session_test.commit()

    # 2. EXECUTAR
    disponiveis = db_session_test.query(Produto).filter(
        Produto.ativo.is_(True),
        Produto.estoque_atual > 0
    ).all()

    # 3. CONFERIR
    assert len(disponiveis) == 1
    assert disponiveis[0].nome == "Mouse"