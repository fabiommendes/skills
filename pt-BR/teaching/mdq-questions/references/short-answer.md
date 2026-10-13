# Resposta curta

Uma resposta digitada curta, comparada com um ou mais padrões.

```md
What is the capital of Brazil?

[short-answer]: Brasília
```

Por padrão, a comparação é **inexata**: maiúsculas, acentos e espaços no início,
no fim ou repetidos são ignorados, então `brasilia` é aceita.

## Formas de padrão

Valem tanto no corpo quanto no frontmatter:

| Escrito como       | Comparado como                                    |
| ------------------ | ------------------------------------------------- |
| `Brasília`         | string simples, inexata (a escolha usual)         |
| `` `math.isnan` `` | literal exato: maiúsculas e pontuação importam    |
| `/[Bb]ras[íi]lia/i` | regex, ancorada nas duas pontas                  |
| `*`                | curinga, aceita qualquer coisa (último item de rejeição) |

Exija uma resposta exata para perguntas sobre código, grafia ou ortografia:

```md
Which **Python** function checks if a number is NaN?

[short-answer]: `math.isnan`
```

## Listas de aceitação e rejeição

Para mais controle, liste padrões com feedback. A ordem importa: o primeiro
padrão que casar fornece o feedback.

```md
What is the capital of Brazil?

[short-answer/accept]:
* /[Bb]ras[íi]lia/i
  > Good call!

[short-answer/reject]:
* Buenos Aires
  > That's the capital of Argentina!
* Rio de Janeiro
  > It used to be, but not since 1960.
* *
  > Sorry, that is not the correct answer.
```

No máximo um bloco `[short-answer]`, um `accept` e um `reject` por questão. Um
`[short-answer]` sem sufixo é apenas uma lista de aceitação com um item. Uma
correspondência na lista de aceitação sempre vence uma correspondência na lista
de rejeição.

## Regex

Sintaxe parecida com JavaScript, ancorada nas duas pontas (então `/abc/` não casa
com `xabc`), **sensível a maiúsculas por padrão**. Flags:

* `i`: ignora maiúsculas.
* `n`: ignora acentos.
* `f`: casa em qualquer parte da resposta (substring).
* `b`: casa um prefixo.

Não suportado: lookbehind, grupos nomeados, `\p{...}` e interseção de classes.
`m g s u v y d` são aceitas, mas ignoradas.

## Frontmatter

| Campo      | Descrição                                                    |
| ---------- | ------------------------------------------------------------ |
| accept     | Mesma lista do bloco `[short-answer/accept]` (use um ou outro, nunca os dois) |
| reject     | Mesma lista do bloco `[short-answer/reject]`                 |
| preAccept  | A resposta precisa casar com um destes padrões para ser enviável; é validação, não correção |
| preReject  | A resposta não pode casar com nenhum destes padrões para ser enviável |
| diacritics | `fold` (padrão) ou `keep` para exigir os acentos             |

Os itens da lista são strings de padrão ou objetos `{ pattern: ..., feedback: ... }`.

## Correção

Sempre binária: 1 ou 0. Uma resposta sem correspondência vai para o professor,
a não ser que a lista de rejeição termine com `*` (ou que não exista bloco de
rejeição). Um `[short-answer]:` vazio, sem padrões, significa correção totalmente
manual.
