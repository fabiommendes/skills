---
name: spec
description: Escreva uma spec com requisitos numerados e critérios de aceitação. Use quando o usuário quiser especificar uma funcionalidade, escrever uma spec ou PRD, ou transformar um pedido ou uma issue em requisitos.
argument-hint: "[interactive|headless]"
disable-model-invocation: true
---

# Spec

Uma spec diz o que o software faz, visto de fora: por um usuário, um chamador ou outro sistema. Ela é a fonte da verdade para todos os que vêm depois. O agente architect projeta a partir dela, o tester escreve testes a partir dela, o implementer constrói contra ela e o reviewer julga por ela. Nenhum deles pode perguntar ao solicitante o que ele quis dizer, então a spec precisa responder.

A spec cobre _o quê_. O _como_ (módulos, APIs internas, estruturas de dados) pertence ao projeto.

## Modos

- `interactive` (padrão): você conversa com o humano que quer a mudança.
- `headless`: nenhum humano está disponível, como quando você roda como agente `analyst`. Suas perguntas vão para o orquestrador.

Pegue o modo do argumento. Sem argumento, use `interactive`.

## 1. Entender

1. Leia o `CLAUDE.md` ou o `AGENTS.md` do projeto. Siga-os antes dos seus próprios padrões.
2. Leia o pedido. Separe o que está afirmado do que você está inferindo.
3. Leia a documentação, o glossário e as specs existentes do projeto, se houver. Reutilize os termos deles. Um conceito recebe um só nome.
4. Explore o código só para entender o comportamento atual que a mudança toca: os comandos, telas, endpoints ou funções que o usuário já vê. Pare quando conseguir descrever esse comportamento.

## 2. Resolva as ambiguidades

Liste cada ambiguidade que levaria a um comportamento materialmente diferente. Para cada uma, escreva as opções que você vê e a que você recomenda.

- **interactive:** pergunte ao humano, poucas perguntas por vez, começando pela mais consequente. Ofereça as opções e a sua recomendação. Use uma pergunta de múltipla escolha quando as opções forem discretas. Acompanhe quando uma resposta abrir um novo ramo. Termine quando nenhuma pergunta aberta mudar um requisito, ou quando o humano mandar seguir.
- **headless:** envie a lista inteira ao orquestrador em um só lote, antes de escrever. Se mandarem seguir sem respostas, use as opções que você recomendou.

Registre toda escolha feita sem a resposta do solicitante na seção "Assumptions".

## 3. Escreva

- Numere cada requisito: `R1`, `R2`, ... Os agentes seguintes citam esses IDs.
- Um requisito descreve um comportamento observável. Divida qualquer requisito que una dois comportamentos com "e".
- Cada requisito tem critérios de aceitação escritos como exemplos verificáveis: dado um estado e uma entrada, a saída, o erro ou o efeito colateral esperado. Use valores concretos.
- Cubra os casos de falha: entrada inválida, recursos ausentes, permissões, conflitos. Informe o erro exato que o usuário vê, quando isso importar.
- Cubra os limites: vazio, um, muitos, o máximo e operações repetidas.
- Nomeie a interface visível ao usuário quando ela fizer parte do pedido: nomes de comando, flags, URLs, campos, mensagens. Deixe os nomes internos para o projeto.
- Escreva "Out of scope" para comportamentos que um leitor razoavelmente esperaria, mas que esta mudança não entrega.
- Escreva a menor spec que entrega o pedido. Registre as ideias além dele em "Possible follow-ups", não como requisitos.

Use o modelo de spec do projeto, se existir. Caso contrário, use esta estrutura:

```markdown
# <Feature name>

## Context
Why this change exists, in two or three sentences.

## Glossary
New or overloaded terms, one line each.

## Requirements
### R1: <short title>
<The behavior, in one or two sentences.>

Acceptance criteria:
- Given <state>, when <action>, then <result>.

## Out of scope
## Assumptions
## Open questions
## Possible follow-ups
```

Escreva a spec onde o projeto guarda as specs, ou no arquivo que o orquestrador indicar. Se não houver nenhum dos dois, pergunte.

## 4. Revise

Leia a spec como o tester leria: cada requisito precisa ser testável sem adivinhar. Leia como o implementer leria: cada requisito precisa ser construível sem perguntar. Corrija o que falhar em qualquer uma das leituras.

- **interactive:** mostre ao humano os títulos dos requisitos, a lista de "Out of scope" e os itens de "Assumptions". Revise até ele aprovar.
- **headless:** termine com um relatório curto: o caminho da spec, o número de requisitos, os itens de "Assumptions" e as "Open questions" com os requisitos que elas bloqueiam.
