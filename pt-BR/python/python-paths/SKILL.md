---
name: python-paths
description: Boas práticas ao trabalhar com caminhos de arquivos em Python
---

# python-paths

O Python tem 3 formas padrão de representar caminhos de arquivos: `str`, `bytes` e `pathlib.Path`. Sempre use `pathlib.Path` em código novo, a menos que ele interaja com código de terceiros que exija `str` ou `bytes`.

Objetos semelhantes a `Path`, como `trio.Path`, também são padrões aceitáveis.

Prefira as APIs de alto nível de `pathlib.Path` às APIs de baixo nível, como `os.path`. Por exemplo, use `Path.read_text()` em vez de `open(path).read()`, e `Path.iterdir()` em vez de `os.listdir()`.

Ao interagir com código de terceiros que exija `str` ou `bytes`, use `str(Path)` ou `bytes(path)`, conforme o caso. Ao ler caminhos dessas APIs, use `Path(path)` para convertê-los de volta para objetos `Path`.

É aceitável projetar APIs públicas que aceitem objetos `str`, `bytes` ou `Path`. Nesse caso, defina tipos de nível superior, como `PathLike = str | bytes | Path`, e use-os nos type hints. Use `Path(path)` para convertê-los em objetos `Path` para uso interno.
