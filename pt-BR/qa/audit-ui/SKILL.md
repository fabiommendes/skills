---
name: audit-ui
description: Auditoria de design visual e acessibilidade da interface de uma aplicação, cobrindo WCAG 2.2 AA (contraste, teclado e foco, semântica e rótulos, reflow e tamanho do alvo), consistência visual, hierarquia e estados dos componentes. Entregue como relatório em PDF/HTML com issues do GitHub prontas para colar. Use quando o usuário pedir uma auditoria de UI, de design visual, de design system ou de acessibilidade (a11y, WCAG).
---

# Auditoria: UI

Audite como a interface se parece e se todas as pessoas conseguem perceber e operá-la,
e entregue o relatório definido pela skill `audit-report`. Fluxos de tarefas e
usabilidade ficam com `audit-ux`.

Copie este checklist e acompanhe-o:

```
- [ ] 1. Carregar audit-report
- [ ] 2. Preparar a interface
- [ ] 3. Montar o inventário de telas
- [ ] 4. Executar as verificações automáticas de acessibilidade
- [ ] 5. Verificar cada categoria em cada tela
- [ ] 6. Sintetizar e renderizar
```

## 1. Carregar audit-report

Invoque a skill `audit-report` agora e inicie ou retome o log. Ela define como você
registra os achados conforme avança. A área é `ui`; o prefixo do título da issue é
`[UI]`.

## 2. Preparar a interface

Pergunte ao usuário como executar a aplicação em um ambiente de teste, com dados de
teste. Use as ferramentas de navegador disponíveis (Claude in Chrome, Playwright)
para ver as telas em largura de desktop e em 320 pixels CSS. Trabalhe apenas no
ambiente que o usuário indicar.

Se a interface não puder rodar, audite a partir do código (estilos, componentes,
marcação) e diga isso em `methodology`. Marque cada achado feito só a partir do
código com "a partir do código" em `conditions`.

Salve as capturas de tela dos achados em `docs/audits/ui/screenshots/`.

## 3. Montar o inventário de telas

Liste cada tela ou página e os componentes compartilhados e os tokens de design
(cores, espaçamentos, tipografia) que elas usam. Registre uma linha por tela em uma
tabela de inventário: tela, rota ou ponto de entrada, componentes compartilhados
usados, verificada em largura de desktop e de celular (sim/não).

## 4. Executar as verificações automáticas de acessibilidade

Execute uma verificação automática em cada tela do inventário:

- `npx @axe-core/cli <url>`, ou axe pelo Playwright quando o projeto o usa;
- senão, `npx lighthouse <url> --only-categories=accessibility --output=json`.

Registre cada violação confirmada como achado. Verificações automáticas encontram só
parte das falhas de WCAG; as categorias 2 e 3 precisam das verificações manuais
abaixo.

## 5. Categorias

### 1. Cor e contraste (`contrast`)

Contraste de texto de pelo menos 4,5:1, ou 3:1 para texto grande (WCAG 1.4.3); 3:1
para bordas de controles, indicadores de foco e gráficos com significado (1.4.11);
informação que não depende só da cor (1.4.1).

### 2. Teclado e foco (`keyboard`)

Toda ação alcançável e operável pelo teclado (2.1.1), sem armadilhas de teclado
(2.1.2), uma ordem de foco lógica (2.4.3), um indicador de foco visível (2.4.7) que
não fique oculto por cabeçalhos fixos ou sobreposições (2.4.11), e o foco movido para
dentro de diálogos e devolvido ao fechá-los. Verifique navegando com Tab em cada tela.

### 3. Semântica e rótulos (`semantics`)

Textos alternativos para imagens com significado e botões só com ícone (1.1.1),
rótulos ligados a cada campo de formulário (3.3.2), elementos nativos ou papéis,
nomes e estados corretos para controles personalizados (4.1.2), títulos e marcos que
refletem a estrutura (1.3.1), e erros anunciados às tecnologias assistivas.

### 4. Layout e responsividade (`responsive`)

Conteúdo utilizável em 320 pixels CSS de largura sem rolagem horizontal (1.4.10) e
com texto em 200% (1.4.4), alvos de toque de pelo menos 24 por 24 pixels CSS (2.5.8),
e nenhum estouro ou corte com textos longos, nomes longos ou traduções.

### 5. Consistência visual (`consistency`)

Tokens de design usados no lugar de cores, tamanhos e espaçamentos fixos no código;
um componente para cada função, em vez de várias variantes do mesmo botão ou card;
uma escala tipográfica, de espaçamento e um conjunto de ícones consistentes.

### 6. Hierarquia visual (`hierarchy`)

Uma ação primária clara por tela, agrupamento e alinhamento que mostrem o que pertence
junto, e densidade que deixa o conteúdo principal se destacar.

### 7. Estados dos componentes (`states`)

Estados de hover, foco, ativo, desabilitado, carregando, vazio e erro projetados para
cada componente interativo e cada visão de dados, em vez de áreas em branco ou
controles travados.

### 8. Movimento e temas (`motion-theme`)

Animações reduzidas ou removidas sob `prefers-reduced-motion`, nada que pisque, e
conteúdo em movimento que possa ser pausado (2.2.2). Quando a aplicação oferece tema
escuro ou de alto contraste, cada tela e cada estado são verificados nele.

## Severidade

| Nível | Significado |
|---|---|
| `critical` | Algumas pessoas não conseguem usar um fluxo primário: uma armadilha de teclado, controles sem rótulo em uma tarefa primária, ou texto ilegível. |
| `high` | Uma falha de WCAG 2.2 AA em um fluxo primário, ou um layout quebrado em uma largura de tela comum. |
| `medium` | Uma falha de WCAG 2.2 AA em uma tela secundária, ou inconsistências que fazem o mesmo elemento parecer diferente de uma tela para outra. |
| `low` | Uma inconsistência só estética. |
| `info` | Uma observação ou ideia de melhoria, sem problema atual. |

## 6. Sintetizar e renderizar

Registre as oito categorias, os achados e os pontos fortes conforme `audit-report`
define, escreva a síntese e renderize. Para cada achado, coloque a tela e o elemento
em `location`, o critério de sucesso do WCAG em `title` quando se aplicar, o
`file:line` do componente em `fix` quando você o encontrou no código, e uma captura
de tela em `screenshot`.
