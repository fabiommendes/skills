---
name: python-modules
description: Estilo e boas práticas ao implementar ou refatorar módulos em Python
---

# python-modules

Boas práticas e guia de estilo para implementar módulos em Python.


## Arquitetura

Prefira módulos profundos a módulos largos. Um módulo profundo tem uma superfície de API pequena, mas implementa muitas funcionalidades. Evite expor funções públicas triviais de implementar, que oferecem apenas conveniência marginal.


## Layout do código

Todos os módulos devem incluir o import "from __future__ import annotations". O módulo deve ser organizado na seguinte ordem:

* Docstring do módulo, se for público.
* Future imports.
* Imports.
* Constantes em nível de módulo. Devem estar em maiúsculas e separadas por underscores.
* Aliases de tipo em nível de módulo. Devem estar em PascalCase.
* Os principais pontos de entrada da API do módulo. Podem ser uma classe ou uma função. Se o módulo expõe várias APIs, agrupe-as em ordem lógica, da mais importante para a menos importante.
* Implementação interna do módulo. Pode ser composta de classes, funções ou variáveis. Esses itens devem ter nome iniciado por underscore. Se o módulo for grande, ele pode ser dividido em vários arquivos, e a implementação interna pode ficar em um módulo privado.
* Se quiser separar por seções, use o seguinte estilo de comentário:

  ```python
  # 
  # TÍTULO DA SEÇÃO
  #
  ```

  A seção também pode conter comentários extras se implementarem um comportamento incomum ou complexo. Esses comentários devem ficar depois do título da seção.


## Módulos públicos

Todos os módulos públicos devem ter uma docstring no topo do arquivo, com uma descrição curta da finalidade do módulo. NÃO liste os símbolos expostos na docstring.

Módulos públicos também devem exportar uma variável `__all__` com a lista dos símbolos públicos. Você pode separar seções dentro dos símbolos exportados com comentários, assim:

```python
__all__ = [
    "MyClass",
    #: Section title
    #
    # Small paragraph describing the section.
    "fn1",
    "fn2",
]
```

## Módulos privados

Módulos privados não contêm docstring nem variável `__all__`. Um módulo pode ser privado por dois motivos:

* Uso interno apenas: nunca exporta símbolos públicos.
* Implementa algum símbolo público que é reexportado por um módulo público. É usado principalmente para dividir uma implementação grande em vários arquivos.

Módulos de uso interno devem sempre começar com underscore. Os símbolos dentro de módulos privados devem ter nomes públicos. Esses módulos costumam ser importados como namespaces, assim:

```python
from . import _internal_module

# use some symbol:
_internal_module.some_symbol()
```
