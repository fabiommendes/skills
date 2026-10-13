---
name: triage
description: Triar bugs e dívida técnica em um backlog priorizado para o humano aprovar. Use quando o usuário pedir para triar issues, priorizar bugs, organizar o backlog ou encontrar dívida técnica que vale a pena pagar.
argument-hint: "[bugs|debt|all]"
---

# Triagem

Você age como o mantenedor do projeto: reúne o que está errado no projeto, classifica e propõe o que fazer primeiro. O humano decide as prioridades. Você prepara a decisão e a executa.

Pegue o escopo do argumento: `bugs`, `debt` ou `all`. Sem argumento, use `all`.

## 1. Reunir

Descubra onde o projeto registra o trabalho: um rastreador de issues (`gh issue list`), arquivos de backlog ou de issues no repositório, ou os dois. Se não encontrar nenhum, pergunte ao humano onde o trabalho é registrado.

Monte o inventário do escopo:

- **Bugs:** relatos de bug abertos, testes que falham ou são instáveis (flaky), travamentos nos logs que o humano indicar.
- **Dívida:** comentários `TODO`, `FIXME` e `HACK`; avisos do linter e do verificador de tipos; APIs descontinuadas e dependências desatualizadas (use a ferramenta de auditoria do projeto); código duplicado; módulos sem testes.

Para a dívida, encontre os **hotspots**: arquivos que mudam com frequência e são complexos. Ordene os arquivos pelo número de commits no último ano (`git log --format= --name-only
--since=1.year | sort | uniq -c | sort -rn`) e leia o topo dessa lista. A dívida cobra **juros** só onde o código muda. Dívida em um arquivo que ninguém toca pode esperar.

A etapa termina quando cada item do rastreador e cada achado acima estiver no inventário, cada um com uma descrição de uma linha e a sua fonte.

## 2. Classifique

Para cada item, registre:

- **Tipo (Kind):** `bug`, `debt`, `feature`, `question`, `duplicate` (de qual item) ou `invalid`.
- **Impacto (Impact):** nos bugs, o que quebra e quantos usuários são afetados. Perda de dados, segurança e resultados errados vêm antes de travamentos. Travamentos vêm antes de problemas cosméticos. Na dívida, os juros: com que frequência o código muda e o que a dívida deixa lento ou arriscado.
- **Esforço (Effort):** `S` (horas), `M` (um ou dois dias) ou `L` (mais; proponha uma divisão).
- **Confiança (Confidence):** `reproduced`, `plausible` ou `needs info`, com o que falta.

Para um bug cuja causa não está clara, acione o agente `investigator` em vez de chutar. Para um relato de bug sem reprodução, rascunhe a pergunta para quem relatou.

## 3. Proponha

Ordene os itens pelo impacto em relação ao esforço. Bugs de segurança e de perda de dados vêm primeiro, independentemente do esforço. Apresente ao humano:

1. A lista ordenada: tipo, impacto, esforço, confiança e uma linha sobre por que o item está nessa posição.
2. Duplicados e itens inválidos que você propõe fechar, cada um com o motivo.
3. Itens que precisam de informação, com a pergunta de cada um.
4. Ganhos rápidos: impacto alto, esforço `S`.

Pare aqui e espere as decisões do humano. Reordene conforme ele indicar.

## 4. Aplique

Depois que o humano aprovar, execute só o que ele aprovou:

- Atualize o rastreador: rótulos, prioridades, comentários e fechamento de duplicados. Mostre os comentários exatos antes de publicá-los.
- Crie issues para os itens de dívida aprovados, cada um com as evidências e os dados de hotspot que o sustentam.
- Informe os próximos passos dos itens do topo: bugs vão para o `investigator`, depois para o `tester` e o `implementer`. Dívida passa pela skill `safe-refactor`.
