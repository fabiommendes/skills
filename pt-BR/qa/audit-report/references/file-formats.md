# Formatos de arquivo

Referência para mantenedores. Agentes nunca leem nem gravam estes arquivos
diretamente: eles passam pelo `audit-findings`, descrito no `SKILL.md`. Os
formatos são os do `audit-findings` 0.4.0.

Uma auditoria fica em `docs/audits/<area>/`:

| Arquivo | Papel |
|---|---|
| `findings.jsonl` | O log somente de acréscimo. A única fonte de verdade enquanto a auditoria roda. |
| `findings.jsonl.lock` | Arquivo de lock mantido durante cada leitura e escrita. Vazio. |
| `.gitignore` | Gravado por `init`; ignora o arquivo de lock. |
| `findings.json` | Montado a partir do log por `build` e `render`. Entrada do renderizador. |
| `report.pdf`, `report.html`, `issues.md` | Gravados por `render`. |
| `screenshots/` | Imagens opcionais referenciadas pelos achados. |

## findings.jsonl

Um objeto JSON por linha, acrescentado sob lock e nunca reescrito. Reproduzir as
linhas em ordem dá os registros atuais.

### Eventos

| Campo | Presente | Significado |
|---|---|---|
| `op` | sempre | `add`, `update`, `remove`, `accept` ou `distinct`. |
| `id` | sempre | ID do registro. |
| `type` | `add` | Tipo do registro (veja abaixo). |
| `data` | `add`, `update`, `distinct` | `add`: o registro inteiro. `update`: os campos a alterar. `distinct`: `{"ids": [...]}`. |
| `reason` | `remove` | Motivo da remoção, como `duplicate of F1`. |
| `agent` | quando `--agent` foi passado | Rótulo livre do agente que fez a alteração. |
| `ts` | sempre | Hora UTC da alteração, ISO 8601, em segundos. |

Regras de reprodução:

- `add` cria o registro. Seu `agent` é o criador do registro.
- `update` mescla `data` no registro; um valor `null` apaga o campo. Ele limpa a
  marca de aceito.
- `accept` marca o registro como revisado até o próximo `update`.
- `distinct` declara que o `id` do achado e cada achado em `data.ids` são defeitos
  diferentes. `status`, `coverage` e `render` deixam de informar esses pares como
  sobrepostos. Ele não altera a marca de aceito.
- `remove` move o registro para o conjunto de removidos, com seu `reason`. Um
  registro removido mantém seus dados e seu histórico, pode ser exibido e não pode
  mais ser alterado.
- IDs nunca são reutilizados: o próximo ID gerado é um a mais que o maior já usado
  com aquele prefixo, incluindo os removidos.
- Um `op` desconhecido, um ID desconhecido ou uma linha que não é JSON tornam o log
  ilegível; o erro indica a linha.

### Tipos de registro

IDs gerados são um prefixo mais um número. Tipos sem prefixo carregam o próprio
`id` em `data`, escolhido pelo agente.

| Tipo | ID | Campos (obrigatórios em negrito) |
|---|---|---|
| `meta` | `meta` (um registro) | `lang`, `title`, `project`, `date`, `scope`, `methodology` |
| `category` | `id` próprio | **`id`**, **`title`**, `applies`, `note`, `status` |
| `finding` | `F1`, `F2`, ... | **`category`**, **`severity`**, **`title`**, **`location`**, **`description`**, **`impact`**, **`fix`**, `snippet`, `language`, `conditions`, `screenshot`, `mechanical` |
| `strength` | `S1`, ... | **`text`**, `category`, `evidence` |
| `risk` | `R1`, ... | **`text`** |
| `recommendation` | `REC1`, ... | **`priority`**, **`text`**, `findings` |
| `issue` | `I1`, ... | **`title`**, **`findings`**, **`summary`**, **`acceptance`**, `labels` |
| `inventory` | `id` próprio | **`id`**, **`columns`**, `title` |
| `row` | `ROW1`, ... | **`table`** (um id de inventário), **`cells`** |

Checagens feitas quando um registro é adicionado ou atualizado:

- Nenhum campo desconhecido; campos obrigatórios não podem estar vazios.
- `lang` é `en` ou `pt`; `severity` é `critical`, `high`, `medium`, `low` ou
  `info`; `status` é `todo`, `doing` ou `done`.
- `category`, os ids em `findings` e `table` se referem a registros existentes.
- Uma linha tem tantos `cells` quanto `columns` tem o inventário.
- `screenshot` existe em caminho relativo ao diretório da auditoria.
- `mechanical` é `true` ou `false`.
- Todo `path:line` em `location` de um achado e em `evidence` de um ponto forte
  existe, e toda linha de `snippet` aparece nas linhas citadas.

`init` preenche `lang` com `en` e `date` com a data local, quando faltam. `status`
em uma categoria é acompanhamento de progresso, gravado por `start`, `done` e
`reopen`; ele não chega ao `findings.json`.

### Exemplo

O log abaixo tem dois agentes registrando ao mesmo tempo, um duplicado unido ao
achado que ele repete, uma revisão e a síntese:

```json
{"op": "add", "id": "meta", "type": "meta", "data": {"lang": "en", "date": "2026-10-08", "title": "Security Audit Report", "project": "acme-api", "scope": "FastAPI backend in `src/`."}, "ts": "2026-10-09T01:53:09+00:00"}
{"op": "add", "id": "idor", "type": "category", "data": {"id": "idor", "title": "IDOR"}, "ts": "2026-10-09T01:53:09+00:00"}
{"op": "add", "id": "xss", "type": "category", "data": {"id": "xss", "title": "XSS", "applies": false, "note": "No HTML rendering of user input."}, "ts": "2026-10-09T01:53:09+00:00"}
{"op": "update", "id": "meta", "data": {"methodology": "Read every router in `src/api/`."}, "ts": "2026-10-09T01:53:09+00:00"}
{"op": "update", "id": "idor", "data": {"status": "doing"}, "agent": "a1", "ts": "2026-10-09T01:53:09+00:00"}
{"op": "add", "id": "F1", "type": "finding", "data": {"category": "idor", "severity": "critical", "title": "GET /invoices/{id} does not check the tenant", "location": "src/api/invoices.py:1-2", "snippet": "return db.query(Invoice).filter(Invoice.id == invoice_id).first()", "language": "python", "description": "No tenant filter.", "impact": "Any user reads any invoice.", "fix": "Filter by the caller tenant.", "conditions": "Any authenticated user."}, "agent": "a1", "ts": "2026-10-09T01:53:09+00:00"}
{"op": "add", "id": "F2", "type": "finding", "data": {"category": "idor", "severity": "critical", "title": "GET /invoices/{id} does not check the tenant", "location": "src/api/invoices.py:1-2", "snippet": "return db.query(Invoice).filter(Invoice.id == invoice_id).first()", "language": "python", "description": "No tenant filter.", "impact": "Any user reads any invoice.", "fix": "Filter by the caller tenant.", "conditions": "Any authenticated user."}, "agent": "a2", "ts": "2026-10-09T01:53:09+00:00"}
{"op": "add", "id": "S1", "type": "strength", "data": {"category": "idor", "text": "The users router checks ownership.", "evidence": "src/api/users.py:1-2"}, "agent": "a1", "ts": "2026-10-09T01:53:09+00:00"}
{"op": "add", "id": "routes", "type": "inventory", "data": {"id": "routes", "title": "Route inventory", "columns": ["Method", "Path"]}, "agent": "a1", "ts": "2026-10-09T01:53:09+00:00"}
{"op": "add", "id": "ROW1", "type": "row", "data": {"table": "routes", "cells": ["GET", "/invoices/{id}"]}, "agent": "a1", "ts": "2026-10-09T01:53:09+00:00"}
{"op": "add", "id": "ROW2", "type": "row", "data": {"table": "routes", "cells": ["GET", "/users/{id}"]}, "agent": "a1", "ts": "2026-10-09T01:53:09+00:00"}
{"op": "update", "id": "idor", "data": {"status": "done"}, "agent": "a1", "ts": "2026-10-09T01:53:09+00:00"}
{"op": "remove", "id": "F2", "reason": "duplicate of F1", "ts": "2026-10-09T01:53:09+00:00"}
{"op": "accept", "id": "F1", "ts": "2026-10-09T01:53:10+00:00"}
{"op": "accept", "id": "S1", "ts": "2026-10-09T01:53:10+00:00"}
{"op": "add", "id": "R1", "type": "risk", "data": {"text": "Tenant isolation depends on a manual filter in every query."}, "ts": "2026-10-09T01:53:10+00:00"}
{"op": "add", "id": "REC1", "type": "recommendation", "data": {"priority": "P1", "text": "Add a tenant filter to every invoice query.", "findings": ["F1"]}, "ts": "2026-10-09T01:53:10+00:00"}
{"op": "add", "id": "I1", "type": "issue", "data": {"title": "[Security] IDOR in GET /invoices/{id}", "labels": ["security", "critical"], "findings": ["F1"], "summary": "Invoices are fetched without a tenant check.", "acceptance": ["A request for another tenant invoice returns 404"]}, "ts": "2026-10-09T01:53:10+00:00"}
```

## findings.json

`build` transforma os registros vivos neste arquivo; o renderizador lê apenas este
arquivo. Agentes, carimbos de tempo, marcas de revisão, pares distintos, progresso
das categorias, registros removidos e IDs de inventário não chegam a ele. Sem log,
um `findings.json` escrito à mão é renderizado diretamente com `render <path>`, e
`import <path>` o transforma em log.

| Campo | Tipo | Obrigatório | Montado a partir de |
|---|---|---|---|
| `lang` | `"en"` ou `"pt"` | não, padrão `en` | `meta` |
| `title`, `project`, `date`, `scope`, `methodology` | texto | sim | `meta` |
| `categories` | lista de `{id, title, applies?, note?}` | sim | registros `category`, na ordem de criação |
| `findings` | lista de objetos de achado com `id` | sim | registros `finding`, em ordem de id |
| `strengths` | lista de `{text, category?, evidence?}` | sim | registros `strength` |
| `risks` | lista de textos | não | o `text` dos registros `risk` |
| `recommendations` | lista de `{priority, text, findings?}` | sim | registros `recommendation` |
| `issues` | lista de `{title, findings, summary, acceptance, labels?}` | sim | registros `issue` |
| `inventory` | uma tabela ou lista de `{title, columns, rows}` | não | cada `inventory` com seus registros `row`; linhas idênticas são unidas |

Campos de texto renderizam trechos `` `código` ``; linhas em branco em
`methodology`, `description`, `impact`, `fix` e `conditions` separam parágrafos.
`recommendations` são ordenadas por `priority`, e os achados, por severidade dentro
de cada categoria, na renderização. Os `labels` de uma issue assumem por padrão as
severidades dos seus achados. `issues.md` termina com uma issue extra que reúne
todo achado com `"mechanical": true`, com o título no prefixo que as outras issues
compartilham; `coverage` não exige que esses achados estejam em uma issue própria.

O log de exemplo acima monta este resultado:

```json
{
  "lang": "en",
  "date": "2026-10-08",
  "title": "Security Audit Report",
  "project": "acme-api",
  "scope": "FastAPI backend in `src/`.",
  "methodology": "Read every router in `src/api/`.",
  "categories": [
    {"id": "idor", "title": "IDOR"},
    {"id": "xss", "title": "XSS", "applies": false, "note": "No HTML rendering of user input."}
  ],
  "findings": [
    {
      "id": "F1",
      "category": "idor",
      "severity": "critical",
      "title": "GET /invoices/{id} does not check the tenant",
      "location": "src/api/invoices.py:1-2",
      "snippet": "return db.query(Invoice).filter(Invoice.id == invoice_id).first()",
      "language": "python",
      "description": "No tenant filter.",
      "impact": "Any user reads any invoice.",
      "fix": "Filter by the caller tenant.",
      "conditions": "Any authenticated user."
    }
  ],
  "strengths": [
    {"category": "idor", "text": "The users router checks ownership.", "evidence": "src/api/users.py:1-2"}
  ],
  "risks": ["Tenant isolation depends on a manual filter in every query."],
  "recommendations": [
    {"priority": "P1", "text": "Add a tenant filter to every invoice query.", "findings": ["F1"]}
  ],
  "issues": [
    {
      "title": "[Security] IDOR in GET /invoices/{id}",
      "labels": ["security", "critical"],
      "findings": ["F1"],
      "summary": "Invoices are fetched without a tenant check.",
      "acceptance": ["A request for another tenant invoice returns 404"]
    }
  ],
  "inventory": [
    {
      "title": "Route inventory",
      "columns": ["Method", "Path"],
      "rows": [["GET", "/invoices/{id}"], ["GET", "/users/{id}"]]
    }
  ]
}
```
