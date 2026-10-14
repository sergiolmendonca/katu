# Katu

> **katu** *(s.)* – o bem; coisa boa; bondade.
> — NAVARRO, Eduardo de Almeida. *Dicionário de tupi antigo: a língua indígena clássica do Brasil*, 2013.

Linguagem de programação didática, localizada em Tupi Antigo.

![Python](https://img.shields.io/badge/python-3.x-blue)
![Lark](https://img.shields.io/badge/parser-Lark-informational)

## Objetivo

A Katu é uma linguagem de programação com palavras-chave em Tupi Antigo, criada como **prova de conceito** para a valorização da língua e da cultura dos povos originários do Brasil diante da dominância do inglês e do viés colonial na ciência da computação.

## Como funciona

A Katu é uma linguagem **transpilada**: o código `.katu` é lido por um *parser* LALR construído com a biblioteca [Lark](https://github.com/lark-parser/lark), e uma árvore sintática é traduzida para Python, que então é executado.

```
código Katu  ──►  árvore sintática  ──►  código Python  ──►  execução
        análise            tradução               execução
```

- A gramática está em [`grammar.lark`](grammar.lark).
- A tradução está em [`tupi_lark.py`](tupi_lark.py).

## Como rodar

Requisitos: Python 3 e a biblioteca Lark.

```bash
pip install lark
```

Execute a partir da **raiz do projeto**, pois o programa lê o `grammar.lark` pelo diretório atual:

```bash
python tupi_lark.py exemplos/hello-world.katu
```

## Vocabulário

O vocabulário atualmente tem 22 palavras e pode ser consultado no arquivo [EBNF](documentos/katu.ebnf)

Regras básicas: cada instrução termina com `;`, blocos ficam entre `ypy` e `sykaba`, textos usam aspas duplas e comentários começam com `#`.

## Exemplo de código

### Olá, mundo

```
mba'e helloWorld îar "Olá Mundo!";

kûatiar(helloWorld);
```

Saída:

```
Olá Mundo!
```

Os demais programas estão em [`exemplos/`](exemplos/): `par-ou-impar`, `tabuada`, `operacoes`, `primo` e `adivinhar-numero`.

## Testes

Os programas-exemplo são verificados por uma suíte de testes em `pytest`. Cada teste transpila um `.katu`, executa o Python gerado com entradas simuladas e confere a saída.

```bash
pip install pytest
pytest -v
```
