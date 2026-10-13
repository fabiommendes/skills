---
name: python-projects
description: Estilo e boas práticas ao implementar projetos em Python
---

# python-projects

## Ferramentas

A escolha padrão é usar `uv` para gerenciar projetos. Escolha-o em projetos novos, mas não mude projetos antigos para usá-lo.

Em projetos novos, escolha também estas ferramentas de desenvolvimento padrão:

* ruff para lint e formatação.
* pytest para testes.
* doc-zero para documentação.
* taskipy para gerenciamento de tarefas.
* mypy para checagem de tipos.


## Tarefas

Todos os comandos comuns de desenvolvimento devem ser declarados explicitamente como tarefas. Isso geralmente significa adicionar entradas à seção `[tool.taskipy.tasks]` do arquivo `pyproject.toml`.

Todo projeto deve definir pelo menos estas tarefas:

* `test` - executa todos os testes.
* `lint` - executa todos os linters e formatadores.
* `docs` - gera a documentação.
* `ci` - executa todas as checagens de CI, incluindo testes, linters e documentação.
* `release` - executa todas as checagens que garantem que o projeto está pronto para ser publicado no PyPI.


## Layout do código-fonte

Projetos complexos, com vários pacotes, devem usar o layout `src`. Isso significa que o código-fonte fica em um diretório `src`, e os testes ficam em um diretório `tests` na raiz do projeto.

```text
src/
    package1/
    package2/
tests/
    package1/
    package2/
```

Projetos menores, formados por um único pacote, podem usar o layout mais simples, em que o código-fonte e os testes ficam no mesmo diretório.

```text
package/
    __init__.py
    module1.py
    ...
tests/
    test_module1.py
    ...
```

Para oferecer suporte a esse último, é importante adicionar estas linhas no `pyproject.toml`:

```toml
[tool.uv.build-backend]
module-name = "<package-name>"
module-root = "."
```

## CI/CD

O projeto deve ter um pipeline de CI/CD que execute todos os testes, linters e a documentação em cada commit. O pipeline também deve executar a tarefa `release` em cada tag.

Por padrão, use GitHub Actions para CI/CD. O workflow padrão deve ficar em `.github/workflows/ci.yml`.

Se o projeto for uma biblioteca, o workflow também deve construir e publicar o pacote no PyPI em cada tag.

## Readme

O projeto deve ter um arquivo `README.md` na raiz. O README deve incluir:

* Uma descrição curta do projeto.
* Um badge do pipeline de CI/CD.
* Um badge da última release.
* Instruções de instalação.
* Exemplos de uso.

## Licença

O projeto deve ter um arquivo `LICENSE` na raiz. Se o LICENSE não existir, crie um arquivo `LICENSE` com a licença MIT.
