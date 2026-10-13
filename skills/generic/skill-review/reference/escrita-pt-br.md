# Regras de escrita para skills em português

Não existe uma língua controlada oficial para o português. Estas regras
adaptam as regras de escrita do ASD-STE100 (Simplified Technical English,
edição 8, 2021) ao português. Elas também seguem os princípios da ABNT NBR ISO
24495-1:2024 (Linguagem Simples): o leitor encontra, entende e usa a
informação.

## Palavras

- Use uma palavra para um significado e um significado para cada palavra. Se
  a skill diz "achado", ela não diz "problema" ou "falha" para a mesma coisa.
- Use a palavra mais simples e comum. Escreva "usar", não "utilizar";
  "começar", não "iniciar"; "mostrar", não "evidenciar".
- Nomes técnicos são permitidos: nomes de ferramentas, arquivos,
  identificadores de código e termos do glossário do projeto. Coloque código e
  caminhos entre crases.
- Mantenha em inglês o termo técnico que não tem tradução comum: "commit",
  "merge", "frontmatter", "hook". Não invente tradução.
- Junte no máximo três substantivos. Escreva "o tempo limite do tratador da
  requisição", não "o valor do tempo limite do tratador da requisição HTTP do
  servidor".

## Verbos

- Use a voz ativa. Escreva "o agente lê o arquivo", não "o arquivo é lido" nem
  "lê-se o arquivo".
- Use os tempos simples: presente, pretérito perfeito, futuro. Não use
  gerúndio ("estou lendo", "vai estar verificando"). Escreva "o agente lê".
- Use o imperativo nas instruções: "Leia o arquivo.", não "Você deve ler o
  arquivo." nem "É necessário ler o arquivo.".
- Não esconda a ação num substantivo. Escreva "verifique a configuração", não
  "faça a verificação da configuração".

## Frases

- Instruções: no máximo 20 palavras por frase. Uma instrução por frase, a não
  ser que duas ações aconteçam ao mesmo tempo.
- Descrições: no máximo 25 palavras por frase. Um assunto por frase.
- Parágrafos: no máximo 6 frases, um assunto por parágrafo.
- Ponha a condição primeiro: "Se o teste falhar, pare.", não "Pare se o teste
  falhar.".
- Ponha o aviso antes da instrução a que ele se aplica, nunca depois.
- Use "não" para proibições. Diga o que fazer no lugar quando não for óbvio.
- Prefira a ordem direta: sujeito, verbo, complemento.

## Estrutura

- Use passos numerados para procedimentos e marcadores para itens sem ordem.
- Use tabelas para dados com mais de dois atributos.
- Use uma lista vertical no lugar de uma frase longa com muitas vírgulas.

## Fora do STE

Estas regras vêm da escrita de skills, não do STE:

- Escreva para um agente que conhece o domínio. Não explique o que é comum.
- Dê o motivo de uma regra quando o motivo muda a forma de aplicá-la.
- Use exemplos para mostrar um padrão e diga qual parte do exemplo importa.
