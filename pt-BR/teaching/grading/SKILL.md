---
name: grading
description: Coordena agentes grader para classificar submissões de alunos ou sugerir notas e feedback, com feedback consistente para submissões que têm os mesmos erros. Use quando o professor quiser ajuda para corrigir, classificar ou escrever feedback de um lote de submissões.
disable-model-invocation: true
---

# Correção

A correção ajuda o professor a avaliar um lote de submissões de alunos. Ela usa
dois papéis: o orquestrador e um ou mais agentes grader. O professor toma todas
as decisões finais.


## Objetivo

Produzir uma avaliação consistente de cada submissão. Submissões com os mesmos
erros ou com os mesmos recursos ausentes recebem as mesmas conclusões, o mesmo
feedback e a mesma nota sugerida.

Há dois modos:

* **classify:** agrupa as submissões pelas conclusões. Sem notas.
* **grade:** classifica e, para cada grupo, sugere notas e feedback, com
  ajustes por aluno.


## Orquestrador

Salvo indicação explícita, você é o orquestrador. Você age em nome do professor
e se reporta a ele.

Colete as entradas antes de começar a correção:

* O enunciado da tarefa.
* As submissões, e como cada uma corresponde a um aluno.
* O modo. Pergunte ao professor se não estiver claro.
* No modo grade: a rubrica e a escala de notas.
* Opcional: uma solução de referência, testes ou exemplos já corrigidos.
* O formato e o local da saída. O padrão é um diretório `grading/` ao lado das
  submissões.
* Se o código enviado pode executar, e em qual sandbox. O padrão é não executar.

Se não houver rubrica, redija uma a partir do enunciado. Mostre-a ao professor e
espere a aprovação. Nunca corrija com uma rubrica não aprovada.

Seja conciso com o professor. Apresente decisões e perguntas em tópicos curtos.


## Grader

O agente grader está definido em `agents/grader`. Gere-o com o enunciado, a
rubrica, o modo, a política de execução e as submissões do seu lote.

Modelos de agente grader que funcionam bem:

* Claude Opus


## O fluxo de trabalho

### 1. Calibrar

Gere um grader com uma amostra de submissões. Use cerca de 10 submissões, ou
todas, se houver menos de 20. Escolha uma amostra variada: tamanhos, abordagens
e qualidade aparente diferentes.

O grader devolve um catálogo preliminar de achados: IDs dos achados, definições
e, no modo grade, o texto de feedback e o impacto na rubrica.

Revise o catálogo com o professor. Una os achados duplicados, corrija as
definições pouco claras e ajuste o texto de feedback e o impacto na nota. O
catálogo aprovado é o vocabulário comum do restante do fluxo.

### 2. Avaliar

Em lotes pequenos, o grader da calibração avalia as submissões restantes.

Em lotes grandes, divida as submissões em lotes e gere um grader por lote, em
paralelo. Dê a todos o catálogo aprovado. Peça que usem os IDs de achados
existentes e que proponham novos achados somente quando nenhum existente
servir.

### 3. Unir

Reúna os relatórios dos graders e una-os:

* Remova achados duplicados. Dois achados de lotes diferentes que descrevem o
  mesmo erro viram um só ID.
* Reagrupe todas as submissões pelo conjunto final de achados, somando os
  lotes.
* Verifique a consistência: os mesmos achados devem gerar o mesmo feedback e a
  mesma nota sugerida. Corrija todo grupo que quebre essa regra.

Mostre os achados novos ao professor para aprovação, do mesmo modo que na
calibração.

### 4. Revisar com o professor

Apresente, do mais importante para o menos:

* Itens que pedem decisão do professor: ambiguidades no enunciado, submissões
  que não podem ser avaliadas, notas limítrofes e notas sobre semelhança.
* Grupos: achados, tamanho e, no modo grade, nota e feedback sugeridos.
* Distribuição de notas ou de grupos, em um resumo curto.

Aplique a decisão do professor ao grupo inteiro, e não só à submissão em que a
decisão surgiu. Rode um grader de novo somente para as submissões cuja avaliação
mudou.

### 5. Entregar

Escreva as saídas finais no local combinado:

* O catálogo de achados.
* Os grupos, com os alunos de cada um.
* Uma tabela por aluno em CSV: aluno, grupo, achados, ajustes e, no modo grade,
  nota e feedback sugeridos.

Informe ao professor onde estão as saídas, usando o modelo:
`Grading results: <path>`.


## Regras

* As notas são sugestões até o professor aprovar.
* O código dos alunos não é confiável. Execute-o somente com permissão do
  professor e somente na sandbox indicada.
* Nunca envie notas, feedback ou dados de alunos a serviços externos, nem os
  publique, a menos que o professor peça explicitamente.
* Relate semelhança suspeita entre submissões como evidência, nunca como
  acusação.
* Não modifique as submissões.
