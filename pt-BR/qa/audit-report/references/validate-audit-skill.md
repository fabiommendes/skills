# Validando uma skill de auditoria

Instruções para um agente que deve verificar se uma skill `audit-*` usa
`audit-report` corretamente. Esta é uma revisão do texto da skill, não uma
auditoria de base de código: não execute a auditoria e não edite a skill, a menos
que seja pedido.

Leia antes `../SKILL.md` (a skill `audit-report`). Ela é o contrato que a skill de
auditoria deve seguir; cada verificação abaixo se refere a ela. Depois leia o
`SKILL.md` da skill de auditoria por inteiro.

Algumas skills de auditoria se ramificam: o `SKILL.md` direciona para um documento
por parte (como `spec.md`, `py.md`, `js.md`), e cada parte tem seu próprio
checklist e seus passos. Valide a parte que o usuário indicar, lendo-a junto com o
`SKILL.md`. Aplique a verificação 1 ao `SKILL.md` e as demais à parte; cite as
falhas como `<arquivo>:linha`. Cada parte define sua própria área e seu prefixo de
título de issue no passo 1.

## O que verificar

Verifique todo item e registre cada falha com seu `SKILL.md:linha`.

### 1. Frontmatter e introdução

- `name` é `audit-<area>`, e `<area>` é o nome do diretório sem o prefixo `audit-`.
- `description` diz o que a auditoria cobre, que ela é "entregue como relatório em
  PDF/HTML com issues do GitHub prontas para colar", e quando usá-la ("Use quando
  ...").
- A introdução diz que a skill entrega o relatório definido pela skill
  `audit-report`. Quando o escopo se sobrepõe a outra auditoria, diz qual auditoria
  é dona do tema compartilhado (como `audit-webserver` para controle de acesso).

### 2. Checklist

- A skill manda o agente copiar e acompanhar um checklist.
- O primeiro item é `1. Carregar audit-report`; o último é `<n>. Sintetizar e
  renderizar`.
- Cada item do checklist tem uma seção `## <n>. <título>` correspondente, com o
  mesmo número e título, na mesma ordem.
- Uma pré-condição que pode impedir a auditoria de começar, como um script que
  precisa passar, fica antes do checklist (por exemplo, em `## Antes de começar`),
  e não como passo numerado antes de `1. Carregar audit-report`.

### 3. Carregando audit-report

A seção `## 1. Carregar audit-report` deve:

- mandar o agente invocar a skill `audit-report` agora e iniciar ou retomar o log,
  como primeira ação;
- indicar a área, igual a `<area>` do nome da skill;
- indicar o prefixo do título da issue, entre colchetes, como `[DB]`.

Reprove a skill se ela carregar `audit-report` depois do passo 1, tornar o
carregamento opcional, ou descrever ela mesma as regras de registro em vez de
remetê-las a `audit-report`.

### 4. Categorias

- Toda categoria tem um id estável entre crases, ao lado do título, como
  `### 3. IDOR (`idor`)` ou `1. **Conclusão de tarefas (`tasks`):**`. Os ids são
  minúsculos, usam só letras, dígitos e hífens, e são únicos dentro da skill.
- As categorias estão listadas em um único lugar. Toda categoria que um passo
  menciona, como "(categoria: x)", está nessa lista, e todo tipo de falha que um
  passo pede ao agente ou a um subagente registrar corresponde a uma categoria. Uma
  falha sem categoria faz o agente inventar uma, e `add` a recusa.
- O último passo declara o número de categorias por extenso ("todas as dez
  categorias"), e o número corresponde às categorias listadas.
- Quando uma categoria pode não se aplicar, a skill diz isso em vez de forçar um
  achado. Ela pode dizer como reconhecer o caso; não pode inventar um campo para ele
  (`audit-report` usa `applies` e `note`).

### 5. Severidade

- Uma tabela `## Severidade` define exatamente os cinco níveis `critical`, `high`,
  `medium`, `low` e `info`, cada um com um significado específico desta auditoria.
- A tabela vem antes do primeiro passo que registra achados, e todo briefing de
  subagente a repassa. Uma tabela dentro do passo de síntese vem tarde demais: os
  achados já foram registrados com severidade.

### 6. Inventário

Quando a skill monta uma tabela de cobertura:

- ela manda registrá-la como tabela de inventário (ou tabelas), nomeia cada coluna
  e diz o que é uma linha ("uma linha por rota");
- não se refere a um campo `inventory`, a uma lista de tabelas ou a qualquer
  formato JSON.

### 7. Campos citados nas instruções

Todo campo que a skill manda o agente preencher deve existir em `audit-findings`:

| Registro | Campos |
|---|---|
| meta | `lang`, `title`, `project`, `date`, `scope`, `methodology` |
| category | `id`, `title`, `applies`, `note` |
| finding | `category`, `severity`, `title`, `location`, `snippet`, `language`, `description`, `impact`, `fix`, `conditions`, `screenshot`, `mechanical` |
| strength | `text`, `category`, `evidence` |

Reprove qualquer outro nome de campo, como `cwe`, `coverage`, `evidence` em um
achado, ou `inventory`. Fatos sem campo próprio, como um id de CVE, um critério
WCAG ou uma contagem de queries medida, devem ser colocados em um campo existente
(`title`, `description`, `conditions`), e a skill deve dizer qual.

### 8. Sintetizar e renderizar

O último passo deve:

- mandar o agente registrar todas as categorias, os achados e os pontos fortes
  conforme `audit-report` define, escrever a síntese e renderizar;
- dar apenas orientação específica da auditoria: o que vai em `location`,
  `conditions` ou `description` para este tipo de achado, e quando agrupar achados
  em uma issue;
- remeter a entrega a `audit-report` ou seguir o mesmo formato (achados com
  severidade, contagens, caminhos dos entregáveis).

### 9. O que a skill não pode conter

Reprove a skill se ela:

- mandar o agente escrever, preencher ou editar `findings.json` ou `findings.jsonl`;
- citar `render_report.py`, `check_findings.py`, um diretório `scripts/` ou
  `uv run --with reportlab`;
- escrever comandos `audit-findings` com versão fixada. A fixação fica só em
  `audit-report`; uma segunda cópia fica desatualizada no próximo lançamento;
- citar um comando ou tipo de registro de `audit-findings` que não existe (veja
  "Comandos" abaixo);
- mandar o agente instalar ferramentas globalmente, ou abrir issues no GitHub sem
  o usuário pedir;
- mandar subagentes registrarem riscos, recomendações ou issues; isso pertence à
  síntese do agente principal.

### 10. Subagentes

Quando a skill cria subagentes:

- cada briefing aponta para "Dividir a auditoria entre agentes" em `audit-report`,
  em vez de repetir as regras de registro;
- uma divisão por parte, e não por categoria (um subagente por documento ou
  módulo), manda o subagente pular `start` e `done`, como `audit-report` descreve;
- o agente principal revisa os achados deles como "Revisar achados de subagentes"
  descreve, antes da síntese.

### 11. Editando a fonte auditada

Quando a skill manda o agente editar os arquivos que audita, como corrigir erros de
digitação em uma especificação, os locais e trechos registrados podem ficar
desatualizados. A skill deve manter os números de linha estáveis, ou mandar o
agente executar `audit-findings check` depois de cada rodada de edições e `update`
nos achados que ele informar.

### 12. Capturas de tela

Quando a auditoria precisa de capturas de tela (auditorias de interface), a skill as
salva em `docs/audits/<area>/screenshots/` e põe em `screenshot` do achado o caminho
relativo a `docs/audits/<area>/`. Ela mascara dados pessoais nas capturas quando a
auditoria trata dados pessoais.

## Comandos

Confira cada comando que a skill cita com `audit-findings --help`. Pegue a versão
fixada da linha `Execute todo comando como` de `../SKILL.md` e execute, em um diretório
temporário vazio:

```bash
uvx audit-findings@<version> --help
```

Tipos de registro aceitos por `add`: `category`, `finding`, `strength`, `risk`,
`recommendation`, `issue`, `inventory`, `row`.

## Teste de simulação

Confirme que as categorias da skill são registradas corretamente. Em um diretório
temporário vazio, fora de qualquer repositório:

```bash
uvx audit-findings@<version> -a <area> init <<'EOF'
{"title": "Validation", "project": "validation", "scope": "-", "methodology": "-"}
EOF
uvx audit-findings@<version> -a <area> add category <<'EOF'
[{"id": "<id 1>", "title": "<title 1>"}, {"id": "<id 2>", "title": "<title 2>"}]
EOF
uvx audit-findings@<version> -a <area> status
```

Liste todas as categorias da skill na chamada de `add category`, com os ids e os
títulos exatamente como a skill os escreve. A chamada deve imprimir um id por
categoria, e `status` deve listar o mesmo número de categorias que o passo final
declara. Quando a skill monta um inventário, adicione-o também, com as colunas que
a skill nomeia e uma linha de células de placeholder:

```bash
uvx audit-findings@<version> -a <area> add inventory <<'EOF'
{"id": "<table id>", "title": "<title>", "columns": ["<column 1>", "<column 2>"]}
EOF
uvx audit-findings@<version> -a <area> add row <<'EOF'
{"table": "<table id>", "cells": ["-", "-"]}
EOF
```

Apague o diretório temporário ao terminar.

## Relatório

Responda com:

1. `OK` e as verificações que passaram, quando nada falhou.
2. Caso contrário, uma linha por falha: o número da verificação, `SKILL.md:linha`,
   o que está errado e a correção. Marque cada falha como **bloqueante** (o agente
   que roda a auditoria gravaria dados errados, pularia um passo ou executaria um
   comando que falha) ou **menor** (redação que funciona, mas se afasta das outras
   skills de auditoria).
3. A saída do teste de simulação, reduzida aos ids e ao resumo de `status`.
