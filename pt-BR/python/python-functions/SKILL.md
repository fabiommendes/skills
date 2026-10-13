---
name: python-functions
description: Estilo e boas práticas ao implementar ou refatorar funções e métodos em Python
---

# python-functions

Boas práticas e guia de estilo para implementar funções e métodos em Python.


## Arquitetura

Evite efeitos colaterais. A maioria das funções e métodos deve ser pura ou, no mínimo, permitir raciocínio local. Deixe os efeitos colaterais mais graves para o framework ou para uma camada externa da aplicação.

Como referência, a lista mostra os efeitos do melhor para o pior.

* sem efeitos colaterais, função pura (melhor).
* logging.
* mutação local de self.
* mutação local dos argumentos de entrada.
* cache.
* print e input.
* I/O de arquivos.
* acesso a banco de dados.
* exibição de imagens, som, renderização complexa de marcação.
* acesso à rede.
* mutação global do comportamento da aplicação (pior).

Procure manter as implementações o mais alto possível nesta lista.

## Argumentos

Se a função tiver apenas um argumento obrigatório, exija que ele seja posicional. Use o símbolo `/` na assinatura da função para impor isso.

```python
def filter[T](data: Iterable[T], /, by: Callable[[T], bool]) -> Iterable[T]: ...
```

Se a função expressa uma relação entre dois argumentos e o papel de cada um é implícito pela posição, exija também que ambos sejam posicionais. Por exemplo:

```python
def swap[T](a: T, b: T, /) -> tuple[T, T]: ...
```

Se a função tiver mais de um argumento opcional do mesmo tipo, exija que todos eles sejam somente por palavra-chave. Se tiver mais de três argumentos opcionais, exija que todos sejam somente por palavra-chave. Use o símbolo `*` na assinatura da função para impor isso. Por exemplo:

```python
def join_items(data: Iterable[str], *, sep: str = ",", end: str = "\n") -> str: ...
```


## Testes

Funções puras devem ser testadas com exemplos em testes unitários. Se a função respeitar algum invariante, use testes baseados em propriedades para gerar uma ampla variedade de entradas. A biblioteca `hypothesis`, do Python, é uma boa escolha para isso.

Funções até o nível "mutação local dos argumentos de entrada" podem ser testadas sem preparação especial. Sempre use testes baseados em propriedades quando um invariante for conhecido.

Funções que usam cache devem, em geral, limpar o cache antes de cada teste.

Funções com I/O simples devem capturar a saída com `redirect_stdout` e `redirect_stderr`, do contextlib, e usar mock para `input`.

Funções que leem arquivos devem usar mock. Funções que escrevem arquivos devem fazê-lo em diretórios temporários.

Funções que acessam bancos de dados devem usar transações e rollbacks para não deixar o banco em estado sujo. Muitos frameworks oferecem suporte nativo para isso por meio de fixtures do pytest.

Funções que produzem multimídia complexa devem, em geral, ser testadas com approval testing. Para isso, o Python tem a biblioteca approvaltests.Python.

Acesso à rede deve, em geral, ser mockado em testes unitários e testado em testes de integração.

Quando uma função produz uma mutação global do comportamento da aplicação, ela também deve oferecer um mecanismo de snapshot que restaure a aplicação ao estado anterior. O ideal é fazer isso com context managers. Pergunte ao usuário se esse mecanismo deve ser exposto como API pública ou não.


## Estilo de código

Siga a PEP 8. Sempre anote os tipos dos parâmetros de entrada e de saída (type hints). Se a função não alterar os argumentos de entrada, prefira tipos abstratos a concretos. Por exemplo, use "Iterable" em vez de "list", "Mapping" em vez de "dict", etc. Nunca use "Any", a menos que seja estritamente necessário.

## Docstrings

Use docstrings no estilo Google. Não repita os tipos na docstring. Documente as exceções que a função pode levantar. Documente o valor de retorno, a menos que seja `None`.

A menos que a função seja uma linha só, as aspas triplas da docstring devem ficar em linhas próprias.

A primeira linha da docstring deve ser um resumo curto da finalidade da função. Se houver mais detalhes, inclua-os depois de uma linha em branco.

Funções públicas sem efeitos colaterais devem ser documentadas com um exemplo de doctest. Dispense o doctest se ele for complexo demais ou exigir muitas dependências externas ou preparação.
