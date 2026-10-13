---
name: audit-webserver
description: Auditoria de segurança de uma base de código de aplicação web ou API inteira, cobrindo isolamento entre tenants, autorização em nível de função e de propriedade (atribuição em massa), IDOR, autenticação, injeção, XSS, SSRF, CSRF/CORS, segredos, limites de recursos e configuração de segurança. Entregue como relatório em PDF/HTML com issues do GitHub prontas para colar. Use quando o usuário pedir uma auditoria ou revisão de segurança de uma aplicação web, API ou backend.
---

# Auditoria: servidor web

Audite a base de código de uma aplicação web em busca de falhas de segurança e entregue
o relatório definido pela skill `audit-report`. Esta é uma auditoria da base inteira;
para revisar uma única mudança ou um pull request, use o agente `security-reviewer`.
Dependências vulneráveis ficam com `audit-dependencies`.

Trabalhe a partir do código. A evidência da leitura do código basta para cada achado;
não envie payloads de exploração a um servidor em execução, a menos que o usuário peça
e indique um ambiente de teste.

Copie este checklist e acompanhe-o:

```
- [ ] 1. Carregar audit-report
- [ ] 2. Detectar a stack
- [ ] 3. Montar o inventário de rotas
- [ ] 4. Verificar cada categoria
- [ ] 5. Sintetizar e renderizar
```

## 1. Carregar audit-report

Invoque a skill `audit-report` agora e inicie ou retome o log. Ela define como você
registra os achados conforme avança. A área é `webserver`; o prefixo do título da
issue é `[Security]`.

## 2. Detectar a stack

Identifique a linguagem, o framework, o ORM ou query builder, o mecanismo de
autenticação, o frontend e os arquivos de deploy (Docker, CI, Helm, Terraform). Associe
cada categoria abaixo ao equivalente da stack e registre o mapeamento em `methodology`.
Quando uma categoria não se aplicar, como XSS em um projeto sem frontend, marque-a como
não aplicável com o motivo, em vez de forçar um achado.

## 3. Montar o inventário de rotas

Liste toda rota que o servidor registra: método, caminho, `file:line` do handler,
autenticação exigida, papel ou permissão verificada, e checagem de posse ou de tenant.
Encontre as rotas onde o framework as registra, não por amostragem de arquivos: chamadas
de router e decorators no código, ou o arquivo de especificação para frameworks
spec-first (`operationId` do OpenAPI no Connexion, configurações de API gateway). Conte
os registros para confirmar que o inventário está completo. Registre-o como tabela de
inventário com uma linha por rota. As categorias 1 a 4 são verificadas contra ele, linha
por linha.

## 4. Categorias

### 1. Isolamento de tenant e de dono (`isolation`)

No Supabase, isso é RLS ausente. Em APIs escritas à mão, são as consultas de listagem,
busca, agregação, relatório e exportação que não filtram pelo usuário autenticado nem
pela sua organização, workspace ou tenant. Primeiro identifique qual mecanismo de
isolamento o projeto usa (RLS, middleware de tenant, filtragem manual por `user_id`),
depois mostre onde ele está ausente ou falha.

### 2. Autorização em nível de função (`function-authz`)

Operações privilegiadas (administração, configurações, gestão de usuários, manutenção,
debug, reset de banco, ações de escrita) que o servidor expõe sem verificar o papel do
chamador, incluindo:

- Operações que o frontend esconde por papel (`isAdmin`, `canEdit`, `role`) enquanto o
  endpoint não faz checagem equivalente. Associe cada restrição de papel do frontend ao
  seu endpoint.
- Endpoints de administração, debug e manutenção acessíveis sem autenticação ou por
  qualquer usuário autenticado.

### 3. IDOR (`idor`)

Rotas que buscam, alteram ou apagam um objeto por um ID do caminho, da query ou do
corpo, sem verificar se o objeto pertence ao chamador ou ao seu tenant. Verifique cada
handler do inventário. Um objeto de outro usuário deve parecer exatamente igual a um
inexistente (404), para que a resposta não revele quais IDs existem.

### 4. Autorização em nível de propriedade (`property-authz`)

Corpos de requisição ligados a models sem lista de permissões (atribuição em massa), de
modo que o chamador defina campos como `admin`, `role`, `owner_id`, `tenant_id`, `price`
ou `verified`; e respostas que serializam models inteiros, devolvendo campos que o
chamador não deve ver (hashes de senha, tokens, flags internas, e-mails de outros
usuários).

### 5. Autenticação e sessões (`authn`)

Hash de senha (argon2, bcrypt ou scrypt, nunca um hash rápido); limite de taxa ou
bloqueio nos endpoints de login, redefinição e MFA; cookies de sessão com `HttpOnly`,
`Secure` e `SameSite`; expiração e revogação de sessões e tokens no logout e na troca de
senha; verificação de JWT que fixa o algoritmo e rejeita `none`; tokens de redefinição
de senha aleatórios, de uso único e com validade.

### 6. Injeção (`injection`)

Entrada do usuário que chega a um interpretador: SQL montado por concatenação ou
formatação de strings, injeção de operadores NoSQL, comandos de shell (`shell=True`,
`exec`, crases), caminhos de arquivo (path traversal, extração de arquivos compactados),
templates do lado do servidor renderizados a partir da entrada do usuário, e
desserialização de dados não confiáveis (`pickle`, `yaml.load`, serialização Java).

### 7. Entrada não sanitizada e XSS (`xss`)

Frontend: `innerHTML`, `dangerouslySetInnerHTML` e equivalentes do framework
(`v-html`, `[innerHTML]`), markdown ou HTML renderizados sem sanitização, URLs
controladas pelo usuário em `href` ou `src` (`javascript:`), `eval`, `new Function`.
Backend: entrada do usuário que chega a HTML de e-mail, templates ou respostas sem
escape. Verifique se o projeto tem uma biblioteca de sanitização e se ela é aplicada em
cada ponto encontrado.

### 8. SSRF (`ssrf`)

O servidor buscando uma URL que o usuário controla: webhooks, prévias de URL, importação
de imagens ou arquivos, geradores de PDF. Verifique se há lista de permissões, bloqueio
de endereços privados e link-local (incluindo o endpoint de metadados da nuvem
`169.254.169.254`), e tratamento de redirecionamentos que revalida o destino.

### 9. CSRF e CORS (`csrf-cors`)

Rotas que alteram estado, autenticadas por cookie, sem token CSRF e sem um cookie
`SameSite` que bloqueie requisições cross-site. Configurações de CORS que refletem
qualquer `Origin` ou que permitem `*` junto com credenciais.

### 10. Segredos expostos (`secrets`)

Chaves de API, tokens, senhas, segredos de assinatura (JWT, webhooks), chaves privadas e
credenciais padrão no código-fonte, nas configurações, em `docker-compose`, charts, CI,
scripts e documentação. Preste atenção especial a:

- Padrões públicos que viram segredos reais quando não são sobrescritos, como
  `${VAR:-valor-padrao}`, e validação ausente na inicialização que os rejeitaria.
- Segredos no histórico do git: execute `gitleaks detect` ou `trufflehog git file://.`
  quando estiverem disponíveis; senão, `git log -p -S '<padrão>'` para cada padrão de
  segredo encontrado na árvore atual. Quando o histórico estiver incompleto (um clone
  raso, `git rev-parse --is-shallow-repository` imprime `true`) ou ausente, registre em
  `methodology` que o histórico não foi verificado.
- Chaves empacotadas no build do frontend.

### 11. Limites de recursos (`limits`)

Limites de tamanho do corpo da requisição e de uploads, verificação de tipo de upload,
tamanho máximo de página em endpoints de listagem, limites de taxa em endpoints caros
ou abusáveis (busca, exportação, envio de e-mail), expressões regulares com backtracking
catastrófico sobre entrada do usuário, e loops ou alocações dimensionados pela entrada
do usuário.

### 12. Configuração de segurança (`config`)

Modo debug ou páginas de erro verbosas acessíveis em produção, stack traces em
respostas, cabeçalhos de segurança ausentes (`Content-Security-Policy`,
`Strict-Transport-Security`, `X-Content-Type-Options`, `frame-ancestors`), painéis de
administração e documentação da API expostos sem autenticação, e listagem de diretórios.

## Severidade

| Nível | Significado |
|---|---|
| `critical` | Explorável por qualquer pessoa que alcance o servidor ou crie uma conta, para ler ou alterar dados de outros usuários ou tenants, assumir contas, obter direitos de administrador, executar código ou obter segredos de produção. |
| `high` | O mesmo impacto, mas o atacante precisa de um papel específico, de uma conta convidada ou de uma configuração comum que não é a padrão; ou uma falha que transforma outra violação em algo pior (senhas guardadas em texto puro ou com hash rápido). |
| `medium` | Explorável só sob condições específicas (configuração, interação do usuário, momento), ou expõe dados limitados. |
| `low` | Lacuna de defesa em profundidade, sem caminho direto de exploração. |
| `info` | Uma observação sem risco por si só. |

## 5. Sintetizar e renderizar

Avalie cada achado pelo seu próprio caminho de exploração, com as condições em
`conditions`. Registre as doze categorias, os achados e os pontos fortes conforme
`audit-report` define, escreva a síntese e renderize. Entregue como `audit-report`
descreve.
