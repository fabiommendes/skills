# Testes

## Índice

- O que testar
- Seams
- Como escolher a abordagem
- Densidade de asserções
- Bons testes
- Maus testes
- Mocking
- Determinismo
- Código de teste

## O que testar

- Testes, como código, são dívida. Seja estratégico sobre quando e como escrevê-los.
- Teste contratos: lógica complexa, regras de negócio, ações do usuário. Não teste detalhes triviais de implementação. Não escreva testes só para aumentar a cobertura.
- Teste explicitamente as condições de fronteira, porque é ali que estão os bugs.
- Prefira garantias estáticas a testes. Não escreva testes para o que o sistema de tipos pode garantir. Para o próprio código em nível de tipos (auxiliares genéricos, tipos condicionais ou mapeados), escreva testes de tipo onde a linguagem permitir (por exemplo, `expectTypeOf` em TypeScript, `assert_type` em Python).
- Ao corrigir um bug, primeiro escreva um teste que o reproduza e falhe pelo motivo relatado. Depois corrija o bug. Dê ao teste o nome do comportamento que quebrou, não o número da issue.

## Seams

Um **seam** é a fronteira pública em que você observa o comportamento. Os testes se acoplam a seams, nunca a detalhes internos.

Prefira o seam mais interno que cobre o comportamento. Para "o usuário pode redefinir a senha", os candidatos podem ser:

- `POST /auth/reset`: o endpoint HTTP. Requisição real, lenta.
- `resetPassword(email, clock, mailer)`: a função de serviço. Rápida.
- `TokenGenerator.create()`: interno. Não teste isto; ele quebra em uma refatoração.

Teste a função de serviço. O endpoint deve ser uma camada genérica e fina sobre ela, com roteamento e serialização, sem lógica própria. Quando a camada externa é fina, testar a interna cobre o comportamento por uma fração do custo.

Isto é uma obrigação de design tanto quanto de teste. Quando o único seam que cobre um comportamento é caro (uma ida e volta HTTP, um navegador, um banco de dados real), a lógica costuma ficar presa na camada externa. Mova-a para uma abstração interna e teste ali.

Testes caros ainda merecem espaço, mas em pequeno número e com escopo amplo: o suficiente para verificar se a ponte entre a camada externa e a abstração interna está ligada corretamente. Um teste que exercita o endpoint e verifica muitas propriedades vale mais que dez que pagam o custo de setup para verificar uma coisa cada.

## Como escolher a abordagem

Em ordem de preferência:

**1. Testes baseados em propriedades ou fuzzing.** Melhores onde existem invariantes: ida e volta, idempotência, ordenação, conservação. Construa os geradores, estratégias ou fábricas uma vez e reutilize-os em vários testes. Esse reuso é o que mantém a suíte pequena.

**2. Testes baseados em exemplos**, orientados a tabela quando fizer sentido: uma função de teste sobre uma tabela de pares de entrada e saída esperada. Use isto para funções puras, sem efeitos colaterais. Use a parametrização do framework (`pytest.mark.parametrize`, `test.each`) em vez de um laço, para que cada caso seja reportado sozinho. Mova os exemplos para arquivos de fixture quando ficarem volumosos.

Para saídas estruturadas grandes (HTML renderizado, código gerado, saída de CLI), em que escrever o valor esperado à mão não é prático, use testes de snapshot ou de golden file. O golden file é o valor esperado: revise cada diferença nele como revisaria código e nunca o regenere só para fazer um teste passar. Remova partes instáveis (timestamps, ids, caminhos absolutos) e mantenha os snapshots pequenos o bastante para serem lidos. Um snapshot que ninguém lê é uma tautologia.

**3. Testes imperativos com mocks.** Só quando nenhuma das anteriores funcionar. Veja [Mocking](#mocking).

Não as sobreponha. Se uma propriedade cobre um comportamento, não escreva também exemplos para ele. O objetivo é o menor conjunto de testes que cubra os cenários.

## Densidade de asserções

Avalie pelo custo de execução do teste.

**Barato** (sem setup de fixture, sem banco de dados, sem rede, sem criação de processo): uma asserção lógica por teste. Uma falha aponta direto para o comportamento que quebrou.

**Caro** (reinicialização de banco de dados, serviços externos, navegador, fixtures grandes): agrupe as asserções. Percorra o caminho feliz uma vez e verifique tudo o que é observável no resultado. Separar isso em testes isolados multiplica o custo de setup e torna a suíte lenta a ponto de ela deixar de ser executada. Isso custa mais do que a precisão perdida.

Casos de borda continuam granulares em qualquer caso. Costumam ser baratos, e um teste de caso de borda agrupado diz pouco quando falha.

## Bons testes

Testes verificam o comportamento por meio de interfaces públicas. O código pode mudar por completo; os testes não devem. Um bom teste se lê como uma especificação.

```typescript
// GOOD: tests observable behavior
test("user can checkout with valid cart", async () => {
  const cart = createCart();
  cart.add(product);
  const result = await checkout(cart, paymentMethod);
  expect(result.status).toBe("confirmed");
});
```

- Testa comportamento que interessa a quem chama o código
- Usa apenas a API pública
- Sobrevive a refatorações internas
- Descreve O QUE, não COMO

## Maus testes

**Acoplado à implementação.** Faz mock de colaboradores internos, testa métodos privados ou verifica por um canal lateral. O sinal: quebra quando você refatora, mas o comportamento não mudou.

```typescript
// BAD: asserts on an internal call
test("checkout calls paymentService.process", async () => {
  const mockPayment = jest.mock(paymentService);
  await checkout(cart, payment);
  expect(mockPayment.process).toHaveBeenCalledWith(cart.total);
});
```

```typescript
// BAD: bypasses the interface to verify
test("createUser saves to database", async () => {
  await createUser({ name: "Alice" });
  const row = await db.query("SELECT * FROM users WHERE name = ?", ["Alice"]);
  expect(row).toBeDefined();
});

// GOOD: verifies through the interface
test("createUser makes user retrievable", async () => {
  const user = await createUser({ name: "Alice" });
  const retrieved = await getUser(user.id);
  expect(retrieved.name).toBe("Alice");
});
```

**Tautológico.** O valor esperado é calculado da mesma forma que o código o calcula. Assim, o teste passa por construção e nunca discorda do código.

```typescript
// BAD: expected value recomputes the implementation
test("calculateTotal sums line items", () => {
  const items = [{ price: 10 }, { price: 5 }];
  const expected = items.reduce((sum, i) => sum + i.price, 0);
  expect(calculateTotal(items)).toBe(expected);
});

// GOOD: expected value is an independent literal
test("calculateTotal sums line items", () => {
  expect(calculateTotal([{ price: 10 }, { price: 5 }])).toBe(15);
});
```

Valores esperados devem vir de uma fonte independente de verdade: um literal conhecido como correto, um exemplo resolvido ou a especificação.

Propriedades não são tautologias. `decode(encode(x)) === x` afirma uma relação que a implementação precisa satisfazer, e ela pode falhar: isso é uma fonte independente de verdade. Reexecutar o próprio algoritmo da implementação para produzir o valor esperado não é.

## Mocking

Prefira objetos reais. Faça mock apenas nas **fronteiras do sistema**:

- APIs externas (pagamento, e-mail, etc.)
- Bancos de dados (às vezes; prefira um banco de teste)
- Tempo e aleatoriedade
- Sistema de arquivos (às vezes; prefira diretórios temporários)

Não faça mock das suas próprias classes e módulos, de colaboradores internos ou de qualquer coisa que você controle.

Uma fronteira injetada é uma fronteira que você pode substituir. Por isso, a facilidade de mock decorre das regras de injeção em [SKILL.md](SKILL.md). Modele a interface injetada com uma função por operação externa, em vez de um único fetcher genérico:

```typescript
// GOOD: each function is independently mockable
const api = {
  getUser: (id) => fetch(`/users/${id}`),
  getOrders: (userId) => fetch(`/users/${userId}/orders`),
  createOrder: (data) => fetch('/orders', { method: 'POST', body: data }),
};

// BAD: mocking requires conditional logic inside the mock
const api = {
  fetch: (endpoint, options) => fetch(endpoint, options),
};
```

Cada mock retorna uma forma específica, não precisa de lógica condicional, mostra quais endpoints um teste exercita e mantém a segurança de tipos por endpoint.

## Determinismo

- Cada teste é independente: sem estado mutável compartilhado e sem depender da ordem dos testes.
- Não use relógio, rede ou aleatoriedade reais, a menos que o comportamento testado seja sobre eles. Injete ou simule-os no lugar. Defina a semente (seed) dos geradores quando precisar de aleatoriedade.
- Nunca use `sleep` para esperar que algo aconteça. Espere pela própria condição com um tempo limite, ou controle o relógio. Um teste que só passa quando a máquina é rápida o bastante é instável (flaky).

## Código de teste

- Testes são código: mantenha-os legíveis acima de tudo, refatore-os e apague-os quando deixarem de agregar valor.
- Dê a cada teste o nome do comportamento que ele fixa.
- Siga a suíte existente: framework, organização, nomes, estilo de fixtures e estilo de asserções. Não introduza um novo framework de teste nem uma nova biblioteca auxiliar sem aprovação.
- Reutilize as fixtures, fábricas e geradores do projeto antes de escrever novos. Monte dados de teste com builders ou fábricas que preenchem valores padrão sensatos. Defina apenas os campos relevantes para o teste, para que ele mostre o que importa.
- Não use desvios sobre o resultado para decidir o que verificar. Separe em testes distintos. Um desvio que nunca executa esconde as suas asserções.
