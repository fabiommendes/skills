---
name: audit-db
description: Auditoria de acesso ao banco de dados de uma base de código, cobrindo queries N+1, índices ausentes, constraints de unicidade, comportamento de ON DELETE, consistência e justificativa da desnormalização, leituras sem limite, transações e concorrência, constraints de integridade e segurança das migrações. Entregue como relatório em PDF/HTML com issues do GitHub prontas para colar. Use quando o usuário pedir uma auditoria de banco de dados, ORM, schema ou desempenho de queries, ou perguntar sobre queries N+1, índices, cascatas ou consistência de dados.
---

# Auditoria: acesso ao banco de dados

Audite o schema e a forma como os serviços, repositórios e outras camadas de acesso a
dados da aplicação o usam, e entregue o relatório definido pela skill `audit-report`.
A pergunta de cada achado é o que acontece quando as tabelas crescem e quando chegam
dados reais: duplicatas, exclusões, requisições concorrentes.

Injeção de SQL e filtros de tenant ausentes ficam com `audit-webserver`; retenção de
dados pessoais fica com `audit-privacy`.

Copie este checklist e acompanhe-o:

```
- [ ] 1. Carregar audit-report
- [ ] 2. Detectar a stack e pedir um banco de dados
- [ ] 3. Montar os inventários de tabelas e de queries
- [ ] 4. Verificar cada categoria
- [ ] 5. Sintetizar e renderizar
```

## 1. Carregar audit-report

Invoque a skill `audit-report` agora e inicie ou retome o log. Ela define como você
registra os achados conforme avança. A área é `db`; o prefixo do título da issue é
`[DB]`.

## 2. Detectar a stack e pedir um banco de dados

Identifique o motor do banco, o ORM ou query builder (Django ORM, SQLAlchemy,
ActiveRecord, Prisma, TypeORM, Drizzle, Sequelize, JPA/Hibernate, Ecto, GORM, SQL
puro), onde o schema é definido (models, migrações, arquivos SQL) e as camadas que
fazem as queries (serviços, repositórios, resolvers, serializers, templates). Registre
o mapeamento em `methodology`.

O schema das migrações é a referência. Quando models e migrações divergem, registre a
divergência em `integrity` e use as migrações.

Pergunte ao usuário se há um banco com volume realista disponível: uma cópia de teste
ou de staging, ou estatísticas somente leitura de produção. Com um banco, leia a
contagem de linhas e o uso de índices (`pg_class.reltuples`, `pg_stat_user_tables`,
`pg_stat_user_indexes`, ou o equivalente do motor) e execute `EXPLAIN` nos pontos de
query em tabelas grandes. Execute `EXPLAIN ANALYZE` só em banco de teste, porque ele
executa a query. Nunca escreva em nenhum banco. Sem banco, audite a partir do código,
diga isso em `methodology` e estime o tamanho das tabelas como o passo 3 descreve.

Quando os testes do projeto rodam localmente, conte as queries que um endpoint de
listagem dispara, ligando o log de queries do ORM por configuração ou variáveis de
ambiente, sem editar arquivos do projeto. Contagens de queries que crescem com o
número de linhas são a evidência mais forte de N+1.

## 3. Montar os inventários de tabelas e de queries

Registre duas tabelas de inventário.

**Tabelas.** Uma linha por tabela: tabela, `file:line` do model ou da migração, classe
de tamanho, índices, constraints de unicidade, chaves estrangeiras com a regra de ON
DELETE, e colunas desnormalizadas. Classes de tamanho:

- `large`: cresce com usuários, eventos ou tempo (pedidos, mensagens, logs, trilhas de
  auditoria, itens de linha);
- `medium`: cresce com clientes ou tenants (contas, projetos);
- `small`: limitada (configurações, tabelas de consulta, planos).

Use contagens de linhas quando o passo 2 deu um banco; caso contrário, informe o
fator de crescimento como motivo.

**Pontos de query.** Comece pelas rotas, jobs e comandos, siga-os até os serviços e
repositórios, e registre uma linha por query em uma tabela `large` ou `medium`:
`file:line` do ponto, ponto de entrada (rota ou job), tabela, colunas de filtro, join
e ordenação, o índice que as atende, e se roda dentro de um loop. Conte os pontos de
entrada para confirmar que nenhum foi pulado. Em uma base grande, cubra um módulo por
vez e registre cada módulo como concluído em `methodology`, em vez de amostrar.

## 4. Categorias

### 1. Queries N+1 (`n-plus-one`)

Uma query por linha de um resultado anterior: relações lidas dentro de loops,
templates e serializers (serializers DRF aninhados, modelos Pydantic criados a partir
de objetos do ORM, métodos `to_json`) sem carregamento antecipado (`select_related`,
`prefetch_related`, `joinedload`, `selectinload`, `includes`, `include`, `JOIN FETCH`);
resolvers GraphQL sem agrupamento (DataLoader); e escritas em loop (insert, update ou
delete por linha) quando existe uma operação em lote. Também o oposto: carregamento
antecipado de coleções grandes que o chamador não usa.

### 2. Índices (`indexes`)

Em tabelas `large` e `medium`: filtros, joins, ordenações e checagens de unicidade em
colunas sem índice cujas colunas iniciais batam; colunas de chave estrangeira sem
índice (o PostgreSQL não cria um); buscas sem diferença entre maiúsculas e minúsculas
ou baseadas em função (`lower(email)`, `LIKE '%termo%'`) que um índice simples não
atende. Também índices redundantes (um é prefixo de outro) e índices que nenhuma query
usa, que custam em toda escrita.

### 3. Constraints de unicidade (`uniqueness`)

Unicidade que o código assume e o banco não garante (corridas entre verificar e
inserir, get-or-create sem constraint), e regras de unicidade que falham com dados
reais. Para constraints de unicidade compostas, em especial, verifique:

- o escopo: global quando deveria ser por tenant ou por pai, ou por pai quando
  deveria ser global;
- colunas nulas: a maioria dos motores trata NULLs como distintos, então
  `UNIQUE (tenant_id, external_id)` aceita duplicatas quando `external_id` é NULL;
- normalização: maiúsculas, acentos e espaços em e-mails, slugs e nomes;
- exclusão lógica: uma regra de unicidade que impede recriar um registro excluído, ou
  que ignora `deleted_at` e deixa entrar duplicatas ativas (um índice único parcial
  resolve os dois);
- chaves naturais que se repetem na vida real (nomes de pessoas, títulos, telefones
  compartilhados por uma família).

### 4. Comportamento de ON DELETE (`on-delete`)

Para cada chave estrangeira, o que a exclusão do pai faz, e se isso está documentado e
é intencional:

- cascatas que apagam dados que os usuários ainda precisam (apagar um usuário apaga as
  faturas da empresa dele), e cadeias longas de cascata;
- `SET NULL` em uma coluna que o model trata como obrigatória;
- o cascade do ORM divergindo do cascade do banco (`on_delete` do Django e `cascade=`
  do SQLAlchemy rodam na aplicação, então exclusões em lote, SQL puro e outros clientes
  os contornam, e signals não disparam);
- pais com exclusão lógica cujos filhos continuam ativos;
- relações sem chave estrangeira nenhuma, que deixam registros órfãos.

### 5. Consistência da desnormalização (`denorm-consistency`)

Para cada valor desnormalizado (contadores, totais, campos copiados, JSON em cache,
views materializadas), liste todo caminho de código que escreve o dado de origem e
verifique se cada um atualiza a cópia na mesma transação, ou se um trigger ou job de
recálculo a mantém correta. Distinga snapshots, valores copiados de propósito para
guardar histórico (o preço em uma linha de pedido), de caches, que precisam acompanhar
a origem.

### 6. Justificativa da desnormalização (`denorm-justification`)

Valores desnormalizados sem caminho de leitura crítico que os use, sem medição ou
comentário que os explique, ou sem um join indexado barato que os substituiria.

### 7. Leituras sem limite (`unbounded`)

Endpoints e jobs de listagem sem limite ou paginação em tabelas `large`; tabelas ou
coleções inteiras carregadas na memória; `SELECT *` ou carga completa de model que
traz colunas grandes (blobs, JSON, texto) que o chamador não usa; contagens ou
checagens de existência que carregam linhas (`len(queryset)`); paginação com `OFFSET`
profundo em tabelas `large` onde a paginação por chave serve.

### 8. Transações e concorrência (`transactions`)

Operações que escrevem várias linhas ou tabelas sem transação; leitura-modificação-
escrita sem trava de linha ou atualização atômica (`balance = balance + x` calculado na
aplicação perde atualizações); chamadas externas (HTTP, e-mail, filas) dentro de uma
transação, ou eventos publicados antes do commit; transações abertas durante a
interação com o usuário ou durante loops longos; premissas de nível de isolamento que
o motor não oferece.

### 9. Constraints de integridade (`integrity`)

Regras de que o código depende e que o schema não garante: chaves estrangeiras
ausentes, colunas que aceitam nulo onde o código exige valor, status e enums guardados
como texto livre sem CHECK ou tipo enum, valores monetários sem CHECK de sinal, dinheiro
em ponto flutuante, timestamps sem fuso horário, e divergência entre models e
migrações.

### 10. Segurança das migrações (`migrations`)

Migrações que travam ou reescrevem tabelas `large`: criação de índice sem
`CONCURRENTLY` (ou o equivalente online do motor), coluna NOT NULL adicionada sem
default ou preenchimento, mudanças de tipo que reescrevem a tabela, e migrações de
dados na mesma transação de mudanças de schema. Também migrações que não podem ser
revertidas sem aviso, e mudanças de schema feitas fora da ferramenta de migração.

## Severidade

| Nível | Significado |
|---|---|
| `critical` | O uso normal perde ou corrompe dados: uma cascata apaga dados que os usuários ainda precisam, uma constraint de unicidade ausente deixa entrar pagamentos ou registros duplicados com efeito legal, requisições concorrentes perdem atualizações de saldo ou estoque. |
| `high` | Um caminho principal cujo custo cresce com uma tabela `large` (N+1, filtro ou ordenação sem índice, leitura sem limite), um valor desnormalizado que diverge e é mostrado aos usuários ou usado em decisões, ou uma migração que trava uma tabela `large`. |
| `medium` | O mesmo em um caminho secundário ou em uma tabela `medium`, ou uma regra de integridade aplicada só no código da aplicação, que funciona hoje. |
| `low` | Higiene sem efeito atual: índices redundantes ou não usados, uma desnormalização consistente sem justificativa, uma regra de ON DELETE intencional que não está documentada. |
| `info` | Uma observação sem risco por si só. |

## 5. Sintetizar e renderizar

Registre as dez categorias, os achados e os pontos fortes conforme `audit-report`
define, escreva a síntese e renderize. Para cada achado, coloque o schema e o ponto de
query em `location`, a classe de tamanho da tabela e a contagem de linhas, quando
conhecidas, em `conditions`, e as contagens de queries ou a saída de `EXPLAIN` em
`description`, quando você mediu. Marque os achados feitos só a partir do código, sem
medição, com "a partir do código" em `conditions`.
