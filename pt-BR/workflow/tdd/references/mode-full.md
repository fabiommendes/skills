# Modo full

Você projeta. O tester escreve os testes, o implementer escreve o código, e os dois rodam em pipeline.

1. Projete, escreva os stubs e informe as seams e os critérios de aceitação.
2. Dê o briefing do lote 1 ao tester.
3. O tester devolve os testes. Rode-os e confirme o vermelho.
4. Dê o briefing do lote 1 ao implementer. Ao mesmo tempo, dê o briefing do lote 2 ao tester.
5. O implementer informa o resultado. Rode **só** os testes do lote 1: os testes do lote 2 já existem e estão vermelhos por design.
6. Verde → dê o briefing do lote 2 ao implementer e o do lote 3 ao tester.

O tester trabalha a partir dos seus stubs, então nunca espera o implementer. Quando um lote forçar uma mudança na API, revise os stubs e avise o tester antes de ele começar o próximo lote.

Os dois agentes continuam vivos entre os lotes.

## Briefings

O tester recebe: critérios de aceitação, os stubs da API, as seams a testar.

O implementer recebe: critérios de aceitação, os stubs da API, os arquivos no escopo.

Os mesmos critérios, dois trabalhos diferentes, nenhum raciocínio compartilhado. Essa independência é o que o modo full oferece. Quando testes e implementação se encontram sem que um tenha visto o outro, a concordância é evidência, e não coincidência.
