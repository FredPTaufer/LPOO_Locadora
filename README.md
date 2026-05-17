# Locadora de Veículos — LPOO

Sistema de gerenciamento de locação de veículos desenvolvido em Python com interface gráfica Tkinter e persistência em banco de dados PostgreSQL, seguindo o padrão de arquitetura MVC.

---

## Funcionalidades Implementadas

- **CRUD de Veículos** — Cadastro, Edição, Listagem e Remoção de Carros e Motorhomes com validação de placa
- **CRUD de Locações (Admin)** — acesso irrestrito para criar, editar, visualizar e remover qualquer locação
- **Operações de Locação (Usuário)** — fluxo operacional com as ações: Nova Reserva, Locar, Devolver e Cancelar, com regras de negócio e botões habilitados conforme o status
- **Ciclo de vida da locação** — controle de status: `reservado → locado → devolvido` ou `reservado → cancelado`
- **Filtro de disponibilidade** — ao criar uma reserva, exibe apenas veículos sem conflito de período e categoria
- **Calendário visual** — seleção de datas com popup de calendário nos formulários de locação
- **Padrões de projeto** — Factory, State, Strategy e Decorator aplicados no modelo

---

## Pré-requisitos e Instalação

### 1. Python
Versão recomendada: **Python 3.12+**

### 2. Dependências Python

Instale as bibliotecas necessárias via pip:

```bash
pip install psycopg2
pip install tkcalendar
```

### 3. PostgreSQL

Instale e inicie o PostgreSQL. As configurações de conexão padrão usadas no projeto são:

| Campo    | Valor                          |
|----------|--------------------------------|
| Host     | localhost                      |
| Porta    | 5432                           |
| Usuário  | postgres                       |
| Senha    | postgres                       |
| Banco    | db_lpoo_locadora_veiculos      |

Para alterar essas configurações, edite o arquivo `dao/db_config.py`.

### 4. Criação do Banco de Dados

No pgAdmin, execute:

```sql
CREATE DATABASE db_lpoo_locadora_veiculos;
```

### 5. Criação das Tabelas

Conecte-se ao banco criado e execute o seguinte script SQL:

```sql
-- Tabela de Veículos
CREATE TABLE IF NOT EXISTS tb_veiculos (
    vei_placa        CHAR(7)         PRIMARY KEY,
    vei_categoria    VARCHAR(20)     NOT NULL,
    vei_taxa_diaria  NUMERIC(10, 2)  NOT NULL CHECK (vei_taxa_diaria > 0),
    vei_estado_atual VARCHAR(20),
    vei_tipo         VARCHAR(20)     NOT NULL
);

-- Tabela de Locações
CREATE TABLE IF NOT EXISTS tb_locacoes (
    loc_id            SERIAL       PRIMARY KEY,
    loc_placa_veiculo CHAR(7)      NOT NULL,
    loc_data_inicio   DATE         NOT NULL,
    loc_data_fim      DATE         NOT NULL,
    loc_status        VARCHAR(20)  NOT NULL DEFAULT 'reservado',
    loc_estrategia    VARCHAR(20)  NOT NULL DEFAULT 'padrao',
 
    CONSTRAINT fk_veiculo
        FOREIGN KEY (loc_placa_veiculo)
        REFERENCES tb_veiculos(vei_placa)
        ON DELETE CASCADE,
 
    CONSTRAINT chk_datas
        CHECK (loc_data_fim >= loc_data_inicio),
 
    CONSTRAINT chk_status
        CHECK (loc_status IN ('reservado', 'locado', 'devolvido', 'cancelado')),
 
    CONSTRAINT chk_estrategia
        CHECK (loc_estrategia IN ('padrao', 'vip'))
);
```

### 6. Executar o sistema

```bash
python main.py
```

---

## Estrutura do Projeto

```
Locadora/
├── main.py                          # Ponto de entrada — inicia a JanelaPrincipal
│
├── control/
│   ├── __init__.py
│   ├── veiculo_controller.py        # Regras de negócio de veículos
│   └── locacao_controller.py        # Regras de negócio de locações (Admin e Usuário)
│
├── dao/
│   ├── __init__.py
│   ├── db_config.py                 # Configuração da conexão com PostgreSQL
│   ├── generic_dao.py               # Interface abstrata CRUD (ABC)
│   ├── veiculo_dao.py               # Persistência de veículos
│   └── locacao_dao.py               # Persistência de locações
│
├── model/
│   ├── __init__.py
│   ├── Veiculo.py                   # Classe abstrata base
│   ├── Carro.py                     # Herda de Veiculo
│   ├── Motorhome.py                 # Herda de Veiculo
│   ├── Categoria.py                 # Enum: ECONOMICO, EXECUTIVO, LUXO
│   ├── StatusLocacao.py             # Enum: reservado, locado, devolvido, cancelado
│   ├── Estados_Veiculo.py           # Padrão State: Disponivel, Alugado, Manutencao
│   ├── Locacao.py                   # Modelo de locação com status e estratégia
│   ├── LocacaoStrategy.py           # Padrão Strategy: Padrão e VIP
│   ├── Decoradores.py               # Padrão Decorator: GPS e SeguroTerceiros
│   ├── VeiculoFactory.py            # Padrão Factory: cria Carro ou Motorhome
│   └── ExcecoesPersonalizadas.py    # Exceções: PlacaInvalidaError, DataInvalidaError
│
└── views/
    ├── __init__.py
    ├── main_view.py                 # JanelaPrincipal (tk.Tk) — barra de menus
    ├── veiculo_list_view.py         # Listagem e CRUD de veículos
    ├── veiculo_view.py              # Formulário de cadastro/edição de veículo
    ├── locacao_list_view.py         # Listagem e CRUD de locações (Admin)
    ├── locacao_cadastro_view.py     # Formulário de cadastro/edição de locação (Admin)
    ├── locacao_usuario_view.py      # Listagem operacional (Usuário)
    └── locacao_nova_reserva_view.py # Formulário de nova reserva (Usuário)
```

---

## Detalhamento de Aprendizado

### Dificuldades Encontradas

- Compreender a hierarquia de janelas do Tkinter: entender a diferença entre `tk.Tk()` e `tk.Toplevel` e por que só pode existir uma instância raiz em toda a aplicação.
- Estruturar o fluxo MVC com DAO: separar corretamente as responsabilidades entre View, Controller e DAO exigiu atenção para não misturar regras de negócio com lógica de interface.
- Implementar os botões com habilitação condicional: controlar o estado (`normal`/`disabled`) dos botões da tela do usuário de acordo com o status da locação selecionada exigiu o uso do evento `<<TreeviewSelect>>` e um método dedicado para atualizar os botões a cada seleção.
- Relacionamento entre tabelas no banco: definir a chave estrangeira entre `tb_locacoes` e `tb_veiculos`, e decidir usar a placa como chave primária natural em vez de um `id` artificial, qual foi uma decisão importante.

### Como Resolvi

- Revisei o padrão já aplicado no CRUD de Veículos nas aulas anteriores e repliquei a mesma estrutura para as locações, adaptando onde necessário para as regras específicas de cada tela (Admin e Usuário).

### Principal Aprendizado

- Entendi na prática como o padrão MVC organiza o código e facilita a manutenção: cada camada tem uma responsabilidade clara, e alterações em uma não quebram as outras.
- Aprendi como o `wait_window()` trava o fluxo da janela pai e por que ele é necessário para recarregar os dados após fechar uma janela filha.
- Compreendi a importância de separar as regras de negócio do usuário (com restrições de status, datas e fluxo) das operações do administrador (irrestrito), implementando métodos distintos no controller para cada perfil.
- O uso de Enums (`StatusLocacao`, `Categoria`) para controlar valores fixos evitou erros de strings avulsas e tornou o código mais seguro e legível.

---

## Declaração de Uso de IA

- [x] **Utilizei IA** como ferramenta de apoio.
- **Ferramenta:** Claude Sonnet 4.6 (Anthropic) — via claude.ai
- **Finalidade:** Apoio na estruturação e formatação do código seguindo o padrão MVC já adotado no projeto, geração dos scripts SQL de criação das tabelas, auxílio na resolução de erros durante o desenvolvimento e elaboração do README do repositório.
- **Validação:** Todo o código gerado foi lido, compreendido e testado. As decisões de estrutura e arquitetura foram tomadas com base no conteúdo das aulas e nos requisitos da atividade.