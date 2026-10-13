---
name: do
description: Executa prompts criados externamente pelo usuário.
disable-model-invocation: true
argument-hint: Path to the prompt file to execute.
---

# Skill Do

Usuários às vezes preferem escrever prompts complexos em um editor de texto antes
de enviá-los ao agente. Esta skill simples encontra e executa esses prompts
escritos externamente.

## Local do prompt

Procure um arquivo de prompt nesta ordem:

1. O argumento que o usuário informou ao chamar a skill.
2. Um arquivo `prompt.txt` ou `prompt.md` no diretório de trabalho atual.
3. Um arquivo no diretório `prompts` dentro do diretório de trabalho atual. Se
   houver mais de um arquivo, mostre uma lista numerada de opções e peça ao
   humano que escolha uma.

Se todas essas tentativas falharem, sugira ao humano usar a skill `/prompt` para
criar um novo arquivo de prompt e encerre.

## Execução

Leia o conteúdo inteiro do arquivo de prompt e peça confirmação ao humano. O
humano já conhece o conteúdo do prompt, então dê apenas algumas palavras-chave
para confirmação. Exemplo: `Should I write the Login component?`

Se o humano confirmar, execute o prompt como se ele tivesse sido digitado
diretamente ao agente.
