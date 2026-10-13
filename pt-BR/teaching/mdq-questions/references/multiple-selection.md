# Múltipla seleção

"Marque todas as que se aplicam". A sintaxe da lista é a mesma da múltipla
escolha, mas o marcador é `[x]` para a alternativa que deve ser marcada e `[ ]`
para a que não deve.

```md
Which cities were capitals of Brazil?

* [ ] Lisbon
* [x] Brasília
* [ ] São Paulo
* [x] Rio de Janeiro
```

As alternativas usam o mesmo `[choice-id]`, o mesmo feedback com `>` e o mesmo
comentário com `!` da [múltipla escolha](multiple-choice.md#anatomia-da-alternativa).
Porcentagens NÃO são permitidas: uma alternativa é marcada ou não é.

## Frontmatter

| Campo   | Valores                                            |
| ------- | -------------------------------------------------- |
| shuffle | `true` para permitir embaralhar as alternativas    |
| grading | `symmetric` (padrão), `partial`, `all-or-nothing`  |

## Correção

Uma caixa não marcada afirma "falso", então toda alternativa é sempre julgada.
Com 4 alternativas e gabarito `[x, , x, ]`:

* `partial`: julgamentos corretos / 4, entre 0 e 1.
* `all-or-nothing`: 1 somente se todas as caixas baterem com o gabarito; senão, 0.
* `symmetric`: (corretos - errados) / 4, entre -1 e 1.

O feedback aparece somente para as alternativas julgadas **erradas**, incluindo
uma alternativa correta que o aluno deixou de marcar. Uma resposta perfeita não
mostra feedback.

## Armadilhas

* O aluno não tem a opção de "deixar em branco". Se for preciso permitir
  abstenção, use uma questão de [verdadeiro/falso](true-false.md).
