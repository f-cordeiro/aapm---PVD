import pytest
from app.controllers.usuario_controller import Usuario
from app.auth import hash_senha, verificar_senha


# ==============================================================================
# BLOCO 1: SCRIPT DE CRIPTOGRAFIA DE SENHA (HASH)


def test_hash_senha_gera_codigo_diferente():
   # """OBJETIVO: Garantir que a senha digitada seja criptografada antes de salvar."""
    # 1. PREPARAR & 2. EXECUTAR
    senha_bruta = "minhasenha123"
    hash_gerado = hash_senha(senha_bruta)

    # 3. CONFERIR
    assert senha_bruta != hash_gerado


# ==============================================================================
# BLOCO 2: VALIDAR LOGIN COM SENHA CORRETA


def test_verificar_senha_correta_retorna_true():
   # """OBJETIVO: Confirmar que o sistema aceita a senha correta no login."""
    # 1. PREPARAR
    senha = "senha_segura"
    hash_gerado = hash_senha(senha)

    # 2. EXECUTAR & 3. CONFERIR
    assert verificar_senha(senha, hash_gerado) is True


# ==============================================================================
# BLOCO 3: BARRAR LOGIN COM SENHA INCORRETA


def test_verificar_senha_incorreta_retorna_false():
   # """OBJETIVO: Confirmar que o sistema recusa senhas incorretas no login."""
    # 1. PREPARAR
    hash_gerado = hash_senha("senha_correta")

    # 2. EXECUTAR & 3. CONFERIR
    assert verificar_senha("senha_errada", hash_gerado) is False


# ==============================================================================
# BLOCO 4: SALVAR E CONSULTAR USUÁRIO NO BANCO DE DADOS

def test_criar_e_buscar_usuario_por_email(db_session_test):
   # """OBJETIVO: Gravar um novo usuário e filtrá-lo pelo e-mail no banco."""
    # 1. PREPARAR
    usr = Usuario(nome="Carlos", email="carlos@email.com", senha_hash="123", ativo=True)
    db_session_test.add(usr)
    db_session_test.commit()

    # 2. EXECUTAR
    buscado = db_session_test.query(Usuario).filter(Usuario.email == "carlos@email.com").first()

    # 3. CONFERIR
    assert buscado is not None
    assert buscado.nome == "Carlos"


# ==============================================================================
# BLOCO 5: FILTRAR SOMENTE USUÁRIOS ATIVOS


def test_filtrar_apenas_usuarios_ativos(db_session_test):
    """OBJETIVO: Trazer na consulta apenas usuários com status ativo = True."""
    # 1. PREPARAR
    u1 = Usuario(nome="Ana", email="ana@email.com", senha_hash="123", ativo=True)
    u2 = Usuario(nome="Bruno", email="bruno@email.com", senha_hash="123", ativo=False)
    db_session_test.add_all([u1, u2])
    db_session_test.commit()

    # 2. EXECUTAR
    ativos = db_session_test.query(Usuario).filter(Usuario.ativo.is_(True)).all()

    # 3. CONFERIR
    assert len(ativos) == 1
    assert ativos[0].nome == "Ana"