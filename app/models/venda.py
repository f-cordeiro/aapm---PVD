
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


# ============================================================
# VENDA
# ============================================================

class Venda(Base):
    __tablename__ = "vendas"

    id = Column(Integer, primary_key=True, index=True)

    # Cliente pode ser NULL em vendas de balcão.
    cliente_id = Column(
        Integer,
        ForeignKey("clientes.id", ondelete="SET NULL"),
        nullable=True
    )

    # Usuário responsável pelo registro da venda.
    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True
    )

    # Percentual total de desconto aplicado.
    desconto_percentual = Column(
        Float,
        nullable=False,
        default=0.0
    )

    # Valores da venda.
    total_bruto = Column(
        Float,
        nullable=False,
        default=0.0
    )

    total_liquido = Column(
        Float,
        nullable=False,
        default=0.0
    )

    # Primeira forma de pagamento.
    forma_pagamento_1 = Column(
        String(30),
        nullable=True
    )

    valor_pagamento_1 = Column(
        Float,
        nullable=False,
        default=0.0
    )

    # Segunda forma de pagamento, opcional.
    forma_pagamento_2 = Column(
        String(30),
        nullable=True
    )

    valor_pagamento_2 = Column(
        Float,
        nullable=False,
        default=0.0
    )

    # Observação opcional.
    observacao = Column(
        String(255),
        nullable=True
    )

    # Data e hora de criação.
    criado_em = Column(
        DateTime,
        server_default=func.now()
    )

    # Relacionamentos.
    cliente = relationship(
        "Cliente",
        back_populates="vendas"
    )

    usuario = relationship(
        "Usuario",
        backref="vendas"
    )

    itens = relationship(
        "ItemVenda",
        back_populates="venda",
        cascade="all, delete-orphan"
    )

    @property
    def desconto_valor(self) -> float:
        """Retorna o valor monetário do desconto."""
        return self.total_bruto - self.total_liquido

    def __repr__(self):
        return (
            f"<Venda id={self.id} "
            f"total={self.total_liquido}>"
        )


# ============================================================
# ITENS DA VENDA
# ============================================================

class ItemVenda(Base):
    __tablename__ = "itens_venda"

    id = Column(Integer, primary_key=True, index=True)

    venda_id = Column(
        Integer,
        ForeignKey("vendas.id", ondelete="CASCADE"),
        nullable=False
    )

    produto_id = Column(
        Integer,
        ForeignKey("produtos.id", ondelete="SET NULL"),
        nullable=True
    )

    # Dados históricos do produto no momento da venda.
    produto_nome = Column(
        String(150),
        nullable=False
    )

    quantidade = Column(
        Integer,
        nullable=False
    )

    preco_unitario = Column(
        Float,
        nullable=False
    )

    @property
    def subtotal(self) -> float:
        """Calcula o subtotal do item."""
        return self.quantidade * self.preco_unitario

    # Relacionamentos.
    venda = relationship(
        "Venda",
        back_populates="itens"
    )

    produto = relationship(
        "Produto",
        backref="itens_venda"
    )
