---
name: skill-review
description: Revisa uma Agent Skill segundo as boas práticas de criação de skills da Anthropic e informa correções concretas. Use quando o usuário pedir para revisar, auditar ou criticar uma skill ou um arquivo SKILL.md.
disable-model-invocation: true
---

# Revisão de skill

Revise uma skill (um `SKILL.md` mais os arquivos que a acompanham) e informe o que
corrigir.

A menos que o usuário peça correções explicitamente, a revisão é uma tarefa de
leitura, não de reescrita. Não edite a skill, a não ser que o usuário peça
correções depois de ver o relatório.

## Fluxo de trabalho

Esta é a checklist da revisão de skill:

- Passo 1: localize a skill e liste os arquivos
- Passo 2: leia o SKILL.md e todos os arquivos que o acompanham
- Passo 3: avalie segundo a rubrica
- Passo 4: esboce três cenários de avaliação
- Passo 5: escreva o relatório
- Passo 6: se o usuário pedir correções, confirme as mudanças com ele antes de
  aplicá-las. Caso contrário, ignore este passo.

**Passo 1: localize a skill e liste os arquivos**

O alvo é um diretório que contém `SKILL.md`. Se o usuário citar uma skill sem
caminho, procure na coleção de skills um diretório com esse nome. Liste a árvore
inteira. Arquivos que nada referencia já são um achado.

**Passo 2: leia o SKILL.md e todos os arquivos que o acompanham**

Leia os arquivos inteiros, não trechos. Anote, para cada arquivo, qual linha do
SKILL.md aponta para ele.

**Passo 3: avalie segundo a rubrica**

Percorra o item a item o [reference/checklist.md](reference/checklist.md). Para
cada item, registre passa, falha ou não se aplica. Para cada falha, cite a linha
problemática e informe a substituição.

Depois, confira a prosa com as regras de escrita do idioma da skill:
[reference/writing-en.md](reference/writing-en.md) para inglês,
[reference/escrita-pt-br.md](reference/escrita-pt-br.md) para português. Informe
cada regra quebrada uma vez, com um exemplo citado e a sua reescrita.

**Passo 4: esboce cenários de avaliação**

Se o frontmatter não contiver `disable-model-invocation: false`, considere três
tarefas concretas que um usuário poderia trazer para esta skill: uma claramente
dentro do escopo, uma na borda do escopo e uma que *não* deveria acionar a skill.
Para cada uma, julgue só pelo campo `description` se a skill seria acionada. Um
quase acerto no caso dentro ou fora do escopo é um bug de descrição. Informe só se
a skill seria acionada de forma incorreta, e registre isso como achado.

**Passo 5: escreva o relatório**

Use o formato de relatório abaixo. Ordene os achados por impacto: primeiro os
problemas de descoberta (`name`, `description`), depois correção, estrutura e
acabamento.

## Formato do relatório

```markdown
# Review: <skill-name>

**Verdict:** ship as-is | fix before sharing | needs rework

## Blocking
- **<issue>** (`<file>:<line>`) — <what is wrong>. Fix: <specific replacement>

## Worth fixing
- ...

## Evaluation scenarios
1. In scope: "<task>" → triggers / misses
2. Edge: "<task>" → triggers / misses
3. Out of scope: "<task>" → correctly ignored / false trigger

## Checklist

```
<one line per rubric item: ✓ / ✗ / n/a. with a phrase only for items marked with an ✗>
```

Cada achado deve ser acionável. "Description is vague" não é um achado; uma
descrição substituta proposta é. Seja específico e conciso nas descrições.

## Julgamentos

A rubrica traz padrões, não leis. Antes de informar uma violação, pergunte se a
skill tem motivo para quebrar a regra:

- **Skills curtas.** Uma skill de 30 linhas sem arquivos auxiliares está bem. Não
  exija divulgação progressiva que ninguém precisa.
- **Graus de liberdade.** Instruções curtas e abertas são corretas para tarefas
  com muitas abordagens válidas. Roteiros rígidos, passo a passo, são corretos
  para tarefas frágeis. Aponte a divergência, não o estilo.
- **Convenções do repositório.** Se skills irmãs compartilham um campo do
  frontmatter ou um layout, trate isso como convenção local, não como defeito.

Informe no máximo um achado por causa de fundo. Uma descrição vaga e um termo de
gatilho ausente são um achado, não dois.
