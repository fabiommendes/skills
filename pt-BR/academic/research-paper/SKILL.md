---
name: research-paper
description: Escreva, reestruture ou revise um artigo científico: ideia-chave, resumo, introdução, contribuições, trabalhos relacionados e texto. Use quando o usuário redigir ou revisar um artigo, um capítulo de tese, ou pedir feedback sobre um deles.
---

# Artigo científico

Um artigo existe para transmitir ao leitor uma ideia útil e reutilizável. Tudo abaixo serve a esse objetivo. A abordagem segue "How to write a great research paper", de Simon Peyton Jones. Quando outros guias discordarem dele, a posição dele é o padrão.

Escreva no idioma do artigo. Os princípios valem em qualquer idioma.

## A ideia-chave

Um artigo tem um **ping**: uma ideia clara e precisa. Antes de redigir ou revisar qualquer coisa, enuncie-a em uma ou duas frases.

- Se você não consegue enunciá-la, esse é o primeiro problema. Pergunte ao autor.
- Se há várias ideias, há vários artigos. Diga isso.
- O artigo enuncia a ideia explicitamente: "A ideia principal deste artigo é...". Nunca deixe o leitor adivinhar.

## A história

Conte a história que você contaria em um quadro branco: aqui está um problema; ele é interessante; ele não está resolvido; aqui está minha ideia; ela funciona (detalhes, evidências); aqui está como ela se compara a outras abordagens.

Estrutura padrão de um artigo para conferência, com orçamento de páginas:

| Parte | Orçamento | Conteúdo |
|---|---|---|
| Título | | A ideia, não o tema. |
| Resumo | 4 frases | Enuncie o problema. Diga por que ele é interessante. Diga o que a solução alcança. Diga o que decorre disso. Dê números quando os resultados forem quantitativos. |
| Introdução | 1 página | O problema, depois as contribuições. Nada além disso. |
| O problema | 1 página | |
| A ideia | 2 páginas | |
| Os detalhes | 5 páginas | Evidência para cada contribuição. |
| Trabalhos relacionados | 1–2 páginas | |
| Conclusões e trabalhos futuros | ½ página | |

Ajuste os orçamentos ao limite de páginas do evento e mantenha a ordem. Em áreas com estrutura obrigatória, como IMRaD, mantenha os nomes de seção exigidos e conte a mesma história dentro deles.

## Introdução

- Apresente o problema com um **exemplo** concreto. Mostre um montinho, não uma montanha: "Considere este programa, que tem um bug interessante" é melhor que "Programas têm bugs. Eliminar bugs é muito importante [1–5]." Corte toda frase de abertura que serviria em qualquer artigo da área.
- Termine com as contribuições em uma **lista com marcadores**. Escreva essa lista primeiro: ela guia o artigo inteiro, e o corpo existe para sustentá-la.
- Cada contribuição é **refutável**: uma afirmação que pode se mostrar falsa. "Provamos que a checagem de tipos é decidível (Seção 4)", e não "Estudamos suas propriedades".
- Cada contribuição aponta para a seção que contém sua evidência. Essas referências substituem o parágrafo "O restante deste artigo está organizado da seguinte forma"; não o inclua.

## Evidência

Cada afirmação na introdução tem evidência no corpo: um teorema, uma medição, uma comparação ou um estudo de caso. Relacione afirmações a evidências. Uma afirmação sem evidência ganha evidência ou é cortada; uma evidência que nenhuma afirmação exige é cortada ou vira afirmação.

Afirme apenas o que a evidência sustenta, nem mais. Prefira "muitos" a "a maioria", a menos que você tenha contado. Marque opiniões como opiniões.

## Trabalhos relacionados

Coloque os trabalhos relacionados perto do fim, depois da ideia. Antes que o leitor conheça o problema, comparações resumidas com outros trabalhos são incompreensíveis, e ficam entre o leitor e a ideia.

- Ainda cite no ponto de uso: quando você adotar a definição, o método ou o resultado de alguém, cite ali mesmo.
- Seja generoso. Crédito não funciona como dinheiro: dar crédito a outros não reduz o seu. Descreva o trabalho alheio de modo que os autores concordassem com a descrição.
- Reconheça as fraquezas da sua própria abordagem.

Mova os trabalhos relacionados para antes apenas quando o leitor não puder entender o problema sem eles, ou quando o evento exigir. Explique ao autor o motivo.

## Apresentando a ideia

- Intuição primeiro, detalhes depois. Um leitor com a intuição consegue acompanhar os detalhes, e quem pula os detalhes ainda leva algo consigo; o inverso não funciona.
- Exemplos primeiro, depois o caso geral.
- Use o caminho mais direto até a ideia. Deixe de fora a história de como você a encontrou, por mais difícil que tenha sido.
- Use um exemplo que se repete quando o artigo tiver várias partes técnicas.
- Defina cada termo e cada notação uma única vez, antes do primeiro uso.
- Dê ao artigo uma estrutura visual: seções, marcadores, itálico, código formatado, figuras. As figuras carregam o argumento; cada legenda diz qual é o ponto da figura.

## Frases

- Use a voz ativa. "Nós" são os autores, ou os autores e o leitor; "você" é o leitor. "Executamos 34 testes", e não "34 testes foram executados".
- Escolha o sujeito de cada frase pelo parágrafo, não por regra: comece com a informação antiga que liga ao que veio antes, e termine com a informação nova que você quer enfatizar. A voz passiva é adequada quando mantém o sujeito do parágrafo na frente, como em "O pólen é disperso por abelhas" em um parágrafo sobre pólen. (Gopen and Swan)
- Mantenha o sujeito perto do verbo. Coloque a ação no verbo: "o coletor foi lento", e não "a velocidade da recuperação de armazenamento deixou a desejar".
- Use palavras simples: "descobrir", e não "envidar esforços para apurar".
- Corte os intensificadores: "muito", "extremamente", "claramente", "novo".
- Monte os parágrafos como contexto, conteúdo e conclusão: a primeira frase prepara o ponto e a última o fecha. (Mensh and Kording)

## Redação

1. Escreva a ideia-chave e a lista de contribuições. Mostre-as ao autor e obtenha concordância antes de escrever mais.
2. Esboce a história com uma frase por parágrafo.
3. Redija o corpo, depois a introdução, depois o resumo.
4. Revise seu próprio rascunho com os passos abaixo.

Escrever cedo expõe o que ainda não está compreendido. Marque resultados, provas ou dados faltantes como `TODO` e liste-os para o autor. Nunca invente resultados, dados ou citações; marque uma citação necessária como `[CITE: o que ela sustenta]`.

## Revisão

Leia como um leitor de primeira viagem. "Me perdi aqui" importa mais que um erro de digitação. Relate os achados nesta ordem, cada um com sua localização, o problema e uma sugestão de reescrita:

1. **Ideia-chave:** você consegue enunciá-la? O artigo a enuncia explicitamente?
2. **Contribuições:** listadas, refutáveis, com referência adiante e sustentadas por evidência.
3. **História:** onde o leitor se perde; desvios pela história da descoberta; trabalhos relacionados antes da ideia.
4. **Apresentação:** casos gerais antes dos exemplos; termos usados antes de serem definidos.
5. **Frases:** as regras acima.
6. **Erros de digitação e pontuação:** agrupados no fim.

Relate sem editar, a menos que o autor peça edições.

## Respondendo a revisores

Trate cada crítica como um sinal de que o artigo deixou de explicar algo. Corrija o artigo para que o ponto fique claro até para um leitor apressado, em vez de discutir na resposta. Agradeça aos revisores.
