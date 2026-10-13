---
type: doc
status: active
tags: [prompt-engineering, claude, sonnet-5, opus-5, effort, adaptive-thinking, agentic-prompting]
relatedTo: [prompt]
---

# Criar prompts eficazes para o Claude

Este guia descreve um fluxo de trabalho para criar prompts eficazes ao usar o Claude.

## Boas práticas

Resumido da documentação da Anthropic, atualizado em 2026-09-20:

- [Boas práticas de prompting](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Prompting Claude Sonnet 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5)
- [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)

## Princípios gerais

**Seja claro e direto.** O Claude não conhece as suas convenções. Declare
explicitamente o formato de saída e as restrições desejadas, e use passos
numerados quando a ordem ou a completude importar. Se quiser trabalho "além do
esperado", peça: "Crie um painel de análises. Inclua o maior número possível de
funcionalidades e interações relevantes. Vá além do básico."

A regra de ouro: mostre o prompt a um colega sem nenhum contexto. Se ele ficaria
confuso, o Claude também ficará.

**Explique o motivo.**

**Use exemplos.** Eles devem refletir o caso de uso real, cobrir casos de borda
e variar o suficiente para que o Claude não se prenda a um padrão não
intencional. Envolva-os nas tags `<example>` / `<examples>`.

**Estruture com tags XML.** `<instructions>`, `<context>`, `<input>`. Use nomes
de tags consistentes e aninhe quando o conteúdo tiver hierarquia.

**Defina um papel** no prompt de sistema. Uma frase muda o comportamento e o tom.

**Contexto longo (mais de 20k tokens):** coloque os documentos no *topo*, acima
da consulta, das instruções e dos exemplos. Em testes, colocar as consultas no
fim melhorou a qualidade da resposta em até 30%. Envolva cada documento em
`<document>`, com os subtags `<source>` e `<document_content>`. Em tarefas com
documentos longos, peça ao Claude para citar os trechos relevantes nas tags
`<quotes>` antes de fazer o trabalho.

## Saída e formatação

Diga ao Claude o que fazer, não o que evitar. Em vez de "não use markdown",
diga "componha sua resposta em parágrafos de prosa fluida", ou use um indicador
de formato XML como `<smoothly_flowing_prose_paragraphs>`. O estilo de
formatação do seu prompt influencia o estilo da saída, então um prompt sem
markdown tende a gerar menos markdown.

Os modelos mais recentes usam LaTeX por padrão em matemática. Peça texto simples
explicitamente se precisar.

**Prefills acabaram.** A partir da geração 4.6, uma mensagem parcial do
assistente na última rodada retorna erro 400. Substitutos: saídas estruturadas
ou enums de ferramentas para controlar o formato; uma instrução direta como
"responda sem preâmbulo" para remover o preâmbulo; mover as continuações para o
turno do usuário ("Sua resposta anterior foi interrompida e terminou com `[...]`.
Continue de onde parou."); injetar lembretes no turno do usuário ou por meio de
ferramentas para reidratar o contexto.

## Pensamento e esforço

O pensamento adaptativo (`thinking: {type: "adaptive"}`) substitui o pensamento
estendido manual. `budget_tokens` retorna erro 400 nos modelos 4.7 e
posteriores. Controle a profundidade com o parâmetro `effort` (`low` / `medium` /
`high` / `xhigh` / `max`) e use `max_tokens` como teto rígido.

Os padrões variam por modelo: no Opus 4.6–4.8 e no Sonnet 4.6, omitir `thinking`
desliga o pensamento. **No Opus 5 e no Sonnet 5, o pensamento vem ligado por
padrão.**

Dá para controlar por prompt quando o pensamento adaptativo é acionado. Para
pensar menos:

```text
Thinking adds latency and should only be used when it will meaningfully improve
answer quality - typically for problems that require multistep reasoning. When in
doubt, respond directly.
```

Prefira instruções gerais ("pense com cuidado") a planos passo a passo escritos
à mão; o raciocínio do próprio Claude costuma superar o que um humano
prescreveria. As tags `<thinking>` dentro de exemplos few-shot ensinam um padrão
de raciocínio.

## Claude Sonnet 5

Prompts existentes do Sonnet 4.6 funcionam bem sem ajustes. Normalmente precisam
de ajuste:

**Tamanho da resposta.** O Sonnet 5 ajusta o tamanho à complexidade da tarefa,
em vez de usar uma verbosidade fixa: mais curto em consultas, mais longo em
análises abertas. Se o seu produto depende de um estilo, ajuste-o, preferindo
exemplos positivos a instruções de "não faça":

```text
Provide concise, focused responses. Skip non-essential context, and keep examples minimal.
```

**Esforço.** O padrão é `high`. Use `xhigh` para as tarefas de código e agentes
mais difíceis, `medium` para caminhos sensíveis a custo, e `low` só para tarefas
curtas e delimitadas ou sensíveis a latência. Mapeamento aproximado de migração:
Sonnet 5 em `medium` ≈ Sonnet 4.6 em `high`; Sonnet 5 em `high` ≈ Sonnet 4.6 em
`max`. Ao fazer benchmark, compare pelo tamanho do pensamento observado, não pelo
nome do esforço.

O Sonnet 5 respeita o esforço de forma rigorosa nas faixas baixas: em `low` e
`medium`, ele limita o trabalho exatamente ao que foi pedido, com algum risco de
pensar pouco em tarefas moderadamente complexas. Se o raciocínio parecer raso,
**aumente o esforço em vez de contornar com o prompt**.

**`max_tokens` precisa de folga.** Ele limita o pensamento mais o texto da
resposta. Por isso, orçamentos apertados em `high`/`xhigh` podem gerar uma
resposta quase toda de pensamento, seguida de uma resposta cortada com
`stop_reason: "max_tokens"`. O Sonnet 5 também usa um novo tokenizador que gera
cerca de 30% mais tokens para o mesmo texto, então limites ajustados para o 4.6
podem cortar a resposta.

**Parâmetros de amostragem são rejeitados.** `temperature`, `top_p` ou `top_k`
fora do padrão retornam erro 400. Ajuste o tom e a variedade pelo prompt de
sistema. O pensamento estendido manual também foi removido (erro 400).

**Uso de ferramentas.** Mais agêntico que o 4.6: recorre a ferramentas e a ciclos
de autoverificação com facilidade, e o esforço `high`/`xhigh` aumenta bastante o
uso de ferramentas. Com o pensamento *desligado*, ele tem menos chance de usar
ferramentas. Se você depende delas, adicione um incentivo explícito.

**Atualizações de progresso.** O Sonnet 5 dá atualizações regulares e boas,
sozinho, durante traços agênticos longos. Remova instruções desnecessárias, como
"a cada 3 chamadas de ferramenta, resuma o progresso".

**Seguimento literal de instruções.** Ele não generaliza em silêncio uma
instrução de um item para outro e não infere pedidos que você não fez. É bom
para extração estruturada e pipelines ajustados. Quando quiser amplitude, declare
o escopo ("Aplique esta formatação a todas as seções, não só à primeira").

**Harnesses de revisão de código** ajustados para modelos antigos podem mostrar
menor recall. É efeito do harness, não regressão de capacidade. "Relate apenas
problemas de alta severidade" agora é seguido fielmente. Peça cobertura total e
filtre em uma passagem separada:

```text
Report every issue you find, including ones you are uncertain about or consider
low-severity. Do not filter for importance or confidence at this stage - a separate
verification step will do that. For each finding, include your confidence level and
an estimated severity so a downstream filter can rank them.
```

**Padrões de frontend.** Em briefings abertos, o Sonnet 5 adota um estilo próprio
consistente, e um direcionamento vago ("deixe mais limpo") apenas troca uma
paleta fixa por outra. Duas coisas funcionam: especificar uma alternativa
concreta (códigos hex exatos da paleta, tipografia, espaçamento, raios de borda),
ou fazer o modelo propor opções primeiro. Por exemplo: "Antes de construir,
proponha 4 direções visuais distintas para este briefing (cada uma com: hex de
fundo / hex de destaque / tipografia, mais uma justificativa de uma linha). Peça
ao usuário que escolha uma e implemente só essa direção." Como `temperature` não
está disponível, o padrão de propor primeiro é a forma recomendada de obter
variedade entre execuções.

**Produtos de código interativos.** Use `xhigh` ou `high`, adicione um modo
automático e reduza as rodadas exigidas do usuário. Especifique tarefa, intenção
e restrições por completo no primeiro turno. Prompts incompletos espalhados por
muitos turnos custam mais tokens e às vezes rendem menos.

## Claude Opus 5

Feito para código agêntico complexo e trabalho de longo horizonte. Funciona bem
com os prompts existentes do Opus 4.8. Sua janela de contexto de 1M de tokens é
ao mesmo tempo o padrão e o máximo, e o seguimento de instruções se mantém em
toda ela.

**Verbosidade é o principal ponto.** As respostas do Opus 5 voltadas ao usuário
são *mais longas* que as dos modelos Opus anteriores, e o esforço controla quanto
ele pensa, não quanto ele diz. Reduzir o esforço não encurta de forma confiável a
resposta visível. Peça brevidade explicitamente:

```text
Keep responses focused, brief, and concise. Keep disclaimers and caveats short, and
spend most of the response on the main answer. When asked to explain something, give
a high-level summary unless an in-depth explanation is specifically requested.
```

Em um prompt de sistema longo, repita um lembrete curto perto do fim
(`<tone_preference>Keep outputs reasonably concise.</tone_preference>`).

**Narração.** Ele anuncia longamente o que vai fazer. Descreva o ritmo que você
quer: uma frase antes da primeira chamada de ferramenta, atualizações breves só
para achados importantes ou mudanças de direção, e uma mensagem final que comece
pelo resultado.

**Entregáveis escritos** (relatórios, arquivos Markdown) também ficam mais longos.
Adicione "ajuste o tamanho dos documentos escritos ao que a tarefa exige; não
encha com seções de enchimento, resumos redundantes ou trechos padronizados".

**Remova instruções de verificação.** O Opus 5 verifica o próprio trabalho sem
precisar de pedido. Instruções herdadas como "inclua uma etapa final de
verificação" ou "use um subagente para verificar" causam verificação excessiva.
Apagá-las economiza tokens sem perda de qualidade. Vale o mesmo para prompts de
reconferência do tipo "revise sua resposta".

**Limite o escopo.** O Opus 5 pode ampliar a tarefa, acrescentando passos que não
foram pedidos. Para trabalho restrito:

```text
Deliver what was asked, at the scope intended. Make routine judgment calls yourself,
and check in only when different readings of the request would lead to materially
different work. If the request seems mistaken or a better approach exists, say so in
a sentence and continue with the task as asked rather than quietly narrowing,
widening, or transforming it.
```

**Subagentes.** O Opus 5 delega com mais facilidade que os modelos anteriores. A
qualidade da coordenação é boa (padrões escritor-verificador funcionam, e os
agentes raramente sobrescrevem uns aos outros), mas a delegação multiplica o
custo em tarefas pequenas:

```text
Delegate to a subagent only for large tasks that are genuinely independent and
parallelizable, such as a wide multi-file investigation. Do not delegate work you can
finish yourself in a handful of tool calls, and do not use subagents to verify or
double-check your own work. If one subagent can complete the task, use one rather
than several, and keep spawn counts low.
```

No Claude Code e no Agent SDK existem limites determinísticos:
`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`,
e o `max_budget_usd` do SDK.

**Narração de correções.** O Opus 5 narra mais as correções às próprias
declarações anteriores do que os modelos anteriores. Limite isso a correções que
mudem o código, as conclusões ou as decisões do usuário.

**Esforço.** `low` e `medium` entregam boa qualidade com uma fração dos tokens e
da latência. Use-os como principal controle de custo e latência, e `xhigh` para
trabalho agêntico exigente. Refaça uma varredura de esforço com as suas próprias
avaliações, em vez de herdar os padrões de um modelo anterior.

**Desligar o pensamento é desencorajado.** Ele só pode ser desligado com esforço
`high` ou inferior. Ao fazer isso, surgem dois artefatos: chamadas de ferramenta
escritas como texto visível em vez de blocos `tool_use` estruturados (a chamada
nunca roda, e, em loops de agente, o texto vazado polui as rodadas seguintes), e
tags XML do tipo `<thinking>` vazando para a resposta. Pensamento ligado com
esforço `low` geralmente supera pensamento desligado com custo parecido. Se for
preciso desligar, remova qualquer regra do prompt de sistema que mande o modelo
não pensar (isso aumenta o vazamento de tags) e adicione:

```text
When you use a tool, you may say a brief sentence first. If no tool can express what
the user asked for, say so instead of guessing. Do not include internal or system XML
tags in your response.
```

**Revisão de código.** Alta precisão e recall, que se sustentam com esforço menor.
Isso permite uma passagem rápida na hora da revisão e uma passagem completa
depois. Como no Sonnet 5, "seja conservador" é levado ao pé da letra. Peça tudo e
filtre em separado.

## Padrões agênticos e de uso de ferramentas

**Diga o que você quer em relação à ação.** "Você pode sugerir algumas mudanças?"
gera sugestões; "altere esta função para melhorar o desempenho" gera edições. Para
tornar a ação o padrão, adicione um bloco `<default_to_action>`; para tornar a
pesquisa o padrão, adicione um bloco `<do_not_act_before_instructions>`.

**Reduza a linguagem agressiva.** Prompts escritos para combater o acionamento
insuficiente em modelos antigos ("CRÍTICO: você DEVE usar esta ferramenta
quando...") agora causam acionamento excessivo. Basta "Use esta ferramenta
quando...".

**Chamadas de ferramenta em paralelo** acontecem nativamente. Um bloco explícito
`<use_parallel_tool_calls>` leva a taxa para perto de 100%. Inclua a ressalva
sobre chamadas dependentes e a proibição de chutar parâmetros.

**Trabalho de longo horizonte entre janelas de contexto:** use um prompt diferente
para a primeira janela (montar testes e scripts), faça o modelo acompanhar os
testes em um arquivo estruturado como `tests.json` e o progresso em notas livres,
use o git como registro de estado e prefira iniciar uma janela de contexto nova a
compactar. Esses modelos são bons em redescobrir o estado a partir do sistema de
arquivos. Dê instruções explícitas de retomada ("revise progress.txt, tests.json e
os logs do git").

**Autonomia e segurança.** Sem orientação, os modelos podem tomar ações difíceis
de reverter. Peça confirmação para operações destrutivas, force-push e qualquer
coisa visível para outras pessoas, e proíba atalhos destrutivos como
`--no-verify`.

**Excesso de engenharia.** Os modelos Opus mais novos acrescentam arquivos,
abstrações e código defensivo que ninguém pediu. Um bloco de escopo,
documentação, código defensivo e abstrações mantém as soluções mínimas.

**Manipulação de testes.** Diga ao modelo que os testes verificam a correção e
não definem a solução. Proíba valores fixos no código e contornos por scripts
auxiliares, e convide-o a relatar que uma tarefa ou um teste está errado, em vez
de contorná-lo.

**Alucinação.** Um bloco `<investigate_before_answering>` ("nunca especule sobre
código que você não abriu; se o usuário citar um arquivo, você DEVE lê-lo antes
de responder") mantém as respostas ancoradas.

**Arquivos temporários.** Arquivos de rascunho costumam melhorar os resultados de
código agêntico. Peça a limpeza no fim da tarefa se preferir não mantê-los.

## Checklist de migração

1. Seja específico sobre o comportamento desejado e adicione modificadores de qualidade.
2. Peça animações e elementos interativos explicitamente.
3. Migre de `budget_tokens` para pensamento adaptativo mais `effort`.
4. Remova mensagens pré-preenchidas do assistente no turno final.
5. Reduza a linguagem contra preguiça e a que força o uso de ferramentas.
6. Mantenha o histórico da conversa somente com acréscimos e devolva os blocos de
   pensamento sem alterações.
7. Revise `max_tokens`. O pensamento vem ligado por padrão no Opus 5 e no Sonnet 5,
   e o tokenizador do Sonnet 5 gera cerca de 30% mais tokens para o mesmo texto.
8. Remova `temperature` / `top_p` / `top_k` no Sonnet 5 (erro 400).
