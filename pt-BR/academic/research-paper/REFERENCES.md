# Referências

Fontes por trás da skill `research-paper`. Este arquivo é para leitores humanos; a skill não o carrega.

## Fontes

- Simon Peyton Jones. _How to write a great research paper: seven simple
  suggestions_. Palestra e slides, Microsoft Research.
  <https://simon.peytonjones.org/great-research-paper/>,
  slides: <https://www.microsoft.com/en-us/research/wp-content/uploads/2014/02/simon-peyton-jones_paper.pdf>.
  Fonte primária. As sete sugestões: não espere, escreva; identifique sua ideia-chave; conte uma história; defina bem suas contribuições; deixe os trabalhos relacionados para depois; coloque seus leitores em primeiro lugar; ouça seus leitores. O resumo de quatro frases vem de Kent Beck, por meio destes slides.
- Jennifer Widom. _Tips for Writing Technical Papers_. Stanford InfoLab, 2006,
  revisado em 2009. <https://cs.stanford.edu/people/widom/paper-writing.html>.
  As cinco perguntas da introdução, contribuição até a página 3, exemplos que se repetem, definições antes do uso.
- Brett Mensh e Konrad Kording. _Ten simple rules for structuring papers_.
  PLOS Computational Biology 13(9): e1005619, 2017.
  <https://doi.org/10.1371/journal.pcbi.1005619>.
  Uma contribuição central: contexto, conteúdo e conclusão em todas as escalas; esboços com uma frase por parágrafo; feedback como iteração.
- George D. Gopen e Judith A. Swan. _The Science of Scientific Writing_.
  American Scientist 78, 1990.
  <https://www.gatsby.ucl.ac.uk/~pel/misc/gopen_swan.pdf>.
  Expectativas do leitor: posições de tema e de ênfase, informação antiga antes da nova, sujeito perto do verbo, ação no verbo.
- Zachary C. Lipton. _Heuristics for Scientific Writing (a Machine Learning
  Perspective)_. Approximately Correct, 2018.
  <https://www.approximatelycorrect.com/2018/01/29/heuristics-technical-scientific-writing-machine-learning-perspective/>.
  Elimine aberturas genéricas, não provoque o leitor, corte intensificadores, faça afirmações defensáveis, cite ao longo do texto.
- George M. Whitesides. _Whitesides' Group: Writing a Paper_. Advanced
  Materials 16(15): 1375–1377, 2004.
  <https://doi.org/10.1002/adma.200400767>.
  Esboce o artigo no início da pesquisa e reformule o esboço conforme a pesquisa evolui; construa o esboço em torno de figuras, tabelas e esquemas.

## Onde as fontes divergem

A skill toma o lado de Peyton Jones em cada caso, com as exceções indicadas.

- **Onde ficam os trabalhos relacionados.** Peyton Jones os coloca no fim, depois da ideia. Widom aceita os dois lugares: cedo quando são curtos ou contexto essencial, tarde quando a comparação exige o conteúdo técnico. A introdução de Widom também pergunta "por que isso ainda não foi resolvido?", o que puxa parte dos trabalhos anteriores para a frente, e Mensh e Kording estruturam a introdução em torno da lacuna na literatura. Muitos eventos de computação usam a seção 2 para eles por hábito. Lipton acrescenta que as citações pertencem ao texto inteiro, não só a uma seção. _Skill:_ fim por padrão, cite no ponto de uso, mova para antes apenas quando o problema não puder ser entendido sem eles.
- **O parágrafo "o restante deste artigo".** Peyton Jones o rejeita em favor de referências adiante a partir das contribuições. O resumo de contribuições de Widom também aponta para seções, mas muitos eventos e orientadores esperam o parágrafo de roteiro. _Skill:_ referências adiante, sem parágrafo de roteiro.
- **Voz passiva.** Peyton Jones: "evite-a a todo custo". Gopen e Swan argumentam que uma regra rígida falha: a passiva é a frase melhor quando mantém o sujeito do parágrafo na posição de tema. Alguns campos ainda escrevem a seção de métodos na passiva por convenção. _Skill:_ ativa por padrão, passiva quando servir à posição de tema (segue Gopen e Swan).
- **O resumo.** Peyton Jones (após Kent Beck): quatro frases, sendo problema, por que é interessante, o que a solução alcança e o que decorre disso. Mensh e Kording: contexto e lacuna, depois métodos e resultados principais, depois conclusão e relevância mais ampla. Lipton: incluir os resultados quantitativos. Essas propostas são compatíveis em espírito; a skill usa as quatro frases e acrescenta números.
- **Quando escrever.** Peyton Jones escreve o artigo antes de a pesquisa terminar, para conduzi-la. Whitesides concorda em substância: esboce no início do projeto e reformule o esboço conforme a pesquisa evolui. O modelo tradicional, pesquisar primeiro e escrever por último, não tem defensores entre essas fontes.
