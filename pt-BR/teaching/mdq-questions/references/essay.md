# Dissertativa

Resposta em texto livre, corrigida manualmente. O corpo é apenas a tag `[essay]`.

```md
Describe how the greenhouse effect works and how it affects the climate.

[essay]
```

## Frontmatter

| Campo     | Valores                                                 |
| --------- | ------------------------------------------------------- |
| input     | `text` (texto formatado), `plain` (sem formatação), `code` |
| highlight | Linguagem para `input: code`, por exemplo `python`      |

## Gabarito

Opcional. Fica depois da tag `[essay]` e de qualquer epílogo. Orienta o
professor e pode ser mostrado aos alunos.

```md
Write a function that computes the n-th Fibonacci number.

[essay]

## [answer-key]
A straightforward iterative solution keeps the two previous values and loops n
times, running in O(n) time and O(1) space.
```

Use `highlight` somente junto com `input: code`.
