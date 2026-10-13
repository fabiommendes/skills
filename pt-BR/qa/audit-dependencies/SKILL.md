---
name: audit-dependencies
description: Auditoria da cadeia de suprimentos das dependências de um projeto, cobrindo vulnerabilidades conhecidas, fixação de versões e lockfiles, código executado na instalação, procedência dos pacotes, saúde de manutenção, dependências não usadas e licenças. Entregue como relatório em PDF/HTML com issues do GitHub prontas para colar. Use quando o usuário pedir para auditar dependências, verificar pacotes vulneráveis ou desatualizados, ou revisar a cadeia de suprimentos.
---

# Auditoria: dependências

Audite tudo o que o projeto puxa de fora (pacotes, imagens base, actions de CI, código
vendorizado) e entregue o relatório definido pela skill `audit-report`.

Copie este checklist e acompanhe-o:

```
- [ ] 1. Carregar audit-report
- [ ] 2. Montar o inventário de dependências
- [ ] 3. Executar os scanners de vulnerabilidade
- [ ] 4. Verificar cada categoria
- [ ] 5. Sintetizar e renderizar
```

## 1. Carregar audit-report

Invoque a skill `audit-report` agora e inicie ou retome o log. Ela define como você
registra os achados conforme avança. A área é `dependencies`; o prefixo do título da
issue é `[Deps]`.

## 2. Montar o inventário de dependências

Encontre todo manifesto e lockfile: `package.json` com `package-lock.json`,
`pnpm-lock.yaml` ou `yarn.lock`; `pyproject.toml` com `uv.lock` ou `poetry.lock`;
`requirements*.txt`; `Cargo.toml`/`Cargo.lock`; `go.mod`/`go.sum`; `Gemfile.lock`;
`pom.xml`; `build.gradle`; `composer.lock`; Dockerfiles (linhas `FROM`); workflows de
CI (linhas `uses:`); e código de terceiros vendorizado ou copiado.

Registre uma linha por manifesto em uma tabela de inventário: caminho, ecossistema,
se o lockfile existe e está sincronizado, e o número de dependências diretas de
produção e de desenvolvimento.

## 3. Executar os scanners de vulnerabilidade

Execute o scanner de cada ecossistema, a partir do diretório do projeto:

| Ecossistema | Comando |
|---|---|
| qualquer (preferido, cobre a maioria dos lockfiles) | `osv-scanner scan source -r .` |
| npm / pnpm / yarn | `npm audit --json`, `pnpm audit --json`, `yarn npm audit --json` |
| Python | `uvx pip-audit` (acrescente `-r requirements.txt` ou execute dentro do ambiente do projeto) |
| Rust | `cargo audit` |
| Go | `govulncheck ./...` |

Informe vulnerabilidades só a partir da saída de um scanner ou de um aviso que você
consultou. Nunca cite um CVE de memória. Se nenhum scanner puder rodar (sem rede, sem
ferramenta), diga isso em `methodology` e diga na `note` da categoria que a cobertura
é parcial.

Para cada vulnerabilidade, verifique a alcançabilidade: o pacote vulnerável é usado em
código de produção, e a função ou o recurso vulnerável é chamado? Registre a evidência
em `conditions`.

## 4. Categorias

### 1. Vulnerabilidades conhecidas (`vulnerabilities`)

Resultados dos scanners, sem duplicatas por aviso, com a versão instalada, a versão
corrigida e a alcançabilidade.

### 2. Fixação de versões e lockfiles (`pinning`)

Aplicações sem lockfile commitado, ou com um lockfile fora de sincronia com o
manifesto; `latest` ou tags flutuantes em linhas `FROM`; GitHub Actions referenciadas
por tag ou branch em vez de um SHA de commit; `curl ... | sh` e downloads sem versão
fixada em Dockerfiles, CI e scripts de configuração.

### 3. Código executado na instalação (`install-scripts`)

Pacotes que executam código na instalação (scripts `preinstall`/`postinstall` no npm,
builds em `setup.py`, scripts de build), e dependências instaladas a partir de URLs
git, tarballs ou caminhos locais.

### 4. Procedência (`provenance`)

Nomes a um erro de digitação de um pacote popular; nomes de pacotes internos que
também resolveriam no registro público (confusão de dependências) quando a
configuração do registro não os restringe; pacotes de forks pessoais ou de contas sem
histórico.

### 5. Saúde de manutenção (`maintenance`)

Pacotes descontinuados, pacotes arquivados pelo autor, e runtimes ou imagens base fora
de suporte (Node.js, Python, releases de distribuição). Verifique o histórico de
releases no registro quando houver acesso à rede; senão, informe só o que o lockfile e
os avisos de descontinuação mostram.

### 6. Tamanho da dependência (`footprint`)

Dependências declaradas e nunca importadas, várias bibliotecas para o mesmo trabalho,
dependências pesadas usadas para uma função trivial, e dependências de desenvolvimento
que chegam ao bundle ou à imagem de produção.

### 7. Licenças (`licenses`)

Dependências com licenças copyleft (GPL, AGPL) em um produto distribuído ou oferecido
como serviço, pacotes sem licença, e licenças incompatíveis com a licença do próprio
projeto. Pergunte ao usuário como o produto é distribuído antes de classificar esses
casos; sem resposta, classifique-os como `info`.

## Severidade

| Nível | Significado |
|---|---|
| `critical` | Um pacote malicioso ou comprometido, ou uma vulnerabilidade alcançável que permite execução de código, bypass de autenticação ou roubo de dados em produção. |
| `high` | Uma vulnerabilidade alcançável de severidade alta, ou código de instalação vindo de uma fonte sem versão fixada ou não confiável. |
| `medium` | Uma vulnerabilidade não alcançável do jeito como é usada, lockfiles ausentes ou actions sem versão fixada, ou um runtime fora de suporte. |
| `low` | Dependências não usadas ou duplicadas, pacotes descontinuados sem vulnerabilidades conhecidas. |
| `info` | Observações sobre licenças e notas de manutenção. |

## 5. Sintetizar e renderizar

Registre as sete categorias, os achados e os pontos fortes conforme `audit-report`
define, escreva a síntese e renderize. Para vulnerabilidades, coloque o id do aviso, a
versão instalada e a versão corrigida no `title` ou na `description` do achado, e o
caminho do manifesto em `location`. Agrupe em uma única issue as atualizações que um
único comando corrige.
