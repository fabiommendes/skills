# Verdadeiro / falso

## Sintaxe

Uma lista de afirmações, cada uma julgada individualmente. Marque uma afirmação
verdadeira com `[T]` e uma falsa com `[F]`.

```md
Judge the statements.

* [F] Earth is flat.
* [T] Humans and apes share a common ancestor.
  > Darwinian evolution describes common descent, not descent from modern apes.
* [T] The Earth is billions of years old.
* [F] Light travels instantly through space.
```

As afirmações usam a mesma sintaxe de `[choice-id]`, feedback com `>` e
comentário com `!` da [múltipla escolha](multiple-choice.md#anatomia-da-alternativa).

### Marcadores

Qualquer letra única funciona, sem diferenciar maiúsculas, exceto `x` (reservada
para a [múltipla seleção](multiple-selection.md)). Use o par que combina com o
idioma do documento:

* Sempre verdadeiro: `T`, `V`, `S`.
* Sempre falso: `F`.
* Qualquer outra letra significa verdadeiro, mas gera um aviso: evite.

Para `locale: pt-BR`, escreva `V`/`F`; para inglês, `T`/`F`. A letra em si é
mantida no documento interpretado, então `V` e `T` continuam distinguíveis.

### Frontmatter

| Campo   | Valores                                            |
| ------- | -------------------------------------------------- |
| shuffle | `true` para permitir embaralhar as afirmações      |
| grading | `symmetric` (padrão), `partial`, `all-or-nothing`  |

### Correção

Diferente da múltipla seleção, uma afirmação pode ficar **sem marcação**, e a
ausência de marcação nunca prejudica:

* `partial`: marcações corretas / total.
* `all-or-nothing`: qualquer marcação errada dá 0; senão, marcações corretas /
  total.
* `symmetric`: (corretas - erradas) / total; sem marcação não pontua nem para um
  lado nem para o outro.

O feedback aparece para toda afirmação julgada errada **e** para toda afirmação
deixada sem julgamento.

### Armadilhas

* Não faça todas as afirmações verdadeiras, nem todas falsas.
* Os textos das afirmações devem ser únicos.


## Como escrever boas questões de verdadeiro ou falso

Ao escrever qualquer questão, tenha em mente um objetivo de aprendizagem. As
questões podem servir para avaliação, prática ou discussão.

Uma questão de verdadeiro ou falso do MDQ é um item de *verdadeiro/falso
múltiplo*: um enunciado seguido de várias afirmações, cada uma julgada por conta
própria.

### Quando usar

* Use verdadeiro/falso para conteúdo que cabe em uma proposição: uma afirmação
  claramente verdadeira ou falsa. Bons exemplos são fatos, definições,
  previsões ("este código imprime `3`") e concepções erradas comuns
  [Clay 2001](references.md#questões-de-verdadeiro-ou-falso).
* Alunos respondem afirmações rapidamente, então uma questão cobre bastante
  conteúdo. Uma única afirmação é cara e coroa para quem chuta, então use várias
  afirmações por questão e várias questões por tema
  [Clay 2001](references.md#questões-de-verdadeiro-ou-falso).
* O verdadeiro/falso múltiplo mostra melhor a compreensão parcial do que a
  múltipla escolha. Um aluno que tem uma ideia certa e uma errada ao mesmo tempo
  é pego, em vez de escolher a única alternativa de que tem certeza
  [Brassil & Couch 2019](references.md#questões-de-verdadeiro-ou-falso).
* O verdadeiro/falso múltiplo tende a testar pensamento de nível mais baixo que a
  múltipla escolha [Haladyna et al. 2002](references.md#questões-de-verdadeiro-ou-falso).
  Para testar aplicação, coloque um cenário ou código no enunciado e pergunte
  sobre ele.

### Enunciado

* Dê ao enunciado conteúdo real: um cenário, um trecho de código, uma tabela ou
  uma pergunta à qual todas as afirmações se referem. "Judge the statements."
  desperdiça o enunciado.
* Mantenha as afirmações independentes: julgar uma afirmação não pode revelar a
  resposta de outra.

### Afirmações

* Expresse uma ideia por afirmação. Com duas ideias, um aluno que domina só uma
  não consegue responder, e uma parte falsa se esconde dentro de uma parte
  verdadeira.
* Escreva afirmações verdadeiras ou falsas sem exceções. Se a afirmação for uma
  opinião ou uma posição contestada, atribua-a: "Segundo Dewey, ...".
* Não copie frases do livro ou da aula. Parafraseie, ou pergunte sobre um caso
  novo, para que decorar a redação não baste.
* Evite afirmações negativas e nunca use dupla negação. Se a negação for
  inevitável, escreva em negrito (`**não**`).
* Evite modificadores extremos (`sempre`, `nunca`, `todos`, `nenhum`, `somente`):
  alunos que fazem prova com estratégia marcam essas afirmações como falsas.
  Evite qualificadores vagos (`geralmente`, `às vezes`, `alguns`, `pode`): são
  verdadeiros para quase todo leitor e significam coisas diferentes para cada
  aluno.
* Faça as afirmações verdadeiras e falsas com o mesmo tamanho, para que o tamanho
  não entregue a resposta.
* Construa as afirmações falsas a partir de concepções erradas reais, para que
  sejam plausíveis para quem não domina o conteúdo.
* Em causa e efeito, mantenha a primeira parte verdadeira e varie a veracidade da
  segunda parte.
* Use vocabulário simples, a não ser que o vocabulário seja justamente o que se
  testa.
* Misture afirmações verdadeiras e falsas sem nenhum padrão previsível.

Todas as diretrizes acima para afirmações seguem
[Clay 2001](references.md#questões-de-verdadeiro-ou-falso).

### Use o feedback

O feedback importa mais nas afirmações falsas. Alunos que julgam afirmações falsas
sem feedback levam a desinformação para as provas seguintes. Com feedback da
resposta correta, esse problema cai de cerca de 14% para cerca de 5% das respostas
[Uner et al. 2022](references.md#questões-de-verdadeiro-ou-falso).

* Em cada afirmação falsa, escreva no feedback a afirmação corrigida, ou por que a
  original não está correta. "Isto é falso" é um feedback muito ruim.
* Nas afirmações verdadeiras, explique por que valem.
* Em provas de prática, peça que os alunos corrijam as afirmações que marcaram como
  falsas. Com feedback, isso melhora a retenção desses itens
  [Uner et al. 2022](references.md#questões-de-verdadeiro-ou-falso).

### Exemplo

Ruim: enunciado vazio, duas ideias em uma afirmação, termo absoluto, afirmação
negativa, e a afirmação verdadeira é a mais longa.

```md
Judge the statements.

* [T] Lists are mutable and tuples are immutable.
* [F] Tuples can never be changed.
* [F] A list is not a sequence type.
* [T] Since Python 3.7, dictionaries preserve insertion order, as guaranteed by
  the language reference.
```

Revisada: o enunciado dá um caso concreto, cada afirmação testa uma ideia, e toda
afirmação tem feedback.

````md
Consider this code:

```python
a = (1, [2, 3])
b = a
```

Judge each statement.

* [T] `a[1].append(4)` runs without error.
  > The tuple is immutable, but the list inside it is mutable.
* [F] `a[0] = 5` replaces the first item of `a`.
  > Tuples do not support item assignment. This line raises `TypeError`.
* [T] After `a[1].append(4)`, `b[1]` is `[2, 3, 4]`.
  > `b = a` does not copy. Both names refer to the same tuple.
* [F] `len(a)` is `3`.
  > `a` has two items: the integer `1` and the list `[2, 3]`.
````
