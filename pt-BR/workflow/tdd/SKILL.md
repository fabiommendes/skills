---
name: tdd
description: Desenvolvimento orientado a testes (TDD) com um implementer sem acesso ao código de teste. Use quando o usuário pedir TDD ou quiser construir uma funcionalidade ou corrigir um bug escrevendo os testes primeiro.
argument-hint: "[lite|default|full]"
---

# Desenvolvimento orientado a testes (TDD)

Um ciclo vermelho → verde, rodado com três quantidades diferentes de agentes. O modo muda quem escreve os testes, não o que é um bom teste nem a ordem das coisas.

Você é o **orquestrador**, a não ser que digam o contrário.

## Modos

| Modo | Agentes | Use quando |
|---|---|---| 
| `lite` | você sozinho | Mudança pequena, uma ou duas seams, nenhum paralelismo a ganhar. |
| `default` | você + implementer | A maior parte do trabalho. Você escreve os testes; o implementer nunca lê o código de teste. |
| `full` | você + tester + implementer | Superfície grande, ou a escrita dos testes é trabalhosa o bastante para merecer um agente próprio. |

Pegue o modo do argumento. Sem argumento, ou se o argumento for um comando, use `default`.

Leia só o arquivo do seu modo:

- `lite`: [references/mode-lite.md](references/mode-lite.md)
- `default`: [references/mode-default.md](references/mode-default.md)
- `full`: [references/mode-full.md](references/mode-full.md)

## Invariantes

Estas regras valem em todos os modos.

- **Vermelho antes de verde.** O teste de um comportamento existe e falha pelo motivo certo antes de o comportamento ser implementado.
- **Um ciclo, uma fatia.** Um ciclo entrega uma fatia vertical, trabalhada em lotes de no máximo 3 critérios de aceitação. Se precisar de mais de cerca de 3 lotes, isso deveria ter sido dois ciclos: divida. Nunca escreva todos os testes de uma funcionalidade antes de qualquer parte da implementação. Testes em massa verificam um comportamento imaginado e fixam uma estrutura de testes antes de você entender a implementação. Lotes pequenos deixam os testes de cada lote responderem ao que o lote anterior ensinou.
- **Testes nunca são escritos a partir da implementação.** No modo `lite`, a ordem garante isso. No `default` e no `full`, o implementer também nunca lê o código de teste para decidir o que construir.
- **Lotes são validados de forma independente.** Enquanto um lote é implementado, os testes do próximo lote podem já existir e falhar. Controle a qual lote cada teste pertence e valide um lote só pelos próprios testes.

## Projeto

Antes de qualquer teste, projete a superfície pública e nada abaixo dela: assinaturas de funções, tipos, definições de classes, estrutura de módulos. Sem detalhes de implementação.

Escreva stubs para tudo que ainda não existe. Os stubs são o contrato em que os outros dois papéis trabalham. Eles também permitem começar um lote antes de o anterior ser integrado.

Projete para testabilidade. Tire os efeitos colaterais para fora com injeção de dependências ou funções de ordem superior. Mantenha as camadas externas (handlers HTTP, pontos de entrada da CLI, código voltado ao navegador) finas, sobre uma abstração interna que contém a lógica. Assim existe uma seam barata para testar.

Antes de escrever testes, carregue a skill `good-code` e leia o `testing.md` dela. Ele trata de onde os testes se conectam e de como devem ser. Esta skill trata só do fluxo de trabalho.

Informe ao humano, em tópicos e antes de começar, as seams que você pretende testar e os critérios de aceitação. Não espere aprovação. Pare e pergunte só quando um lote posterior precisar de uma seam fora desse conjunto, o que significa que o projeto mudou.

## O ciclo

1. Projete a superfície, escreva os stubs e informe as seams e os critérios de aceitação.
2. Pegue o próximo lote: até 3 critérios de aceitação.
3. Escreva os testes do lote, por você ou pelo tester, conforme o modo.
4. Rode os testes. Confirme que falham, e que falham pelo motivo esperado. Um teste que passa contra um stub não testa nada.
5. Escreva a implementação do lote a partir dos critérios e dos stubs, nunca a partir do código de teste.
6. Rode os testes do lote. Verde → próximo lote. Não verde → diagnostique. Se o teste estiver errado, e não o código, corrija o teste e diga isso.
7. Depois do último lote, rode a suíte inteira e confira a fatia contra os critérios de aceitação.

Quando a estratégia não funcionar, mude-a e diga isso. Um lote que expõe uma premissa errada sobre a API mostra o ciclo fazendo o seu papel: revise os stubs, avise quem vem depois e continue.

## Refatoração

Refatorações pequenas dentro do código que você já está mexendo estão no escopo. Refatorar não é o objetivo de um ciclo, a não ser que o humano diga que é.

Tudo que é visível de fora (renomear uma função pública, mudar uma assinatura, mover um módulo) deve ser levado ao humano antes, mesmo quando for claramente uma melhoria.

## Criação de agentes

Use os agentes `tester` e `implementer` do projeto quando eles existirem. Assim o projeto substitui os padrões, e as definições deles já trazem o contrato do papel.

Quando o projeto não define nenhum dos dois, crie um agente geral com o briefing correspondente de [references/agent-briefs.md](references/agent-briefs.md) e peça um modelo da classe Sonnet.

Mantenha os agentes criados vivos entre os lotes. Eles acumulam o contexto que barateia os lotes seguintes.

Quando um agente disser que um teste parece errado, faça as visões convergirem. Se elas não convergirem, a palavra final é sua.

## Informes

Você e o humano são pares. Seja direto e conciso, e pule a cerimônia.

Informe cada lote em uma ou duas linhas: o que ele cobre e se ficou verde. Informe também uma mudança de projeto, uma seam nova ou uma discordância entre agentes. Não anuncie que preencheu um stub, porque a existência do stub já indica isso. E não informe o andamento de rotina.
