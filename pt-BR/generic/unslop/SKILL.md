---
name: unslop
description: Remove marcas de IA de qualquer texto. Deve sempre ser aplicada.
---

# Unslop

Edite o texto para remover padrões de IA e acrescentar voz humana.

## Processo

1. Procure os padrões abaixo.
2. Reescreva. Preserve o sentido e mantenha o tom pretendido.
3. Acrescente personalidade (veja a próxima seção).
4. Auto-auditoria: "What makes this obviously AI generated?" Corrija as marcas restantes.

## Acrescentando personalidade

Remover padrões é metade do trabalho. Texto estéril e sem voz é igualmente óbvio.

- **Tenha opiniões.** Reaja aos fatos em vez de listar prós e contras de forma neutra.
- **Varie o ritmo.** Frases curtas. Depois frases mais longas, que se demoram. Misture.
- **Reconheça a complexidade.** "Impressive but also kind of unsettling" é melhor que "impressive."
- **Use "I" ou "We" quando couber.** Primeira pessoa não é falta de profissionalismo.
- **Deixe um pouco de bagunça.** Estrutura perfeita parece feita por máquina.
- **Seja específico.** Não "this is concerning", mas "there's something unsettling about agents churning away at 3am."

## Padrões a detectar e corrigir

### Conteúdo

1. **Exagero vazio.** "pivotal moment", "testament to", "evolving landscape", "setting the stage for", "indelible mark", "deeply rooted". Corte o exagero e diga o que aconteceu.
2. **Citação de nomes.** Listar veículos de imprensa sem contexto. Escolha um e diga o que foi dito.
3. **Frases superficiais em -ing.** "highlighting...", "ensuring...", "reflecting...", "showcasing...", "fostering...". Apague ou expanda com fontes reais.
4. **Linguagem promocional.** "nestled", "vibrant", "breathtaking", "groundbreaking", "renowned", "stunning", "must-visit". Use descrições neutras.
5. **Atribuições vagas.** "Experts believe", "Industry reports suggest", "Some critics argue". Nomeie a fonte ou apague.
6. **Desafios em fórmula.** "Despite challenges... continues to thrive." Troque por fatos específicos.

### Linguagem

7. **Vocabulário de IA.** Additionally, crucial, delve, enduring, enhance, fostering, garner, interplay, intricate, landscape (abstract), pivotal, showcase, tapestry (abstract), testament, underscore, vibrant. Troque por palavras simples.
8. **Formas rebuscadas de dizer "is".** "serves as", "stands as", "boasts", "features". Diga apenas "is" ou "has".
9. **"Not just X, but Y."** Diga o ponto diretamente.
10. **Regra dos três.** Forçar ideias em grupos de três. Use o número natural.
11. **Rodízio de sinônimos.** Protagonist, main character, central figure, hero no mesmo parágrafo. Escolha um e repita-o.
12. **Intervalos falsos.** "from X to Y" em que X e Y não estão em uma escala significativa. Liste os tópicos diretamente.

### Estilo

13. **Excesso de travessão.** Evite travessões por completo. Use apenas pontos ou vírgulas (sem parênteses, sem travessões en, sem hífen no lugar de travessão). Travessões são marca de IA, e trocá-los por parênteses apenas troca uma marca por outra. Se um pensamento precisa de separação, encerre a frase ou use vírgula.
14. **Excesso de dois-pontos.** Dois-pontos são aceitáveis antes de uma lista ou de um exemplo. Não os use como conectores no meio da frase. "If you're coming from traditional automation: instead of registering event handlers, you describe conditions" não ganha nada com os dois-pontos. Reescreva para que o ponto se sustente sozinho, sem enquadramento de comparação. "Describing when the scheduler should fire works best as plain English." Mesmo sentido, sem pontuação muleta.
15. **Excesso de negrito.** Não coloque em negrito todo nome próprio ou sigla.
16. **Listas com cabeçalho na linha.** O sinal é um rótulo em negrito com dois-pontos que repete a linha: "**Performance:** Performance improved...". Converta isso em prosa. Um início em negrito que termina em ponto, nomeia o item e é seguido de um detalhe realmente novo ("**Schema in TypeScript.** Tables live in one file.") é aceitável, não é marca.
17. **Capitalização de título.** Use maiúscula só na primeira palavra.
18. **Emojis decorativos.** Remova de títulos e marcadores.
19. **Aspas curvas.** Troque por aspas retas.

### Artefatos de comunicação

20. **Frases de chatbot.** "I hope this helps!", "Let me know if...", "Of course!", "Certainly!", "Found the smoking gun!" Remova.
21. **Ressalvas de corte.** "While specific details are limited..." Encontre fontes ou remova.
22. **Tom bajulador.** "Great question! You're absolutely right!" Responda diretamente.
24. **Ressalvas com travessão.** "— but this is just my opinion." Remova. Se é sua opinião, diga isso diretamente.

### Enchimento

25. **Frases de enchimento.** "In order to" vira "To". "Due to the fact that" vira "Because". "It is important to note that" é apagada.
26. **Ressalvas em excesso.** "could potentially possibly be argued that it might" vira "may".
27. **Conclusões genéricas.** "The future looks bright." Diga planos ou fatos específicos.

### Jargão

28. **Substantivos metafóricos abstratos.** Substrate, wedge, vector, locus, vantage, nexus, primitive (as noun), harness (as metaphor), surface (as in "API surface"), bedrock, scaffolding (as metaphor), modality, paradigm, gold-plating, ratchet (as metaphor), evacuate (for moving code), endgame, north star, flywheel. Parecem técnicos, mas geralmente têm uma palavra concreta mais simples. "Substrate" vira "base". "Wedge in" vira "add". "Vector" vira "way" ou "method". "Gold-plating" vira "more than the job needs". "Ratchet" vira o nome real do mecanismo ou "a limit that only tightens". "Evacuate" vira "move out". "Endgame" vira "the last phase". Escolha a palavra concreta.

### Linguagem simples

29. **Diga o que faz, não como se sente.** "the database stays close at hand", "SQL you can read", "types that follow your schema" nomeiam um sentimento. A correção nomeia o mecanismo ou um número: "`.toSQL()` returns the exact string sent to the database", "a column rename fails the build". Pergunte o que a frase diz ao leitor para fazer ou saber, e escreva isso. Se não der para reescrevê-la como uma instrução, um fato ou um número concretos, corte-a. Mais uma verificação: se a frase poderia aparecer sem mudança na documentação de outro projeto, ela não diz nada sobre este. Corte-a.
30. **Encurte ou divida frases densas.** Se o leitor precisar voltar para entender uma frase, divida-a em duas ou remova orações. Uma ideia por frase.
31. **Voz ativa.** Prefira-a. Identifique "is/are/was/were + past participle" e nomeie o agente: "queries are validated" vira "the compiler validates queries", "the file is parsed by the loader" vira "the loader parses the file". A voz passiva só serve quando o agente é desconhecido ou realmente não importa.
32. **Corte advérbios ou use um verbo mais forte.** "runs quickly" vira "is fast" ou o número. "significantly improves" vira a variação medida. Um advérbio sustentando um verbo fraco indica que o verbo está errado.
33. **Prefira a palavra simples.** "utilize" vira "use", "leverage" vira "use", "facilitate" vira "help", "numerous" vira "many", "in the event that" vira "if". O sinônimo mais rebuscado raramente é mais claro.
