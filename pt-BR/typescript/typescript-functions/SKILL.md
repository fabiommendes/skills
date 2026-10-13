---
name: typescript-functions
description: Estilo e boas práticas ao implementar ou refatorar funções e métodos em TypeScript
---

# typescript-functions

Boas práticas e guia de estilo para implementar funções e métodos em TypeScript.


## Arquitetura

Evite efeitos colaterais. A maioria das funções e métodos deve ser pura ou, pelo
menos, permitir raciocínio local. Deixe os efeitos colaterais mais graves para o
framework ou para uma camada externa da aplicação.

Como referência, a lista mostra os efeitos do melhor para o pior.

* sem efeitos colaterais, função pura (melhor).
* logging.
* mutação local de `self`.
* mutação local dos argumentos de entrada.
* cache.
* print e input.
* I/O de arquivos.
* acesso a banco de dados.
* exibição de imagens, som, renderização complexa de marcação.
* acesso à rede.
* mutação global do comportamento da aplicação (pior).

Tente manter a implementação o mais alto possível nesta lista.

## Testes

Funções puras devem ser testadas com exemplos em testes unitários. Se a função
respeitar algum invariante, use testes baseados em propriedades para gerar uma
ampla gama de casos. A biblioteca `fast-check` do TypeScript é uma boa escolha
para isso.

Funções até "mutação local dos argumentos de entrada" podem ser testadas sem
configuração especial. Use sempre testes baseados em propriedades quando um
invariante for conhecido.

Funções que usam cache devem, normalmente, limpar o cache antes de cada teste.

Funções com I/O simples devem capturar a saída com mocks apropriados para
`console.log`, `console.error` e `prompt`.

Funções que leem arquivos devem usar mocks. Funções que escrevem arquivos devem
fazê-lo em diretórios temporários, por exemplo, com a biblioteca `tmp`.

Funções que acessam bancos de dados devem usar transações e rollbacks, para não
deixar o banco em estado sujo. Muitos frameworks oferecem suporte nativo para
isso, por meio de fixtures do pytest.

Funções que produzem multimídia complexa devem, normalmente, ser testadas com
approval testing. Em Python, use a biblioteca approvaltests.Python.

O acesso à rede deve, normalmente, ser mockado em testes unitários e testado em
testes de integração.

Quando uma função produz uma mutação global do comportamento da aplicação, ela
também deve oferecer um mecanismo de snapshot que restaure a aplicação ao estado
anterior. O ideal é fazer isso com context managers. Pergunte ao usuário se esse
mecanismo deve ser exposto como API pública ou não.


## Estilo de código

Nomes de funções seguem camelCase. Sempre documente funções públicas. Sempre
tipifique os parâmetros de entrada e de saída. No nível superior, use declarações
`function` em vez de `const` com arrow functions. Use arrow functions como
callbacks e para funções internas.


## Argumentos

Use no máximo 4 argumentos posicionais em uma função. Se ela tiver mais de 4
parâmetros, use um único parâmetro objeto com propriedades nomeadas.

Se a função tiver mais de 2 argumentos do mesmo tipo, prefira um parâmetro objeto
com propriedades nomeadas. Quebre esta regra se a função expressar uma relação
clara entre os dois argumentos, ou se a posição não importar.

Uma relação clara tem a forma `palavra(primeiro, segundo)` e pode ser entendida
como `primeiro palavra segundo`.

```typescript
// good
function join(a: string, b: string): string { ... }
function hasPrefix(text: string, prefix: string): boolean { ... }
function replace(text: string, { sub, by }: { sub: string, by: string }): string { ... }

// bad
function replace(text: string, sub: string, by: string): string { ... }
```

Se a função expressar uma relação entre dois argumentos e o papel de cada um for
implícito pela posição, exija também que sejam posicionais. Por exemplo:

```python
def swap[T](a: T, b: T, /) -> tuple[T, T]: ...
```

Se a função tiver mais de um argumento opcional do mesmo tipo, exija que ambos
sejam somente por nome. Se tiver mais de 3 argumentos opcionais, exija que todos
sejam somente por nome. Use o símbolo `*` para impor isso na assinatura da função.
Por exemplo:

```python
def join_items(data: Iterable[str], *, sep: str = ",", end: str = "\n") -> str: ...
```

Se a função não alterar os argumentos de entrada, prefira interfaces a tipos
concretos.


## Comentários de documentação

Use o estilo JSDoc. Sempre quebre o bloco de comentário em mais de uma linha,
mesmo em comentários curtos. Por exemplo:

```typescript
/**
 * Return a new array in reverse order of elements.
 */
function reverse() {
    // ...
}
```

Use markdown para estruturar a informação (por exemplo, listas e blocos de código).

A primeira linha deve ser um resumo curto da finalidade da função. Se houver mais
detalhes relevantes, inclua-os em um ou mais parágrafos separados por linhas em
branco.

Use as tags JSDoc `@param`, `@returns` e `@throws` para documentar parâmetros,
valores de retorno e exceções. Não inclua os tipos nas tags `@param` e `@returns`.
Especifique-os na assinatura da função.

Coloque uma linha em branco antes da primeira tag `@param` e antes das tags
`@returns` e `@throws`.

Funções públicas que não produzem efeitos colaterais devem ser documentadas com um
exemplo de doctest. Use a tag `@example`. Pule o teste se ele for complexo demais
ou exigir muitas dependências externas ou preparação.

Abaixo está um bom exemplo de como documentar uma função:

```typescript
/** 
  * Return a new array in reverse order of elements.
  *
  * @example reverse([1, 2, 3]) 
  * //=> [3,2,1]
  * 
  * @param arr - The array to reverse.
  * @param inplace - If true, reverse the array in place. Otherwise, return a new array.
  *
  * @returns A new array with the elements in reverse order.
  */ 
function reverse<T>(arr: T[], inplace: boolean = false): T[] {
    return inplace? arr.reverse() : [...arr].reverse();
}
```
