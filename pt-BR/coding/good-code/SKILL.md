---
name: good-code
description: |
  Heurísticas de design e legibilidade de código, independentes de linguagem, que cobrem nomes, comentários e docstrings, organização de módulos, modelagem de tipos e dados, design de funções, tratamento de erros, classes, fronteiras e testes. Use ao projetar tipos ou módulos, ao refatorar, ao revisar código ou um diff quanto à qualidade, ou quando o usuário perguntar sobre nomes, estrutura ou code smells.
---

# Bom código

Otimize para quem lê o código. Estas heurísticas guiam o trabalho.

Aplique-as ao código que você escreve ou altera. Se notar problemas no código ao redor, não corrija nem liste cada um. Mencione brevemente que há alguns problemas de estilo e pergunte se devem ser corrigidos.

Se a tarefa é escrever ou revisar testes, leia [testing.md](testing.md).


## Nomes

Nomes refletem o design. Se nomear uma coisa é difícil ou confuso, o design provavelmente está errado.

- Nomes revelam a intenção: por que a entidade existe, o que ela faz e como é usada. Só pelo nome e pelo tipo, o propósito e o uso devem ficar claros.
- Uma palavra para cada conceito em toda a base de código. Não misture `fetch`, `get` e `retrieve` para a mesma operação. Não use o mesmo verbo para operações diferentes. Verifique se o projeto define um glossário de termos-chave e conceitos e use-os de forma consistente.
- O tamanho do nome acompanha o escopo. Um índice de laço pode ser `i`; uma exportação no nível do módulo não pode.
- Nomes de uma letra são aceitáveis quando seguem convenções matemáticas estabelecidas (i, j, k para índices; x, y, z para coordenadas, etc.). Eles servem para abstrações matemáticas e nunca se referem a objetos do domínio. Por exemplo, `x` e `xs` são aceitáveis em uma função genérica sobre uma coleção. Mas um callback que espera um tipo específico `User` deve usar `user`, e não `u`.
- Classes e tipos são locuções nominais. Funções com efeitos colaterais são locuções verbais. Funções puras podem ser substantivos (`area`) ou verbos (`computeArea`). Escolha um estilo por base de código.
- Evite codificar o tipo ou o escopo no nome. Evite nomes criativos demais. Evite palavras genéricas (`Data`, `Info`, `Manager`, `Processor`) que não distinguem nada.
- Troque literais com significado de domínio (limites, tempos limite, taxas) por constantes nomeadas.


## Comentários

- NÃO cite documentos de processo (handoffs, planos, especificações em revisão) nos comentários. Leitores futuros podem não ter acesso a eles, e os comentários ficam desatualizados.
- Explique o motivo de uma decisão, não que alguém a tomou (por exemplo, em uma conversa). O comentário deve ser autocontido, completo e não depender de contexto externo.

Ao encontrar um comentário no código que você altera:

- **Apague**: comentários errados ou enganosos devem ser apagados na hora. Eles são ativamente nocivos. Também remova comentários sem valor: repetições do código ou dos tipos, código comentado, créditos de autoria, etc.
- **Mantenha**: a intenção por trás de uma decisão não óbvia, avisos sobre consequências, cabeçalhos legais, esclarecimentos sobre algo que você realmente não pode mudar, justificativas para supressões de linter ou de verificador de tipos, verificações de segurança, etc.
- **Refatore**: TODOs, FIXMEs e comentários que indicam dívida técnica. Corrija-os se a correção for trivial e local. Mova-os para uma issue se a correção for clara, mas não local. Deixe-os como estão se a correção não for clara.
- **Reescreva**: comentários mal redigidos devem ser reescritos para ganhar clareza e precisão.

Comentários de documentação e docstrings:

- APIs públicas devem ser documentadas. Documentar APIs privadas é aceitável, mas mantenha os detalhes no mínimo.
- O comentário ou a string de documentação e o código documentado formam sempre um parágrafo. Deixe linhas em branco separando-o de outros parágrafos no mesmo nível de aninhamento.
- Nunca use a forma de bloco (`/** ... */` ou `""" ... """`) em uma única linha. Comentários de várias linhas sempre começam com uma frase que os resume. Se for preciso mais explicação, coloque detalhes depois da frase-resumo. Para funções, os detalhes podem incluir os parâmetros, o valor de retorno, as exceções e os efeitos colaterais.
- Não documente parâmetros nem o valor de retorno quando tudo isso for óbvio pela assinatura da função. Se um único parâmetro precisar de esclarecimento, explique-o em um segundo parágrafo. Se dois ou mais precisarem, documente todos, inclusive os triviais.


## Organização do módulo

- Mantenha juntas as funcionalidades relacionadas.
- O módulo deve ser lido de cima para baixo: as definições mais importantes vêm primeiro (geralmente os tipos). As demais seguem em ordem decrescente de importância e de chance de serem usadas de fora do módulo. Esta regra também vale para os métodos de uma classe. Em linguagens que exigem definição antes do uso, se a definição central depender de muitas definições anteriores, mova-as para um módulo auxiliar.
- Se um módulo ficar grande demais, considere dividi-lo em módulos auxiliares menores.
- Módulos costumam ser organizados como coleções (uma biblioteca de funções) ou como funcionalidade centrada em um tipo específico. No segundo caso, coloque esse tipo no topo: dê destaque a ele!
- Se mais de um tipo é o foco do mesmo módulo, considere separá-los em módulos distintos. Tipos auxiliares não contam.
- Pense em como o módulo se leria como prosa: frases, parágrafos, seções, capítulos. No código, separamos parágrafos com linhas em branco e seções com comentários de seção. Cada arquivo corresponde a um capítulo.


## Tipos

- Projete em torno dos dados. As funções vêm depois.
- Tipos devem ser focados e componíveis. A composição costuma favorecer coesão, reuso e expressividade.
- Vá além da composição: analise o domínio e procure relações que possam ser descritas como alguma estrutura algébrica. Como combinar comportamentos? Quais dados são processados juntos de forma natural? Quais transformações são importantes? Você identifica algum padrão funcional, como Functor (map/flatMap), Monoid (empty/combine) ou Applicative (pure/<*>)? Em linguagens que não usam a nomenclatura funcional, aplique os padrões sem os nomes.
- Torne estados inválidos não representáveis: modele os tipos para reduzir ao mínimo o número de estados inválidos que podem ser representados. O ideal é que não haja nenhum. Um bug não pode acontecer se não é possível expressá-lo no código. Tipos enumerados, sealed classes, uniões de tipos e construções semelhantes costumam ajudar a atingir esse objetivo.
- Use ocultação de dados se a abordagem anterior falhar ou se a representação usar tipos internos complicados. Tipos simples devem expor todos os campos ou ocultar todos eles. Ocultar todos é útil para implementar o padrão "Parse, don't validate".
- Prefira imutabilidade. Use-a como padrão e mude apenas se houver um bom motivo para mutabilidade. Ganhos marginais de desempenho fora de laços executados com frequência não são justificativa suficiente.
- Se um tipo ficar grande demais, extraia partes dele e use composição quando elas puderem ser separadas de forma significativa e reutilizadas ou testadas de forma independente.
- Se um padrão se repetir entre tipos, extraia-o para uma abstração de tipo genérica. Defina genéricos, interfaces ou protocolos conforme a linguagem e o contexto.
- Use aliases de tipo e programação em nível de tipos livremente para melhorar a legibilidade.
  - Tipos primitivos geralmente devem receber alias para sinalizar a intenção (por exemplo, `UserId` em vez de `String`). Isso também abre caminho para endurecê-los no futuro, como novos tipos ou branded types.
  - Trate operações em nível de tipos como código funcional: componíveis, reutilizáveis, focadas e documentadas. Se a linguagem permitir, escreva testes em nível de tipos para garantir a correção.


## Funções

- Mantenha as funções focadas: faça uma coisa só, em um único nível de abstração. Funções puras sempre fazem uma coisa só. Funções com efeitos devem executar um único efeito.
- Ao projetar um conjunto de funções ou métodos, projete para composição. Extraia o conjunto mínimo de primitivas que cobre todos os comportamentos desejados e exponha-as como API pública.
- Funções planas e pequenas. Aninhamento profundo é o sinal para extrair, possivelmente para uma função aninhada, se a linguagem suportar. Em funções grandes e complexas, auxiliares aninhados não contam para o tamanho da função externa.
- Menos argumentos é melhor. Três é o teto prático. Se a função recebe muitas opções, agrupe-as em um objeto de configuração (ou use argumentos somente por palavra-chave, em Python).
- Evite argumentos booleanos sem nome: na chamada, não fica claro se `true` ativa ou desativa o recurso. Dê nomes às flags de forma que o padrão se leia naturalmente (`cache=True` em vez de `no_cache=False`). Se as duas opções lerem bem, considere extrair como enum.
- Sem argumentos de saída. Altere o objeto dono ou retorne um valor.
- Prefira separar comandos de consultas: uma função ou muda o estado, ou responde a uma pergunta. Exceções atômicas ou idiomáticas (`pop`, compare-and-swap) são aceitáveis.
- Pequenas quantidades de duplicação são aceitáveis. Extraia quando isso criar uma abstração útil e compreensível. Se for difícil nomear a abstração, talvez não valha a pena extraí-la.
- Não superabstraia. Aplique a mesma regra dos comentários: `isEven(x)` é uma abstração ruim para `x % 2 === 0`, pelo mesmo motivo que não escreveríamos um comentário explicando este trecho trivial de código. É aceitável expor detalhes de baixo nível em lógica trivial.
- Se a função for longa ou complexa demais, considere extrair os detalhes internos para uma classe privada. A instância funciona como um closure que permite inspecionar os passos intermediários da execução.


## Tratamento de erros

As duas abordagens mais comuns para tratar erros são o padrão de resultado/opcional e as exceções. Resultados obrigam quem chama a tratar os casos de falha. Exceções deixam o erro se propagar. Cada uma impõe obrigações diferentes a quem chama. Uma base de código pode misturar os dois estilos se cada um for usado de forma consistente e previsível. Não os misture sem critério.

- Prefira exceções para condições excepcionais (invariantes quebradas, estados inesperados, recursos indisponíveis, etc.), e não para o fluxo de controle normal.
- Prefira tipos de resultado (por exemplo, `Result<T, E>`, `Optional<T>` ou similares) para desvios esperados do caminho feliz.
- Mas as convenções da linguagem têm precedência. Por exemplo, coleções em Python levantam `KeyError` e `IndexError` em vez de retornar opcionais, então em Python seguimos isso.
- Inclua contexto: exceções e resultados devem informar a operação tentada e por que ela falhou. Evite mensagens de texto puras como única fonte de contexto. Use opcionais quando o contexto for trivial e houver um único motivo óbvio para a falha.
- Tipos opcionais sobre coleções e strings exigem mais cuidado: existe diferença semântica entre `null` e o valor vazio? Se não existir, remova o nullable. Se existir, documente com clareza o que a diferença significa.


## Classes

- Classes são uma forma de definir tipos em linguagens orientadas a objetos. Não traga conceitos de OO só porque o tipo foi declarado como classe. Evite hierarquias gratuitas, ocultação de dados, estado e considerações de variância.
- Evite herança concreta: OO mistura tipos, interfaces, reuso de código e taxonomias. Só taxonomias exigem herança concreta. Use-a quando o domínio tiver uma taxonomia real e estável. Caso contrário, costuma ser uma abstração frágil e desnecessária.
- Classes podem representar muitas coisas: tipos, hierarquias, closures, comportamento compartilhado de uma interface ou uma classe base abstrata. Não misture papéis.
- Dependa de interfaces nas fronteiras ou onde existir mais de uma implementação. Mantenha a construção (montagem/wiring, fábricas, injeção) separada da lógica de execução.


## Fronteiras

- Encapsule APIs de terceiros que não são centrais em uma interface moldada às suas necessidades. Não deixe tipos externos se espalharem pelo código: o encapsulamento é onde você absorve as mudanças deles.
- Aplique regra semelhante às camadas de transporte e persistência (APIs, bancos de dados): projete primeiro os tipos centrais, derive um DTO para cada fronteira a partir deles e não deixe os DTOs chegarem ao núcleo da aplicação.
- Se você usa um framework ou biblioteca central para a aplicação, adote as convenções e a nomenclatura dele.


## Refatoração e evolução

Ao refatorar, corrigir bugs ou ajustar código:

- Quebrar APIs públicas em código de biblioteca é caro. Prefira mudanças aditivas e deprecações.
- Quebrar APIs privadas ou internas em bases de código tipadas pode ser barato. Se o raio de impacto for pequeno, você pode refatorar com agressividade. Raios de impacto grandes exigem planejamento, mas a refatoração ainda pode valer a pena.


## Design simples

O design está bom o suficiente quando, nesta ordem de prioridade, ele:

1. Passa em todos os seus testes.
2. Expressa a intenção do autor.
3. Não usa mais código do que precisa.

**Regra do escoteiro:** deixe o código que você altera um pouco mais limpo do que encontrou. Faça isso aos poucos, durante outro trabalho, e não como um projeto de limpeza separado.
