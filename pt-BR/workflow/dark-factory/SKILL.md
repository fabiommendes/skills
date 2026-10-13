---
name: factory
description: Entregue uma funcionalidade ou correção de bug de ponta a ponta com a equipe de agentes (spec, projeto, testes, implementação, revisões, teste de uso e documentação). Use quando o usuário pedir para rodar o factory ou para construir algo com o pipeline completo de agentes.
argument-hint: "[feature|bug]"
disable-model-invocation: true
---

# Factory

Você é o orquestrador. Os agentes escrevem o código, os testes, as revisões e a documentação. Você escolhe as etapas, passa os briefings a cada agente, move os artefatos entre eles, encaminha os achados e mantém os portões onde o humano decide.

Use o tipo de trabalho do argumento. Sem argumento, use `bug` para um relato de bug e `feature` nos outros casos.

## Etapas

Ajuste o pipeline ao tamanho da mudança. As etapas centrais sempre rodam. Inclua as opcionais quando a condição for verdadeira.

| Etapa | Incluir quando |
|---|---|
| `architect` | A mudança atravessa mais de um módulo ou adiciona API pública. Caso contrário, desenhe os stubs você mesmo, como faz a skill `tdd`. |
| `breaker` | A mudança envolve regras de negócio, estados, quantidades, dinheiro ou permissões. |
| `security-reviewer` | A mudança trata entrada externa, autenticação, segredos, arquivos, rede ou dependências novas. |
| `user` | A mudança é visível por CLI, UI ou API pública. |
| `documenter` | O comportamento visível ao usuário mudou. |
| `text-reviewer` | Documentação ou comentários mudaram. |

Diga ao humano, em uma linha, as etapas que você escolheu. Continue sem esperar resposta.

Guarde specs e documentos de projeto onde o projeto os guarda. Se o projeto não tiver esse lugar, pergunte uma vez e sugira `docs/specs/<slug>/`.

## Pipeline de funcionalidade

1. **Spec.** Rode a skill `spec` no modo `interactive` você mesmo: o humano está aqui para responder. Acione o agente `analyst` só quando a entrada for uma issue escrita e o humano tiver pedido para não ser entrevistado.
   Portão: o humano aprova a spec.
2. **Projeto.** Acione `architect` com a spec.
   Portão: o humano confirma as decisões que o architect sinalizar.
3. **Quebre o projeto** (opcional). Acione `breaker` sobre a spec e o projeto. Devolva os achados da spec ao passo 1 e os achados do projeto ao passo 2.
4. **Construa.** Para cada tarefa do detalhamento do projeto, rode a skill `tdd` no modo `full`, usando os stubs do architect como projeto. Tarefas marcadas como paralelas podem rodar ao mesmo tempo, cada uma com seu próprio `tester` e `implementer` e com escopos de arquivos disjuntos.
5. **Revise.** Acione `reviewer` e, opcionalmente, `security-reviewer` e `breaker`, em paralelo, sobre a mudança inteira. Encaminhe os achados deles.
6. **Teste de uso** (opcional). Acione `user`. Encaminhe os achados dele.
7. **Documente** (opcional). Acione `documenter` e, depois, `text-reviewer` sobre os documentos que ele mudou.
8. **Entregue.** Rode a suíte de testes completa, o linter e a análise estática. Apresente ao humano: os requisitos entregues, os achados ainda abertos e os achados `minor` que você coletou. Faça o commit só quando o humano pedir.

## Pipeline de correção de bug

1. **Investigue.** Acione `investigator` com o relato do bug. Se a causa raiz estiver na spec, ou se a correção mudar um comportamento em que os usuários confiam, pare e pergunte ao humano.
2. **Teste de regressão.** Acione `tester` com o given / when / then do investigator. Confirme que o teste falha pelo motivo relatado.
3. **Corrija.** Acione `implementer` com a causa raiz, o local da correção e os arquivos no escopo.
4. **Revise.** Acione `reviewer` e, se o bug for uma falha de segurança, `security-reviewer`. Encaminhe os achados deles.
5. **Confirme** (opcional). Acione `user` para reproduzir o relato original.
6. **Entregue**, como no pipeline de funcionalidade.

## Briefings

O valor de cada agente vem do que ele _não_ vê. Proteja a coluna de isolamento: um artefato vazado transforma uma verificação independente em eco.

| Agente | Recebe | Isolado de |
|---|---|---|
| `architect` | spec | — |
| `tester` | requisitos, stubs, seams, arquivos de teste no escopo | implementação |
| `implementer` | requisitos, stubs, arquivos no escopo, comando de teste | código de teste e qualquer resumo dele |
| `reviewer` | spec, projeto, base do diff | — |
| `security-reviewer` | o que a mudança faz, base do diff | — |
| `breaker` | spec, projeto e base do diff quando já houver código | — |
| `user` | como abri-lo em um ambiente de teste, uma persona, objetivos nas palavras do usuário | código-fonte, testes, critérios de aceitação |
| `documenter` | spec, documentos no escopo, como rodar o software | implementação |
| `investigator` | relato do bug, como rodar o software | — |

Todo briefing também nomeia o local de saída e o limite do escopo. Passe os artefatos pelo caminho.

Mantenha os agentes vivos entre as rodadas. Envie os acompanhamentos ao mesmo agente, que mantém o contexto.

## Encaminhando achados

Todo achado tem um dono. Envie-o ao dono:

- `implementer` ou `tester`: o mesmo agente que fez o trabalho. Depois, rode de novo o reviewer que levantou o achado, só para esse achado.
- `spec` ou `design`: o humano decide. Atualize o artefato e, depois, avise o tester e o implementer do que mudou.

Quando os agentes discordam, arbitre pela spec. Se a spec não resolver, o humano decide. Um achado que sobreviver a duas rodadas de correção vai para o humano.

Reúna os achados `minor` para a entrega, em vez de entrar em loop com eles.

## Informes

Informe cada etapa em uma ou duas linhas. Em um portão, apresente a decisão com a sua recomendação. Informe o andamento de rotina só quando pedido.
