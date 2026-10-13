# Provas

Uma prova é um arquivo com várias questões. Ela começa com um título H1
(opcionalmente com um slug) e separa as questões com `===`.

````md
---
course: CS101
locale: pt-BR
---

# [midterm] Midterm Exam

One or more paragraphs of instructions.

---
include: recursion-01
---

---
id: q2
---
Convert this iterative algorithm into a recursive one.

```python
def factorial(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
```

[essay]

===

Judge the statements.

* [V] Any iterative algorithm can be implemented recursively.
* [F] Recursion tends to be more memory efficient than iteration.
````

* O separador `===` precisa de uma linha em branco antes. Ele é opcional quando
  a questão começa com o próprio frontmatter.
* `include: <id>` puxa uma questão definida em outro lugar e ocupa uma posição
  como qualquer outro bloco.
* Questões sem `id` recebem `q1`, `q2`, ... pela posição.
* O corpo da prova não pode usar títulos H1 (o título é o único).

## Frontmatter

Além de `title`, `id`, `uuid`, `tags` e `meta`, que são comuns:

| Campo   | Descrição                                                  |
| ------- | ---------------------------------------------------------- |
| course  | Código da disciplina                                       |
| author  | Herdado pelas questões                                     |
| locale  | Herdado pelas questões, por exemplo `pt-BR`                |
| grading | Estratégia de correção padrão das questões; pode ser também um mapa de tipo de questão para estratégia |
| penalty | `none` (padrão), `capped` ou `full`                        |

Só `author` e `locale` são herdados pelas questões. Uma questão que declara um
dos dois mantém o próprio valor. `grading` é um padrão que a questão pode
sobrescrever.

```yaml
grading:
  multiple-choice: all-or-nothing
  true-false: partial
```

`penalty` decide o que acontece com uma nota negativa em uma questão: `none`
limita cada questão em 0, `capped` mantém os negativos, mas limita o total da
prova em 0, e `full` não limita nada.
