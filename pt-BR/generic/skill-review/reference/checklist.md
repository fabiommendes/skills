# Rubrica de revisão de skills

Condensada das boas práticas de criação de skills da Anthropic. Cada item é uma
verificação a fazer na skill revisada, com a assinatura de falha a procurar.

## Sumário

- Frontmatter e descoberta
- Concisão
- Estrutura e divulgação progressiva
- Fluxos de trabalho e ciclos de feedback
- Diretrizes de conteúdo
- Scripts e código executável
- Avaliações

## Frontmatter e descoberta

- **`name` é válido.** Apenas letras minúsculas, números e hífens; máximo de 64
  caracteres; sem tags XML; não pode conter as palavras reservadas `anthropic` ou
  `claude`.
- **`name` corresponde ao diretório.** Divergência quebra o carregamento.
- **`name` é descritivo.** Gerúndio (`processing-pdfs`) ou locução nominal
  (`pdf-processing`) funcionam. Reprove `helper`, `utils`, `tools`, `data`,
  `files`.
- **`description` não está vazio e tem menos de 1.024 caracteres.**
- **`description` diz o que a skill faz *e* quando usá-la.** Uma oração para a
  capacidade e uma começando com `Use when…` para o gatilho.
- **`description` está em terceira pessoa.** Reprove "I can help you…" e "You can
  use this to…"; um ponto de vista inconsistente prejudica a descoberta.
- **`description` traz os termos-chave que um usuário realmente digitaria.**
  Extensões de arquivo, nomes de ferramentas, substantivos do domínio. Reprove
  "Helps with documents."
- **Sem tags XML em `name` ou `description`.**

## Concisão

- **Cada parágrafo se justifica pelos tokens que consome.** Corte tudo que
  explica o que um modelo competente já sabe: o que é um PDF, o que é uma
  biblioteca, o que é HTTP.
- **Não repetir o pedido ao modelo.** Instruções, não preâmbulo.
- **Sem conteúdo duplicado** entre SKILL.md e os arquivos auxiliares.

## Estrutura e divulgação progressiva

- **O corpo do SKILL.md tem menos de 500 linhas.** Acima do limite, o conteúdo
  deve ir para arquivos auxiliares.
- **Referências têm um nível só.** O SKILL.md pode linkar `reference/guide.md`;
  `reference/guide.md` não pode levar o leitor a um terceiro arquivo. Referências
  aninhadas são lidas parcialmente.
- **Todo arquivo auxiliar é linkado no SKILL.md.** Arquivo sem referência é peso
  morto: o modelo nunca o abrirá.
- **Arquivos auxiliares têm nomes que refletem o conteúdo.**
  `form-validation-rules.md`, não `doc2.md`.
- **Arquivos de referência com mais de 100 linhas abrem com um sumário**, para que
  uma leitura parcial ainda revele o escopo completo.
- **A divisão é por domínio, não por tamanho.** Arquivos separados devem
  corresponder a situações separadas, para que só o relevante seja carregado.

## Fluxos de trabalho e ciclos de feedback

- **Procedimentos com várias etapas são passos numerados**, não prosa.
- **Fluxos complexos trazem uma checklist copiável** que o agente pode acompanhar.
- **Os passos dizem a ação de forma concreta**: o comando exato, o arquivo exato a
  editar, em vez de descrever o objetivo.
- **Tarefas críticas para a qualidade têm ciclo de validação:** produzir →
  verificar → corrigir → verificar de novo, com a instrução explícita "only
  proceed when it passes".
- **Pontos de decisão são explícitos.** "Creating new content? → creation
  workflow. Editing? → editing workflow."
- **O grau de liberdade combina com a tarefa.** Operações frágeis e dependentes de
  ordem recebem comandos exatos; tarefas abertas de julgamento recebem direção e
  margem. Aponte qualquer uma das divergências.

## Diretrizes de conteúdo

- **Sem informação sensível ao tempo.** Reprove "before August 2025, use the old
  API." Material obsoleto vai numa seção "Old patterns", de preferência dentro de
  um bloco `<details>` recolhido.
- **Terminologia consistente.** Um termo por conceito em todo o texto: não
  "field", "box", "element" e "control" para a mesma coisa.
- **Exemplos são concretos.** Pares reais de entrada e saída valem mais que
  descrições do que seria uma boa saída.
- **Modelos de saída estão presentes onde o formato importa**, com o rigor
  declarado ("use this exact structure" versus "a sensible default").
- **Uma abordagem recomendada, não um menu.** "Use pdfplumber", com uma saída
  nomeada para a exceção, e não "you could use pypdf, or pdfplumber, or PyMuPDF."
- **Ferramentas MCP usam nomes totalmente qualificados** na forma
  `ServerName:tool_name`.
- **Caminhos usam barras normais.** `scripts/helper.py`, nunca `scripts\helper.py`.

## Scripts e código executável

Pule esta seção em skills só de markdown.

- **Scripts resolvem, não adiam.** Eles tratam o caso de erro sozinhos, em vez de
  falhar e deixar o agente descobrir o que fazer.
- **Mensagens de erro são acionáveis.** "Field 'signature_date' not found.
  Available fields: …" é melhor que um traceback puro.
- **Sem constantes mágicas.** Cada valor ajustado tem um comentário que o
  justifica. Se o autor não consegue explicar o número, o agente também não
  consegue.
- **Dependências são declaradas** e disponíveis no ambiente de execução. Reprove
  "use the pdf library" sem uma linha de instalação.
- **A intenção de execução é inequívoca.** "Run `analyze_form.py`" (executar)
  versus "See `analyze_form.py` for the algorithm" (ler). A ambiguidade desperdiça
  contexto.
- **Trabalho determinístico é um script**, não um prompt pedindo ao agente que
  gere o mesmo código toda vez.
- **Operações em lote ou destrutivas produzem um artefato intermediário
  verificável**: um arquivo de plano que um validador confere antes de qualquer
  aplicação.

## Avaliações

- **Existem pelo menos três cenários de avaliação**, cada um nomeando a consulta,
  eventuais arquivos de entrada e o comportamento esperado.
- **Os cenários miram lacunas observadas de verdade**, não imaginadas.
- **A skill foi testada em uma tarefa real**, não apenas lida.
- **O comportamento se mantém nos modelos em que vai rodar.** Instruções ajustadas
  para um modelo grande podem ser insuficientes para um modelo pequeno.
