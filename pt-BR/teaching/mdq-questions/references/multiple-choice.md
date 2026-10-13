# Múltipla escolha

## Sintaxe

Uma resposta correta escolhida em uma lista. O corpo é uma lista não ordenada em
que cada item começa com `[ ]` (errada) ou `[*]` (certa). As alternativas
erradas são chamadas de "distratores".

```md
What is the capital of Brazil?

* [ ] Lisbon
* [*] Brasília
* [ ] São Paulo
  > Largest city, but never the capital.
* [ ] Rio de Janeiro
  > It was the capital until 1960.
```

### Anatomia da alternativa

```md
* [value] [choice-id] Choice text
  > Feedback shown to the student who picked this choice.
  ! Comment for other instructors.
```

* `value` é ` ` (0), `*` (1) ou uma porcentagem, como `[50%]` ou `[-25%]`.
  As porcentagens devem ficar entre -1 e 1, então `[150%]` é inválido.
* Evite crédito parcial ou várias alternativas corretas. O formato permite isso,
  principalmente para revisões posteriores da pontuação das alternativas.
* `choice-id` é opcional, mas recomendado: permite que as respostas referenciem
  a alternativa pelo nome, e não pela posição. Deve ser seguro para URL e único.
* O feedback (`>`) e os comentários (`!`) podem ocupar várias linhas. Cada linha
  mantém o próprio prefixo. Ambos são opcionais.

### Frontmatter

| Campo   | Valores                                            |
| ------- | -------------------------------------------------- |
| shuffle | `true` para permitir embaralhar as alternativas    |
| grading | `symmetric` (padrão), `partial`, `all-or-nothing`  |

A não ser que seja pedido explicitamente, evite definir esses parâmetros. Se
ficarem sem valor, o professor pode definir valores para a prova toda.

### Correção

Uma porcentagem explícita na alternativa escolhida sempre prevalece. Caso
contrário:

* `partial` / `all-or-nothing`: alternativas não marcadas valem 0.
* `symmetric`: alternativas não marcadas recebem nota negativa, para que chutar
  ao acaso tenha média zero (4 alternativas, uma correta: uma resposta errada
  vale -0,33).

O feedback sempre aparece para a alternativa que o aluno escolheu, certa ou
errada. Por isso, coloque uma explicação também na alternativa certa.

### Armadilhas

* Os textos das alternativas devem ser únicos.
* Marcar várias alternativas como corretas é válido. O aluno ainda escolhe uma.
* Não marque todas as alternativas como corretas.


## Como escrever boas questões de múltipla escolha

Ao escrever qualquer questão, tenha em mente um objetivo de aprendizagem. As
questões podem servir para avaliação, prática ou discussão.

Salvo indicação em contrário, as diretrizes abaixo seguem
[Haladyna et al. 2002](references.md#questões-de-múltipla-escolha) e o
[NBME Item-Writing Guide](references.md#questões-de-múltipla-escolha). Itens
mal feitos tornam a questão mais difícil por motivos que não têm relação com o
que ela testa [Downing 2005](references.md#questões-de-múltipla-escolha).

* Teste uma ideia importante por questão. Evite trivialidades.
* Vá além da memorização quando o objetivo permitir: peça que o aluno aplique,
  analise ou julgue, usando um cenário novo em vez da redação do livro
  [Brame 2013](references.md#questões-de-múltipla-escolha).
* Mantenha as questões independentes: uma questão não pode entregar a resposta
  de outra.
* Evite perguntas de opinião ("Qual é a melhor linguagem?"), a não ser que o
  enunciado diga de quem é a opinião ou qual critério conta.
* Sem pegadinhas. A dificuldade deve vir do conteúdo, não da redação
  [Butler 2018](references.md#questões-de-múltipla-escolha).

### Enunciado e preâmbulo

* Coloque o problema inteiro no enunciado. Se for preciso apresentar um cenário,
  conceitos novos, um texto para o aluno ler, tabelas, trechos de código etc.,
  coloque isso em parágrafos de preâmbulo. Aplique a **regra de cobrir as
  alternativas**: um aluno que domina o conteúdo deve conseguir responder com as
  alternativas escondidas.
* Prefira uma pergunta direta a uma frase para completar. Se quiser uma questão
  de completar lacunas, prefira o tipo lacunas.
* Corte o enfeite: texto que não ajuda a responder nem torna um distrator
  atraente só testa a velocidade de leitura.
* Formule o enunciado de forma positiva. Se `NOT`, `EXCEPT` ou algo parecido for
  inevitável, escreva em maiúsculas e em negrito (`**NOT**`).
* Mova para o enunciado as palavras repetidas em todas as alternativas.

### Alternativa correta

* Garanta que exatamente uma alternativa esteja correta, ou claramente seja a
  melhor. Peça a um colega que responda a questão antes de usá-la.
* Não deixe a alternativa correta se destacar: muitas vezes ela é a mais longa,
  a mais precisa ou a única escrita como frase de livro.
* Varie a posição dela. Dependendo da configuração do sistema, as alternativas
  podem ter ordem fixa, ser embaralhadas ou ordenadas por algum critério (como
  tamanho da palavra, ordem alfabética etc.). Se o enunciado exigir uma ordem
  específica, defina `shuffle: false` no frontmatter.
* Se a ordem não importa para entender a questão, ordene as alternativas pelo
  tamanho.

### Distratores

* Construa os distratores a partir de erros reais dos alunos e de concepções
  erradas. Para cada questão, pense nos erros comuns e plausíveis e construa os
  distratores em torno deles [Gierl et al. 2017](references.md#questões-de-múltipla-escolha).
* Considere apenas erros conceituais: erros de digitação, de conta básica e
  outros erros pequenos costumam ser fáceis de perceber.
* Cada distrator deve ser plausível para um aluno que não domina o conteúdo.
  Elimine alternativas absurdas ou de brincadeira.
* O ideal é escrever uma alternativa correta com quatro distratores, mas três
  alternativas (uma correta e dois distratores) costumam bastar. Escolha só
  distratores que façam sentido: três boas alternativas valem mais que quatro ou
  cinco com enchimento, e economizam tempo de prova
  [Rodriguez 2005](references.md#questões-de-múltipla-escolha). Na prática, itens
  escritos por professores têm, em média, cerca de 1,5 distratores que funcionam
  [Tarrant et al. 2009](references.md#questões-de-múltipla-escolha). Use quatro
  quando tiver quatro alternativas plausíveis, e não porque sente a obrigação de
  ter um número fixo de distratores.
* Se o usuário pedir um número específico de alternativas, forneça o número
  pedido, mas tente, pelo menos, escrever alternativas de enchimento que façam
  sentido.
* Mantenha as alternativas homogêneas: mesmo tipo de coisa, mesma forma
  gramatical e mais ou menos o mesmo tamanho.
* Mantenha as alternativas mutuamente exclusivas. Intervalos numéricos
  sobrepostos e alternativas que implicam umas às outras deixam mais de uma
  resposta defensável.
* Ordene as alternativas de forma lógica (numérica, cronológica ou por tamanho)
  quando tiverem uma ordem natural. Desative o embaralhamento nessas questões.

### Evite estes padrões

* **Todas as anteriores:** um aluno que percebe duas alternativas corretas
  acerta a questão sem saber o resto [Brame 2013](references.md#questões-de-múltipla-escolha).
  Além disso, a questão passa a separar pior os alunos fortes dos fracos
  [Butler 2018](references.md#questões-de-múltipla-escolha).
* **Nenhuma das anteriores:** diz apenas o que o aluno rejeita, não o que ele
  sabe. Se for preciso, escreva uma alternativa concreta.
* **Alternativas combinadas** ("A e C", "B, mas não D"): testam raciocínio lógico,
  não conteúdo. Use uma questão de múltipla seleção.
* **Termos absolutos** (`always`, `never`) nos distratores: alunos que fazem
  prova com estratégia eliminam essas opções. Termos vagos de frequência
  (`usually`, `often`) são lidos de formas diferentes por alunos diferentes.
* **Pistas sonoras:** uma palavra do enunciado repetida só na alternativa correta.
* **Pistas gramaticais:** só a alternativa correta combina com o artigo, o número
  ou o tempo verbal do enunciado.
* **Convergência:** a alternativa correta compartilha mais termos com as outras
  alternativas.
* **Pares coletivamente exaustivos:** duas alternativas que cobrem todas as
  possibilidades ("aumenta" / "não aumenta"), de modo que a resposta tem de ser
  uma delas.

### Use o feedback

O MDQ mostra o feedback da alternativa escolhida. Explique a concepção errada de
cada distrator e por que a alternativa correta está certa. O feedback depois de
uma prova de múltipla escolha reduz o risco de que os alunos aprendam a resposta
errada a partir de um distrator [Butler 2018](references.md#questões-de-múltipla-escolha).

Você pode dar feedback também na alternativa correta, se isso ajudar a deixar
claro por que ela está certa.

### Comentários

Use comentários para dar contexto adicional ou explicar o raciocínio por trás da
construção da questão e de cada distrator. Isso ajuda o professor a revisar ou
revisar a questão depois. Não repita informações que já estão no feedback ou na
própria alternativa.

Comentários só são úteis quando trazem algo que não é evidente pelo enunciado,
pelas alternativas ou pelo feedback.

### Exemplo

Ruim: enunciado vago, alternativa correta é a mais longa, "todas as anteriores"
e um distrator absurdo.

```md
Python lists:

* [ ] are immutable
* [*] can be changed in place after creation, for example with `append`
* [ ] are a type of fish
* [ ] all of the above
```

Revisada: o enunciado apresenta o problema, e cada distrator é uma concepção
errada real, com feedback.

````md

Consider the Python code

```python
a = [1, 2]
b = a
b.append(3)
print(a)
```

What does it print?

* [*] `[1, 2, 3]`
  > `b = a` does not copy the list. Both names refer to the same object.
* [ ] `[1, 2]`
  > Assignment does not copy. Use `a.copy()` to get an independent list.
* [ ] An error, because lists are immutable
  > Lists are mutable. Tuples are the immutable sequence type.
````
