# Ordenação

Coloque linhas na ordem certa. O bloco `[ordering]` é **sempre escrito na ordem
correta**: ele é o gabarito, e as implementações o embaralham antes de mostrar ao
aluno.

````md
Sort the lines below into a program that prints the first 10 Fibonacci numbers.

[ordering]
```python
x, y = 1, 1
for _ in range(10):
    print(x)
    aux = x + y
    x = y
    y = aux
```
````

O bloco depois da tag é um bloco de código cercado (o que implica `content: code`,
e a linguagem da cerca vira `highlight`) ou uma lista não ordenada (o que implica
`content: text`).

## Seções extras

Todas são opcionais e usam o mesmo tipo de bloco do bloco principal.

````md
## [extra]                  # distractor lines, mixed in, must NOT be used
```python
y = x + y
```

## [accept]                 # an alternative correct order; may repeat
! Instructor comment: the print and aux lines can be swapped.
```python
x, y = 1, 1
for _ in range(10):
    aux = x + y
    print(x)
    x = y
    y = aux
```

## [reject]                 # a known wrong order, worth explaining; may repeat
> Without the auxiliary variable this produces powers of two.
```python
x, y = 1, 1
for _ in range(10):
    print(x)
    x = y
    y = x + y
```
````

As linhas `>` são feedback para o aluno, e as linhas `!` são comentários do
professor; elas não podem se intercalar. A mesma linha nunca pode aparecer como
aceita e como rejeitada.

## Frontmatter

| Campo          | Valores                                                   |
| -------------- | --------------------------------------------------------- |
| content        | `code` ou `text`; inferido pelo corpo                     |
| highlight      | Linguagem, para `content: code`; inferida pela cerca      |
| indentation    | `fixed` (padrão), `lenient`, `strict`                     |
| unmatched      | `manual` (padrão) ou `incorrect`                          |
| normalizations | `dedent`, `skip-blanks`                                   |

* `fixed` mantém a indentação escrita, e o aluno não pode alterá-la.
* `lenient` deixa o aluno indentar livremente, mas ignora a indentação na correção.
* `strict` deixa o aluno indentar e corrige a indentação. Use para código em que
  a indentação tem significado.

## Correção

Uma resposta igual ao gabarito ou a um bloco `## [accept]` está correta. Uma
resposta igual a um bloco `## [reject]` está errada. Qualquer outra resposta vai
para o professor, a não ser que `unmatched: incorrect` lhe dê nota 0.
