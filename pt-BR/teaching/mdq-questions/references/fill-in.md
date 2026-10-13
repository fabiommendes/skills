# Lacunas

Uma frase com lacunas. Cada `[^slug]` no enunciado é uma lacuna, e cada lacuna
recebe uma definição abaixo.

```md
The capital of Brazil is [^capital]. It has roughly [^size] inhabitants.

[^capital]:
* [ ] Lisbon
* [*] Brasília
* [ ] São Paulo
* [ ] Rio de Janeiro

[^size/numeric]: 2750000 +- 10%
```

Toda lacuna do enunciado precisa de definição, e toda definição precisa ser
referenciada no enunciado. As definições podem vir em qualquer ordem.

## Tipos de lacuna

O sufixo da tag define o tipo. Um `[^slug]:` sem sufixo é uma lacuna de escolha.

```md
[^city]:                              # choice blank: list starts on the NEXT line
* [ ] Salvador
* [*] Brasília
  > Since 1960.

[^length/numeric(km)]: 6400 +- 5%     # numeric blank, same syntax as [numeric]

[^planet/short-answer]: Jupiter       # short answer blank

[^planet/short-answer/accept]:        # or with accept/reject lists
* Jupiter
* `Jove`
  > Archaic, but accepted.

[^planet/short-answer/reject]:
* Saturn
  > Second largest, but not the largest.
* *
  > Not a planet of the Solar System.
```

As lacunas de escolha aceitam a sintaxe completa de item de
[múltipla escolha](multiple-choice.md#anatomia-da-alternativa), incluindo
feedback. As lacunas numéricas e de resposta curta não têm sintaxe de feedback.

## Onde as lacunas podem aparecer

Somente em um trecho de texto simples de um parágrafo comum. Não podem aparecer
em títulos, itens de lista, células de tabela, citações em bloco, blocos de
código, nem dentro de marcação inline. Por isso, `**start [^blank] end**` é
inválido. Coloque a ênfase em volta do texto, não em volta da lacuna.

## Frontmatter

| Campo   | Valores                                                |
| ------- | ------------------------------------------------------ |
| shuffle | `true` para permitir embaralhar as alternativas internas |
| grading | `symmetric` (padrão), `partial`, `all-or-nothing`      |

## Correção

Cada lacuna é corrigida pelas regras do próprio tipo e gera uma nota entre -1 e
1 (só as lacunas de escolha podem ficar negativas). Uma lacuna vazia vale 0.
Depois:

* `partial`: média das notas das lacunas, com os negativos tratados como 0.
* `all-or-nothing`: 1 somente se todas as lacunas estiverem totalmente corretas.
* `symmetric`: média simples, com os negativos incluídos.
