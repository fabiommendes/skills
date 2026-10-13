---
name: mdq-questions
description: Escreve questões e provas em MDQ, um formato markdown para quizzes e provas (arquivos .mdq.md). Use ao criar, revisar ou converter questões (múltipla escolha, múltipla seleção, verdadeiro/falso, resposta curta, numérica, lacunas, dissertativa, ordenação) ou ao montar questões em uma prova.
---

# Escrevendo questões MDQ

O MDQ escreve uma questão como um arquivo markdown. O tipo da questão é
inferido pelo corpo, então, na maioria dos casos, você escreve markdown comum e
nada mais.

Os arquivos usam a extensão `.mdq.md` (ou `.mdq`). Um arquivo guarda uma
questão, ou uma prova com várias. Valide com `mdq validate <arquivo>` quando a
implementação de referência estiver disponível.

Especificação: https://github.com/fabiommendes/mdq.spec (`docs/question-types/`,
`docs/exam.md`, além de pares de markdown e YAML esperado em `examples/`).

## Anatomia

```md
---
# Optional comment string (stored, unlike a YAML comment after a blank line).
id: capital-br
title: Capital of Brazil
tags: geography, brazil
---

Optional preamble paragraphs.

What is the capital of Brazil?

* [ ] Lisbon
* [*] Brasília

Optional epilogue paragraphs.
```

O último parágrafo antes do corpo é o **enunciado** (obrigatório), e a lista é
o **corpo** (obrigatório, e é ele que define o tipo da questão). Todo o resto é
opcional.

* Campos do frontmatter: `type`, `title`, `id`, `uuid`, `tags`, `author`,
  `locale`, `meta`, além dos específicos de cada tipo. O frontmatter sempre
  prevalece sobre o que está escrito no corpo.
* Escreva o enunciado como `...` para obter a instrução padrão do tipo.
* `[slug]` no início do primeiro parágrafo define o id: `[Q1] O que é ...`.
* Nunca use títulos H1 dentro de uma questão. Não comece um parágrafo ou um
  item de lista com `[`, a não ser que seja uma tag real.

## Escolha o tipo

| Você quer                            | Corpo                               | Referência |
| ------------------------------------ | ----------------------------------- | ---------- |
| Uma resposta certa entre várias      | Lista `* [ ]` / `* [*]`             | [multiple-choice](references/multiple-choice.md) |
| Marcar todas as que se aplicam       | Lista `* [ ]` / `* [x]`             | [multiple-selection](references/multiple-selection.md) |
| Julgar cada afirmação como V ou F    | Lista `* [T]` / `* [F]`             | [true-false](references/true-false.md) |
| Uma palavra ou frase curta digitada  | `[short-answer]: ...`               | [short-answer](references/short-answer.md) |
| Um número, com tolerância            | `[numeric(unit)]: ...`              | [numeric](references/numeric.md) |
| Lacunas dentro de uma frase          | Marcadores `[^slug]` + definições   | [fill-in](references/fill-in.md) |
| Texto livre, corrigido à mão         | `[essay]`                           | [essay](references/essay.md) |
| Colocar linhas na ordem certa        | `[ordering]` + bloco de código ou lista | [ordering](references/ordering.md) |
| Várias questões em um arquivo        | `# Título` + separadores `===`      | [exam](references/exam.md) |

Defina `type:` no frontmatter só para desambiguar. Caso contrário, deixe o tipo
ser inferido.

## Feedback e comentários

Em qualquer lugar em que uma alternativa ou um padrão for listado, use linhas
com `>` para o feedback do aluno e linhas com `!` para comentários visíveis só
ao professor:

```md
* [ ] Rio de Janeiro
  > It was the capital until 1960.
  ! Most common wrong answer.
```

## Correção

Os tipos baseados em escolha (múltipla escolha, múltipla seleção, verdadeiro/falso,
lacunas) aceitam `grading` no frontmatter:

* `symmetric` (padrão): respostas erradas subtraem, então chutar tem média zero.
* `partial`: crédito por item certo, nunca negativo.
* `all-or-nothing`: tudo certo ou zero.

Resposta curta e numérica são sempre binárias (1 ou 0). Dissertativa é sempre
manual.

## Checklist

* Enunciado presente e não vazio; corpo presente.
* Textos das alternativas únicos; defina `[choice-id]`s explícitos quando os
  ids importarem.
* Pelo menos uma resposta certa, e não todas as alternativas certas.
* Respostas numéricas que não são inteiras têm tolerância.
* Prefira um `id` e um `title` explícitos.
