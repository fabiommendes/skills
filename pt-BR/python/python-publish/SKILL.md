---
name: python-publish
description: "Diretrizes para publicar pacotes Python. Aplique ao criar um novo
projeto Python ou quando pedirem para configurar um pipeline de publicação em um
projeto existente."
disable-model-invocation: true
---

# python-publish

Bibliotecas Python e ferramentas de linha de comando (CLI) são publicadas no PyPI. Outros projetos, como aplicações web em Python, podem ter requisitos de publicação diferentes, então não são cobertos aqui.

Jogos e aplicações autônomas também podem ser publicados por outro mecanismo, como PyInstaller, AppImage, Snapcraft ou WebAssembly.

## PyPI

O PyPI usa pipelines de CI/CD com parceiros confiáveis para construir e publicar pacotes. Por padrão, usamos GitHub Actions. Se o projeto nunca foi publicado antes, instrua o usuário a entrar no PyPI e adicionar um novo publicador em https://pypi.org/manage/account/publishing/.

Em seguida, crie o arquivo .github/workflows/publish.yml (se ele não existir) com o seguinte conteúdo:

```yaml
# $schema=https://www.schemastore.org/github-workflow.json
on:
  release:
    types:
      - created
  push:
    tags:
      - "v*.*.*"

name: release

jobs:
  pypi-publish:
    name: upload release to PyPI
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3
        with:
          enable-cache: true

      - name: Set up Python
        run: uv python install

      - name: Build package distributions
        run: uv build

      - name: Publish to PyPI
        run: uv publish
```

Instrua o usuário a criar um commit novo com tag e fazer push para o repositório.
