---
name: principle-subtract-before-you-add
description: "Aplique ao sequenciar uma adição, refatoração ou reescrita. Remova peso morto, validadores redundantes e referências vazias primeiro, depois construa sobre a base mais simples."
disable-model-invocation: true
metadata:
  from: https://github.com/cursor/plugins/blob/main/pstack/skills/principle-subtract-before-you-add/SKILL.md
---

# Subtraia antes de adicionar

Ao evoluir um sistema, remova a complexidade primeiro e depois construa. A remoção
dá uma base mais simples, o que torna a próxima adição menor e menos frágil.

**Motivo:** Adicionar a um sistema complexo multiplica a complexidade. Remover
primeiro reduz a superfície, revela a estrutura essencial e geralmente torna óbvio
o próximo desenho. Adote a subtração como padrão.

Trate a simplificação como investimento contínuo. Deixe o desenho um pouco mais
simples e mais capaz, com a mesma superfície ou uma menor do que encontrou.

**O padrão:**
- Faça a remoção antes da construção
- Corte antes de polir (chegue ao mínimo antes de investir em qualidade)
- Projete para o uso observado, não para casos de borda especulativos
- Nada de validadores, parsers ou guardas especulativos além do que a especificação exige
- Funcionalidades fora da especificação arrastam validadores atrás de si. Persistência,
  nova tentativa na inicialização e migração de esquema exigem, cada uma, guardas para
  proteger suas entradas.
- Simplifique prompts (remova instruções redundantes e modelos excessivos)
- Quando uma referência não tem conteúdo novo, apague-a em vez de deixar um esboço
