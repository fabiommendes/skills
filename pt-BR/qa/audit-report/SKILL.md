---
name: audit-report
description: Define como as skills audit-* registram achados com a linha de comando audit-findings, que vários agentes podem compartilhar em paralelo e entre sessões, e como os transformam em um relatório em PDF, um relatório em HTML e issues do GitHub prontas para colar. Use quando uma skill de auditoria chegar ao primeiro passo, ou quando o usuário quiser regerar um relatório de auditoria a partir de um findings.json.
---

# Relatório de auditoria

Toda skill `audit-*` registra seus resultados com a linha de comando
`audit-findings` e os renderiza com ela. A skill de auditoria decide o que
procurar; esta skill decide como os achados são registrados e entregues.

Execute todo comando como `uvx audit-findings@0.4.0 <command>`, a partir da raiz
do projeto. Abaixo, esse prefixo aparece encurtado como `audit-findings`. Sem
`uv`, crie um ambiente virtual fora do projeto (`python3 -m venv /tmp/audit-venv`),
instale `audit-findings==0.4.0` nele e execute o `audit-findings` dele. Não
instale nada globalmente.

## Diretório de saída

Tudo vai para `docs/audits/<area>/`, em que `<area>` é o nome da skill de
auditoria sem o prefixo `audit-` (`webserver`, `db`, `dependencies`, `privacy`,
`ux`, `ui`). Passe `-a <area>` em todo comando.

| Arquivo | Gerado por |
|---|---|
| `findings.jsonl` | `audit-findings`, conforme você registra; nunca edite à mão |
| `screenshots/*.png` | você, quando um achado precisar de uma (opcional) |
| `findings.json`, `report.pdf`, `report.html`, `issues.md` | `audit-findings render` |

## Início ou retomada

Se `docs/audits/<area>/findings.jsonl` existir, a auditoria está em andamento:
execute `audit-findings -a <area> status` e continue a partir do que ele lista.
Não leia o log em si.

Caso contrário, crie-o e registre cada categoria da skill de auditoria:

```bash
audit-findings -a webserver init <<'EOF'
{"lang": "en", "title": "Security Audit Report", "project": "acme-api",
 "scope": "FastAPI backend in `src/`, React frontend in `web/`."}
EOF

audit-findings -a webserver add category <<'EOF'
[{"id": "idor", "title": "IDOR"},
 {"id": "xss", "title": "XSS", "applies": false, "note": "no HTML rendering of user input"}]
EOF
```

Use os ids e títulos de categoria que a skill de auditoria fornecer, e registre
toda categoria, inclusive as que não se aplicam: marque-as com `"applies": false`
e o motivo em `note`. Uma categoria com cobertura parcial diz isso em `note`.

Escreva todo o texto em um único idioma e defina `lang` como `en` ou `pt`. `date`
assume a data de hoje. Defina `methodology` assim que souber o método: parágrafos
separados por linhas em branco, com a stack detectada e como cada categoria se
mapeia nela.

```bash
audit-findings -a webserver update meta <<'EOF'
{"methodology": "..."}
EOF
```

Execute `start <category>` ao começar uma categoria e `done <category>` ao
terminá-la; `status` mostra então o que falta.

## Registro de achados

Passe os registros como JSON na entrada padrão, um objeto ou uma lista. `add`
imprime o id de cada registro e recusa o lote inteiro se um registro estiver
errado: um campo ausente, uma categoria desconhecida, ou um local ou trecho que
não está no código-fonte. Corrija o que ele informar e execute de novo.

```bash
audit-findings -a webserver add finding <<'EOF'
{"category": "idor", "severity": "critical",
 "title": "GET /invoices/{id} does not check the tenant",
 "location": "src/api/invoices.py:42-47",
 "snippet": "return db.query(Invoice).filter(Invoice.id == invoice_id).first()",
 "language": "python",
 "description": "What is wrong.",
 "impact": "What an attacker or user can do, or what goes wrong.",
 "fix": "The suggested fix.",
 "conditions": "Any authenticated user."}
EOF
```

- Registre só o que você verificou: código que leu, comando que executou, tela
  que viu. Nunca especule e nunca invente locais, CVEs ou citações.
- Um achado para cada defeito distinto. O mesmo erro repetido em vários lugares
  é um achado cujo `location` lista todos os lugares. Quando `add` avisar que um
  achado se sobrepõe a outro, leia os dois com `show`: execute `merge <id novo>
  <id antigo>` se forem o mesmo defeito, ou `distinct <id novo> <id antigo>` se
  não forem. Quando avisar que se sobrepõe a um achado removido antes, leia o
  motivo e remova o novo se o motivo se aplicar.
- Dê o local exato: `path:line` ou `path:start-end` para código; rota ou tela,
  mais os passos para chegar até ela, para achados de interface.
- Cite o código ofensivo em `snippet`, cortado às linhas que mostram o problema.
  Mascare valores secretos e dados pessoais: mantenha os quatro primeiros
  caracteres de um segredo com 12 ou mais caracteres e substitua o resto por
  `****`; substitua segredos menores por completo por `****`.
- Atribua a severidade com a tabela de severidade da skill de auditoria que você
  executa: `critical`, `high`, `medium`, `low` ou `info`.
- Registre as condições de exploração ou de reprodução em `conditions`: flags de
  funcionalidade, configuração necessária, papéis, dispositivos.
- Defina `"mechanical": true` quando a correção decorrer só do achado: sem decisão
  de projeto, sem escolha entre opções, e um revisor consegue confirmá-la pelo
  diff. Erro de digitação, condição invertida ou `await` ausente são mecânicos;
  uma nova abstração ou uma API alterada não são. Isso é independente da
  severidade: uma checagem de permissão invertida é mecânica e `critical`. O
  relatório reúne todas as correções mecânicas em uma issue, a ser aplicada em
  uma única passada.
- `snippet`, `language`, `conditions`, `screenshot` (caminho relativo ao diretório
  de saída) e `mechanical` são opcionais.

Registre o que está **correto** como pontos fortes, com evidência. Pontos fortes
comprovam a cobertura: "todo handler em `routers/orders.py` verifica a posse"
mostra que o router foi lido.

```bash
audit-findings -a webserver add strength <<'EOF'
{"category": "idor", "text": "Every handler in the users router checks ownership.",
 "evidence": "src/api/users.py:10-80"}
EOF
```

Quando a skill de auditoria pedir uma tabela de cobertura, declare-a uma vez e
adicione linhas conforme avança. Linhas idênticas são unidas na montagem do
relatório.

```bash
audit-findings -a webserver add inventory <<'EOF'
{"id": "routes", "title": "Route inventory", "columns": ["Method", "Path"]}
EOF
audit-findings -a webserver add row <<'EOF'
[{"table": "routes", "cells": ["GET", "/invoices/{id}"]}]
EOF
```

Para alterar um registro, passe os campos a alterar para `update <id>`; `null`
apaga um campo opcional. `remove <id> --reason "..."` apaga um registro do qual
nada depende; o motivo fica no log, e `list --removed` o mostra. `list [kind]
[--category C] [--severity S]` e `show <id>...` leem os registros de volta.

## Dividir a auditoria entre agentes

Em uma base de código grande, registre você mesmo o meta e as categorias, e
depois dê a cada subagente um conjunto de ids de categoria. Diga a cada subagente
que ele deve:

- invocar esta skill e seguir "Registro de achados";
- passar `--agent <seu nome>` em todo comando, com o nome que você deu a ele, e
  executar `start` e `done` para as categorias dele;
- registrar achados, pontos fortes e linhas de inventário, mas nenhum risco,
  recomendação ou issue;
- responder com os ids que registrou e as categorias que concluiu, não com os
  achados em si.

Quando a skill de auditoria dividir o trabalho por parte (um subagente por módulo
ou documento, cada um procurando várias categorias), dê a cada subagente a parte
dele e as categorias a procurar. Ele pula `start` e `done`; você executa `done`
para cada categoria depois que todas as partes forem revisadas.

O log trava cada escrita, então subagentes podem registrar ao mesmo tempo. O nome
do agente é um rótulo livre: o log o guarda em cada alteração, `show` mostra quem
alterou um registro e quando, e `list --agent <nome>` filtra pelo agente que o
criou. Ele nunca chega ao relatório. Não passe `--agent` por conta própria.

### Revisar achados de subagentes

`status` lista em "to review" todo achado e ponto forte que um subagente registrou
e que você ainda não aceitou. Revise cada um antes da síntese:

1. Leia-o com `show <id>` e releia o código citado.
2. Mantenha-o com `accept <id>`, depois de corrigi-lo com `update <id>` se
   necessário. Uma alteração posterior feita por qualquer agente com `update` o
   devolve para revisão.
3. Una um duplicado ao achado que ele repete com `merge <duplicado> <mantido>`:
   as referências em issues e recomendações passam para o achado mantido. Depois,
   faça `update` no achado mantido se o duplicado citava lugares que ele não cita.
4. Descarte um achado errado, não verificado ou fora do escopo com `remove <id>
   --reason "..."`. O motivo fica no log e é mostrado quando um agente registrar
   um achado no mesmo lugar depois.

Resolva todo par sobreposto que `status` listar: `merge` para o mesmo defeito,
`distinct` para defeitos diferentes. Siga para a síntese quando não restar nada a
revisar. Uma sessão posterior retoma do mesmo jeito, a partir de `status`.

## Síntese

Quando toda categoria estiver `done` ou não se aplicar, escreva as partes que
exigem a visão completa. `status` lista cada achado com id, severidade e título;
use `show` para os detalhes.

```bash
audit-findings -a webserver add risk <<'EOF'
["Tenant isolation depends on a manual filter in every query."]
EOF
audit-findings -a webserver add recommendation <<'EOF'
{"priority": "P1", "text": "What to do first.", "findings": ["F1"]}
EOF
audit-findings -a webserver add issue <<'EOF'
{"title": "[Security] IDOR in GET /invoices/{id}", "labels": ["security", "critical"],
 "findings": ["F1"], "summary": "The problem and why it matters.",
 "acceptance": ["A request for another tenant's invoice returns 404", "A test covers it"]}
EOF
```

- Cada issue recebe uma única correção acionável. Agrupe achados relacionados
  com a mesma correção em uma só issue, como vários segredos padrão, em vez de
  abrir uma issue por linha. Use o prefixo de título que a skill de auditoria
  define. Critérios de aceite são afirmações verificáveis. `labels` assume por
  padrão as severidades dos achados da issue.
- O renderizador compõe o corpo de cada issue a partir dos seus achados:
  evidência, impacto e correção vêm dos achados, então escreva esses campos de
  modo que se leiam sozinhos.
- Todo achado acima de `info` precisa estar em uma issue e em uma recomendação.
  Achados mecânicos precisam só da recomendação: o renderizador os reúne em uma
  última issue, então deixe-os fora das outras. Verifique com
  `audit-findings -a <area> coverage`, que lista os achados que faltam em uma das
  duas e as sobreposições ainda não resolvidas, e sai com erro até não restar
  nenhuma; `--all` inclui os achados `info`.

## Renderização

1. Renderize:

   ```bash
   audit-findings -a <area> render
   ```

   Ele verifica de novo cada local e trecho contra o código-fonte, grava
   `findings.json` e o renderiza. Para cada problema que ele informar, releia o
   código e faça `update` no achado, ou `remove` com um motivo se o código não
   estiver lá. Execute de novo até ele gravar os arquivos do relatório.
2. Confira o PDF visualmente: `pdftoppm -r 60 -png docs/audits/<area>/report.pdf /tmp/<area>-page`,
   depois olhe cada página. Corrija o que renderizar mal, como trechos longos
   demais para ler, com `update`, e renderize de novo. Entregue só quando cada
   página estiver legível.

Para regerar um relatório a partir de um `findings.json` que não tem log, execute
`audit-findings render <path>/findings.json`; acrescente `--no-check` se o
código-fonte tiver mudado desde então. Para continuar uma auditoria assim, execute
antes `audit-findings import <path>/findings.json`; ele cria o log ao lado do
arquivo.

## Entrega

No chat, informe:

1. Os achados, arquivo por arquivo e linha por linha, com a severidade.
2. A contagem por severidade.
3. Os caminhos de `findings.json`, `report.pdf`, `report.html` e `issues.md`.

Não abra issues no GitHub nem em qualquer outro rastreador, a menos que o usuário
peça.
