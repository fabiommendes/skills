---
name: principle-prove-it-works
description: "Aplique depois de concluir uma tarefa, antes de declará-la pronta. Verifique no artefato real (rode a funcionalidade, leia o valor real, inspecione o diff), não em um substituto, autorrelato ou 'it compiles.'"
disable-model-invocation: true
metadata:
  from: https://github.com/cursor/plugins/blob/main/pstack/skills/principle-prove-it-works/SKILL.md
---

# Prove que funciona

Verifique a saída de cada tarefa olhando diretamente a coisa real. Não infira a
partir de substitutos, autorrelatos ou "it compiles."

**Motivo:** Trabalho não verificado tem correção desconhecida. A verificação
indireta (datas de modificação de arquivos, frescor da saída, autorrelatos de
agentes, capturas de tela em cache) parece mais barata que a observação direta.
Agir sobre uma inferência errada custa muito mais que checar a fonte.

**Padrão:** Depois de concluir qualquer tarefa, pergunte: "como provo que isto
realmente funciona?"

Verifique a coisa real, não um substituto:
- Verifique se o processo está vivo diretamente, não por meio de estado derivado
- Leia o valor real, não uma representação em cache ou derivada
- Quando a verificação falhar, suspeite do método de observação antes de suspeitar do sistema

Código e funcionalidades:
1. Compile-o (necessário, mas não suficiente)
2. Rode-o e percorra o caminho real da funcionalidade
3. Verifique a cadeia inteira: os dados vão da entrada até a saída?
4. Em integrações, teste o caminho de comunicação completo, de ponta a ponta

Delegação: confie em artefatos, não em autorrelatos. Ao verificar trabalho
delegado, inspecione o artefato de saída real (git diff, conteúdo dos arquivos,
comportamento em execução), não o resumo do delegado. Agentes relatam o que
pretendiam, nem sempre o que aconteceu.

## Automatize a verificação quando puder

A prova mais forte é um script determinístico que refaz a mesma comparação, não
uma olhada pontual. Escreva o script, rode-o e guarde a saída como artefato que um
revisor possa rodar de novo, em vez de confiar na sua palavra. Um script que
compara a saída compilada antiga com a nova pega o que uma olhada rápida deixa
passar.

Mantenha o artefato visível para o humano. Faça commit dele só em trabalho grande
ou complexo em que o rastro precise ser auditável depois, como uma portagem grande
ou uma migração (a skill **show-me-your-work**). A maioria dos trabalhos só precisa
que o artefato fique visível, não commitado.
