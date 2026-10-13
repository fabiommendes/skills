---
name: audit-privacy
description: Auditoria de privacidade e proteção de dados (LGPD, GDPR) de uma base de código, cobrindo o inventário de dados pessoais, minimização, dados pessoais em logs, compartilhamento com terceiros, consentimento, direitos do titular, retenção e proteção de dados sensíveis. Entregue como relatório em PDF/HTML com issues do GitHub prontas para colar. Use quando o usuário pedir uma auditoria de privacidade, LGPD ou GDPR, ou quiser saber quais dados pessoais uma aplicação coleta e para onde eles vão.
---

# Auditoria: privacidade

Audite como a aplicação coleta, guarda, compartilha e apaga dados pessoais, e entregue
o relatório definido pela skill `audit-report`.

Esta auditoria lê código e configuração; ela não é aconselhamento jurídico. Registre
esses pontos como achados `info` marcados com "para revisão jurídica", em vez de
julgá-los.

Falhas de controle de acesso que expõem dados pessoais ficam com `audit-webserver`;
cite-as aqui só para apontar essa auditoria.

Copie este checklist e acompanhe-o:

```
- [ ] 1. Carregar audit-report
- [ ] 2. Montar o inventário de dados pessoais
- [ ] 3. Verificar cada categoria
- [ ] 4. Sintetizar e renderizar
```

## 1. Carregar audit-report

Invoque a skill `audit-report` agora e inicie ou retome o log. Ela define como você
registra os achados conforme avança. A área é `privacy`; o prefixo do título da issue
é `[Privacy]`.

## 2. Montar o inventário de dados pessoais

Dado pessoal é qualquer informação sobre uma pessoa identificada ou identificável:
nomes, e-mails, telefones, documentos (CPF, passaporte), endereços, endereços IP,
identificadores de dispositivo e de publicidade, localização, fotos, campos de texto
livre que os usuários preenchem. Dados sensíveis, pelo art. 5º, II, da LGPD e pelo
art. 9 do GDPR, abrangem dados de saúde, biométricos e genéticos, origem racial ou
étnica, religião, opinião política, filiação sindical, e vida ou orientação sexual;
dados de crianças também exigem cuidado especial.

Encontre dados pessoais em schemas e migrações de banco, models do ORM, tipos de
requisição e resposta da API, formulários, uploads de arquivos, eventos de analytics e
comandos de log. Registre uma linha por item de dado em uma tabela de inventário: item
de dado, onde é guardado (`tabela.coluna` ou arquivo), origem, finalidade encontrada
no código, sensível (sim/não), terceiros que o recebem, e retenção.

## 3. Categorias

### 1. Minimização (`minimization`)

Dados pessoais coletados ou guardados mas nunca usados para nenhuma finalidade que o
código mostre; documentos completos ou datas de nascimento guardados onde uma checagem
ou um ano bastaria; objetos de usuário inteiros devolvidos por APIs que precisam de
dois campos.

### 2. Dados pessoais em logs e telemetria (`logs`)

Dados pessoais ou segredos gravados em logs, rastreadores de erro (Sentry e similares),
eventos de analytics, URLs e query strings, e caches. Verifique o middleware de log de
requisições e os handlers de exceção, que muitas vezes despejam corpos inteiros.

### 3. Compartilhamento com terceiros (`sharing`)

SDKs e serviços que recebem dados pessoais: analytics, publicidade, provedores de
e-mail e SMS, processadores de pagamento, widgets de suporte, APIs de LLM e de IA. Para
cada um, registre quais dados recebe. Sinalize rastreadores e SDKs carregados antes de
o usuário consentir, e dados pessoais enviados a serviços que não precisam deles.

### 4. Consentimento (`consent`)

Como o consentimento é coletado, guardado (com data e a versão do texto aceito) e
retirado; se cookies e rastreadores não essenciais esperam pelo consentimento; se
retirar o consentimento interrompe o tratamento no código.

### 5. Direitos do titular (`rights`)

Se o código oferece acesso e portabilidade (exportar os dados de um usuário),
correção e exclusão. Na exclusão, siga os dados: exclusões lógicas que mantêm tudo,
tabelas relacionadas, arquivos enviados, índices de busca, caches, analytics e
terceiros que guardam uma cópia.

### 6. Retenção (`retention`)

Jobs de limpeza, TTLs ou arquivamento para dados pessoais; dados mantidos para sempre
por padrão; logs e backups sem retenção configurada quando a configuração está no
repositório.

### 7. Proteção de dados pessoais (`protection`)

Criptografia em trânsito e, para dados sensíveis, em repouso ou por campo; dados
pessoais expostos em ferramentas de administração e de suporte a mais funcionários do
que precisam; dados pessoais reais em seeds, fixtures, dumps de teste ou ambientes que
não são de produção.

### 8. Transferência internacional (`transfer`)

Dados pessoais armazenados ou tratados fora da jurisdição do usuário, como mostram as
regiões de nuvem e os provedores terceiros na configuração. Registre-os como `info`
para revisão jurídica.

## Severidade

| Nível | Significado |
|---|---|
| `critical` | Dados pessoais sensíveis expostos publicamente ou a partes sem motivo para recebê-los. |
| `high` | Dados pessoais enviados a terceiros sem consentimento ou sem finalidade no código, dados pessoais em logs enviados a serviços externos, ou nenhuma forma de apagar os dados de um usuário. |
| `medium` | Exclusão ou exportação incompleta, retenção ausente para dados pessoais, coleta além do que o código usa. |
| `low` | Pequenas lacunas de minimização, como uma API que devolve um campo não sensível de que não precisa. |
| `info` | Pontos para revisão jurídica, e observações sem risco por si só. |

## 4. Sintetizar e renderizar

Registre as oito categorias, os achados e os pontos fortes conforme `audit-report`
define, escreva a síntese e renderize. Mascare dados pessoais em trechos e capturas de
tela.
