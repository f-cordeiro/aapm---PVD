# Sistema de PDV e Gestão de Estoque

Sistema web desenvolvido em Python com FastAPI para gestão de estoque, clientes, categorias, produtos, movimentações e ponto de venda (PDV). O projeto foi pensado para uso em lojas, mercados, pequenos negócios e operações de varejo, com autenticação por JWT, templates HTML renderizados no servidor e banco de dados SQLite por padrão.

## Visão geral

Este projeto permite:

- Gerenciar usuários com autenticação e perfis
- Cadastrar, editar e desativar produtos
- Controlar categorias de produtos
- Registrar clientes
- Registrar movimentações de entrada e saída de estoque
- Realizar vendas no PDV com cálculo de descontos e formas de pagamento
- Consultar histórico de vendas e comprovantes
- Visualizar e controlar estoque em tempo real

## Stack tecnológica

- Python 3.11+
- FastAPI
- SQLAlchemy
- Alembic
- Jinja2
- SQLite
- JWT (Python-JOSE)
- Bcrypt / Passlib
- HTML, CSS e JavaScript

## Estrutura do projeto

```text
.
├── app/
│   ├── controllers/
│   ├── models/
│   ├── static/
│   ├── templates/
│   ├── auth.py
│   ├── database.py
│   └── main.py
├── migrations/
├── tests/
├── .env
├── alembic.ini
├── criar_usuarios.py
├── requirements.txt
├── README.md
└── estoque.db (gerado após execução)
```

## Requisitos

Antes de iniciar, garanta que você tenha instalado em sua máquina:

- Python 3.11 ou superior
- pip
- Git
- Ambiente virtual (recomendado)

## Clonando o projeto

```bash
git clone <URL_DO_REPOSITORIO>
cd aapm---PVD
```

## Configurando o ambiente virtual

No Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

No Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Instalando dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Configuração de variáveis de ambiente

O projeto já inclui um arquivo `.env` com as configurações iniciais. Verifique o conteúdo:

```env
DATABASE_URL=sqlite:///estoque.db
SECRET_KEY=901e6de8c4d51d46e09ee880a72e20cf
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTE=60
```

Se necessário, você pode alterar:

- `DATABASE_URL`: URL do banco de dados
- `SECRET_KEY`: chave secreta para assinatura do JWT
- `ALGORITHM`: algoritmo de criptografia do token
- `ACCESS_TOKEN_EXPIRE_MINUTE`: tempo de expiração do token em minutos

Importante: em produção, troque a `SECRET_KEY` por uma string forte e segura.

## Banco de dados

Este projeto usa SQLite por padrão, o que facilita execução local e testes.

Para verificar ou inicializar o banco, o sistema já está preparado para gerar as tabelas automaticamente a partir dos modelos SQLAlchemy. Se quiser usar migrações Alembic, execute:

```bash
alembic upgrade head
```

Se o banco ainda não existir, o sistema pode criá-lo ao rodar a app, dependendo da configuração e da estrutura do projeto.

## Criando usuário administrativo

O projeto possui um script de seed para criar um usuário administrador inicial:

```bash
python criar_usuarios.py
```

Esse script cria um usuário padrão com:

- Nome: `admin`
- E-mail: `admin@teste.com`
- Senha: `admin@123`

Você pode alterar essas credenciais diretamente no arquivo `criar_usuarios.py`.

## Executando a aplicação

Inicie o servidor com:

```bash
uvicorn app.main:app --reload
```

A aplicação ficará disponível em:

```text
http://127.0.0.1:8000
```

Para encerrar o servidor, pressione:

```text
Ctrl + C
```

## Acesso ao sistema

Ao abrir a aplicação, o sistema redireciona para a tela de login. Use o usuário administrativo criado anteriormente:

- E-mail: `admin@teste.com`
- Senha: `admin@123`

Após login, o sistema encaminha para a área do PDV.

## Funcionalidades principais

### 1. Autenticação

- Login com e-mail e senha
- Proteção de rotas via cookies e JWT
- Usuários ativos e inativos
- Controle de acesso por perfil (`admin` e `operador`)

### 2. Usuários

- Cadastro de usuários
- Edição de dados
- Ativação/desativação
- Controle de permissões

### 3. Categorias

- Cadastro de categorias
- Edição e exclusão lógica
- Organização dos produtos

### 4. Produtos

- Cadastro com nome, preço, estoque e categoria
- Upload de imagem
- Controle de estoque atual
- Desativação de produtos sem apagar do banco

### 5. Clientes

- Cadastro de clientes
- Histórico de compras associadas
- Ativação e inativação

### 6. Movimentações de estoque

- Entrada de produtos
- Saída de produtos
- Registro de movimentações por motivo e quantidade
- Controle do saldo de estoque

### 7. PDV

- Adição de produtos ao carrinho
- Cálculo de desconto
- Seleção de cliente
- Formas de pagamento
- Validação de estoque antes da venda
- Atualização automática do estoque
- Geração de comprovante e histórico

## Rotas principais

A aplicação possui rotas organizadas por módulo:

- `/auth/login` — tela de login
- `/auth/cadastro` — cadastro de usuário
- `/usuarios/` — listagem de usuários
- `/categorias/` — categorias
- `/produtos/` — produtos
- `/clientes/` — clientes
- `/movimentacoes/` — movimentações
- `/pdv/` — ponto de venda
- `/pdv/historico` — histórico de vendas

## Fluxo de uso recomendado

### Primeiros passos

1. Instale as dependências
2. Verifique o arquivo `.env`
3. Crie o usuário administrador com `python criar_usuarios.py`
4. Execute a aplicação com `uvicorn`
5. Faça login no sistema
6. Cadastre categorias e produtos
7. Registre clientes
8. Inicie o fluxo de vendas no PDV

### Exemplo de atividade real

- Criar categoria: `Alimentos`
- Cadastrar produto: `Arroz 5kg`, preço `R$ 18,90`, estoque `40`
- Cadastrar cliente: `Maria da Silva`
- Fazer uma venda no PDV
- Conferir o histórico de vendas
- Validar a atualização do estoque

## Testes

O projeto contém testes automatizados na pasta `tests/`. Para executar:

```bash
pytest
```

Se quiser ver uma saída mais detalhada:

```bash
pytest -q
```

## Migrações com Alembic

Este projeto já inclui migrações em `migrations/versions`.

Para aplicar as migrações:

```bash
alembic upgrade head
```

Para gerar uma nova migração após alterar um modelo:

```bash
alembic revision --autogenerate -m "descricao_da_mudanca"
```

## Dicas de desenvolvimento

- Mantenha a chave secreta sempre protegida
- Use um banco de dados mais robusto em produção, como PostgreSQL
- Sempre teste alterações antes de publicar em produção
- Atualize o arquivo `.env` nas instâncias de produção
- Em ambientes Windows, use o PowerShell para ativar o ambiente virtual

## Troubleshooting

### Erro de importação do módulo

Se aparecer erro como `ModuleNotFoundError` ou similar:

```bash
pip install -r requirements.txt
```

E confirme que o ambiente virtual está ativo.

### Erro ao iniciar o servidor

Verifique se:

- o Python está correto
- o ambiente virtual está ativado
- as dependências estão instaladas
- a variável `DATABASE_URL` está correta

### JWT inválido ou não autenticado

Isso geralmente acontece quando:

- o cookie `access_token` não foi gerado corretamente
- o token expirou
- a `SECRET_KEY` foi alterada

### Banco de dados não encontrado

Confirme se o arquivo `estoque.db` foi gerado ou se a conexão em `.env` aponta para um banco válido.

## Contribuição

Se você quiser colaborar com o projeto:

1. Faça um fork
2. Crie uma branch para a funcionalidade
3. Faça suas alterações
4. Teste o projeto
5. Abra um pull request com uma descrição clara

## Licença

Este projeto foi desenvolvido para fins acadêmicos e de uso interno. Verifique com o responsável do repositório antes de usar em produção sem autorização.

## Resumo rápido

Comandos essenciais:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python criar_usuarios.py
uvicorn app.main:app --reload
```

Acesso:

```text
http://127.0.0.1:8000
```

Login padrão:

```text
admin@teste.com
admin@123
```

Se você quiser, posso também criar uma versão mais visual deste README com badges, ícones e uma seção de screenshots do fluxo do sistema.