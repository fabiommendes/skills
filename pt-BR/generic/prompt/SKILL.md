---
name: prompt
description: Fluxo de trabalho para prompts eficazes. Defina tarefas mais assertivas antes de acionar o agente.
disable-model-invocation: true
argument-hint: "What should I do now?"
---

# Prompts com Claude

Este é um fluxo de trabalho que ajuda a preparar prompts mais eficazes ao usar o Claude.

1. Você produz um arquivo de prompt modelo (que pode ser genérico ou baseado no contexto da conversa).
2. Um humano edita este arquivo com os detalhes necessários.
3. Você ou outro agente usa o arquivo de prompt atualizado para continuar a tarefa.


## Local do arquivo

O destino do arquivo de prompt é escolhido entre as opções a seguir (nesta ordem).

1. `prompts/<title>.md` se o humano forneceu algum contexto. O título é um slug que resume o pedido do humano. Não sobrescreva arquivos existentes.
2. Um arquivo `prompt.md` na raiz do projeto, se ele não existir.
3. Se o arquivo existir, peça contexto ao humano e aplique a primeira regra.


## Modelo

A estrutura básica de um arquivo de prompt é a seguinte:

```md
<instructions>
  Describe the final outcome of what you want Claude to do.
</instructions>

<why>
  Explain the reasons for the job, since it helps guide reasoning and 
  decision-making for Claude.
</why>

<examples>
  Examples help guide desired behavior and expectations.

  Put each <example> tag under a <examples> block if there is more than one example.
</examples>

<document>
  If there are any relevant documents or references, include them here.

  Put each <document> tag under a <document> block if there is more than one document.
</document>

<strategy>
  Include any reasoning or thought process that Claude should follow.
</strategy>

<constraints>
  Specify any rules, constraints, or guidelines that Claude should follow during 
  the task. E.g, "only modify some specific file(s)". "do not change backend code".
</constraints>

<done_means>
  Tell the acceptance criteria for the task.
</done_means>
```

Se o humano tiver fornecido algum contexto, você pode trocar o texto de exemplo
por frases curtas, mais relevantes para a tarefa em questão.

## O que informar?

Depois de criar o arquivo, informe apenas o local, assim:

```
Prompt file created at `<full_path_to_prompt_file>`.
```

O humano provavelmente vai editar o arquivo de prompt com detalhes. Mostre uma
mensagem de confirmação perguntando se o humano quer continuar a tarefa. Se sim,
releia o arquivo com o conteúdo atualizado e prossiga como se fosse o primeiro
prompt dado na conversa.

Quando a tarefa terminar, confirme com o humano se o `<prompt_file>` deve ser
apagado e apague-o se o humano confirmar.
