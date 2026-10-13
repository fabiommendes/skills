# Modo default

Você projeta e escreve os testes. O implementer escreve o código.

1. Projete, escreva os stubs e informe as seams e os critérios de aceitação.
2. Escreva você mesmo os testes do lote.
3. Rode-os e confirme o vermelho.
4. Crie ou envie mensagem ao implementer com: os critérios de aceitação em texto corrido, os stubs da API e os arquivos no escopo. Nunca envie o código de teste, nem um resumo de como os testes são estruturados.
5. O implementer informa o resultado. Rode os testes do lote.
6. Verde → próximo lote, com o mesmo implementer.

Este é o modo mais forte. É o único que tem uma fase de vermelho de verdade e um implementer cego ao mesmo tempo, e custa um agente só. Use-o, a não ser que a escrita dos testes seja grande o bastante para merecer um agente próprio.
