---
name: audit-ux
description: Auditoria de usabilidade dos fluxos de usuário de uma aplicação, com percursos de tarefas e as heurísticas de Nielsen, cobrindo conclusão de tarefas, feedback, prevenção e recuperação de erros, consistência e ajuda. Entregue como relatório em PDF/HTML com issues do GitHub prontas para colar. Use quando o usuário pedir uma auditoria de UX ou de usabilidade, ou quiser descobrir onde os usuários travam, ficam confusos ou perdem trabalho.
---

# Auditoria: UX

Audite como os usuários conseguem realizar suas tarefas, e entregue o relatório
definido pela skill `audit-report`. Esta auditoria trata de comportamento e fluxo:
o que o usuário precisa fazer, entender e lembrar. Design visual e acessibilidade
ficam com `audit-ui`.

Copie este checklist e acompanhe-o:

```
- [ ] 1. Carregar audit-report
- [ ] 2. Preparar a interface
- [ ] 3. Montar o inventário de tarefas
- [ ] 4. Percorrer cada tarefa
- [ ] 5. Verificar cada heurística
- [ ] 6. Sintetizar e renderizar
```

## 1. Carregar audit-report

Invoque a skill `audit-report` agora e inicie ou retome o log. Ela define como você
registra os achados conforme avança. A área é `ux`; o prefixo do título da issue é
`[UX]`.

## 2. Preparar a interface

Pergunte ao usuário como executar a aplicação em um ambiente de teste, com dados de
teste, e quem são os seus usuários. Use as ferramentas de navegador disponíveis
(Claude in Chrome, Playwright) para interfaces web, e o terminal para ferramentas de
linha de comando. Trabalhe apenas no ambiente que o usuário indicar.

Se a interface não puder rodar, audite a partir do código (rotas, componentes,
textos, validação) e diga isso em `methodology`. Marque cada achado feito só a partir
do código com "a partir do código" em `conditions`.

Salve as capturas de tela dos achados em `docs/audits/ux/screenshots/`.

## 3. Montar o inventário de tarefas

Liste as tarefas que os usuários vêm fazer, a partir da navegação, das rotas, da
documentação e da descrição do usuário: criar conta, criar o objeto principal,
encontrar algo, mudar configurações, recuperar a senha. Marque cada uma como
primária ou secundária. Registre uma linha por tarefa em uma tabela de inventário:
tarefa, primária ou secundária, ponto de entrada, número de passos, concluída (sim,
com contorno, não).

## 4. Percorrer cada tarefa

Execute cada tarefa como um usuário na primeira vez faria. A cada passo, pergunte:

1. O usuário vai saber o que fazer em seguida para chegar ao objetivo?
2. Ele vai ver o controle que faz isso?
3. Ele vai entender que esse controle faz o que ele quer?
4. Depois de agir, ele vai ver que funcionou?

Um "não" a qualquer pergunta é um achado. Depois, repita a tarefa cometendo erros
típicos: entrada inválida ou vazia, voltar, cancelar no meio, recarregar, clicar
duas vezes em enviar, abrir a mesma página em duas abas.

## 5. Categorias

Associe cada achado à categoria que ele viola. A primeira trata de tarefas inteiras;
as demais são as dez heurísticas de usabilidade de Nielsen.

1. **Conclusão de tarefas (`tasks`):** becos sem saída, passos que exigem informação
   de outro lugar, fluxos que perdem a entrada do usuário, tarefas com muito mais
   passos do que o necessário.
2. **Visibilidade do estado do sistema (`status`):** feedback após ações, progresso
   em operações lentas, local e estado atuais.
3. **Correspondência com o mundo real (`language`):** palavras dos usuários no lugar
   de termos internos ou técnicos, ordem natural da informação.
4. **Controle e liberdade do usuário (`control`):** desfazer, cancelar, voltar sem
   perder trabalho, sair de estados indesejados.
5. **Consistência e padrões (`consistency`):** a mesma ação com o mesmo nome e no
   mesmo lugar em todo o sistema, convenções da plataforma seguidas.
6. **Prevenção de erros (`error-prevention`):** restrições e padrões que evitam
   erros, confirmação antes de ações destrutivas.
7. **Reconhecimento em vez de memorização (`recognition`):** opções e informações
   visíveis quando necessário, em vez de memorizadas de uma tela anterior.
8. **Flexibilidade e eficiência (`efficiency`):** atalhos, ações em lote e escolhas
   lembradas para usuários frequentes.
9. **Conteúdo focado (`minimalism`):** cada tela mostra o que a tarefa precisa;
   informação secundária não compete com ela.
10. **Recuperação de erros (`error-recovery`):** mensagens de erro em linguagem
    simples que dizem o que deu errado e como corrigir, com a entrada do usuário
    mantida.
11. **Ajuda e documentação (`help`):** ajuda onde o usuário precisa dela, orientada a
    tarefas e fácil de encontrar.

## Severidade

| Nível | Significado |
|---|---|
| `critical` | O usuário não consegue concluir uma tarefa primária, ou perde dados ou trabalho. |
| `high` | Uma tarefa primária só funciona com um contorno ou após muita confusão, ou uma tarefa secundária não pode ser concluída. |
| `medium` | O usuário fica bem mais lento ou confuso, ou um problema pequeno se repete em muitas telas. |
| `low` | Um incômodo pequeno ou raro. |
| `info` | Uma observação ou ideia de melhoria, sem problema atual. |

## 6. Sintetizar e renderizar

Registre as onze categorias, os achados e os pontos fortes conforme `audit-report`
define, escreva a síntese e renderize. Para cada achado, coloque a tela ou a rota e
os passos para reproduzir em `location` e `description`, o `file:line` do componente
em `fix` quando você encontrou a causa no código, e a captura de tela em
`screenshot`.
