# Numérica

Uma única resposta numérica, com unidade opcional e tolerância opcional.

```md
How many grams of water are in a liter?

[numeric(g)]: 1000
```

## Formas do corpo

```md
[numeric]: 42                  # integer
[numeric]: 3.14                # exact decimal - rarely what you want
[numeric]: 3.14 +- 0.1         # absolute tolerance
[numeric]: 3.14 +- 5%          # relative tolerance (5% of the answer)
[numeric]: 3.14 +- 5% +- 0.1   # both: the response passes if it clears EITHER
[numeric]: -1/3                # fraction
[numeric(kg)]: 5.5 +- 0.1      # with a unit
```

A unidade é formada por letras, dígitos, `.`, `-` e `_`. Ela é escrita dentro da
tag, nunca depois do valor.

## Frontmatter

| Campo         | Descrição                                                 |
| ------------- | --------------------------------------------------------- |
| unit          | Igual ao `(unit)` da tag                                  |
| domain        | `integer`, `decimal` ou `fraction`; normalmente inferido  |
| decimalPlaces | Casas decimais para mostrar/aceitar; só vale para `decimal` |

O domínio é inferido pela forma como o valor e a tolerância absoluta são escritos
(vale o mais amplo dos dois: integer < fraction < decimal). A tolerância
percentual não muda o domínio.

## Correção

Binária: dentro da tolerância vale 1, qualquer outra coisa vale 0. Não existe
campo `grading` nem crédito parcial. Para ser mais tolerante, aumente a
tolerância.

## Armadilhas

* Sempre dê uma tolerância para respostas decimais ou fracionárias. Sem ela, a
  quantidade de casas que o aluno digita decide a nota.
* Uma tolerância relativa sobre uma resposta `0` aceita apenas um `0` exato.
* `5%` significa cinco por cento. Um `relative: 5` na forma interpretada seria
  500%.
