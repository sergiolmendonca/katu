import io
import random
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import pytest
from lark.exceptions import UnexpectedInput

from tupi_lark import transpile

RAIZ = Path(__file__).resolve().parent.parent

PASTA = next(p for p in (RAIZ / "exemplos", RAIZ / "examples", RAIZ) if p.is_dir())

def ler(nome: str) -> str:
    return (PASTA / f"{nome}.katu").read_text(encoding="utf-8")


def transpilar(fonte: str) -> str:
    with redirect_stdout(io.StringIO()):
        return transpile(fonte)


class Execucao:
    def __init__(self, linhas, codigo, chamadas_sorteio):
        self.linhas = linhas                       # saída, linha a linha
        self.codigo = codigo                       # Python gerado
        self.chamadas_sorteio = chamadas_sorteio   # argumentos de random.randint


def rodar(nome: str, entradas=(), sorteios=()) -> Execucao:
    codigo = transpilar(ler(nome))
    fila_entradas, fila_sorteios = iter(entradas), iter(sorteios)
    chamadas = []

    def input_falso(prompt=""):
        try:
            valor = next(fila_entradas)
        except StopIteration:
            raise AssertionError("o programa pediu mais entradas do que o teste forneceu")
        print(f"{prompt}{valor}")
        return valor

    def randint_falso(a, b):
        chamadas.append((a, b))
        try:
            return next(fila_sorteios)
        except StopIteration:
            raise AssertionError("o programa sorteou mais vezes do que o teste previa")

    saida = io.StringIO()
    with patch("builtins.input", input_falso), \
         patch.object(random, "randint", randint_falso), \
         redirect_stdout(saida):
        exec(compile(codigo, f"<{nome}>", "exec"), {})
    return Execucao(saida.getvalue().splitlines(), codigo, chamadas)

def test_hello_world_saida():
    assert rodar("hello-world").linhas == ["Olá Mundo!"]


def test_hello_world_codigo_gerado():
    assert transpilar(ler("hello-world")) == (
        "katu_helloWorld = 'Olá Mundo!'\n"
        "print(katu_helloWorld)"
    )

@pytest.mark.parametrize("n, esperado", [
    (0, "Zero é par"),
    (4, "4 é par"),
    (10, "10 é par"),
    (7, "7 é ímpar"),
    (-3, "-3 é ímpar"),
])
def test_par_ou_impar(n, esperado):
    assert rodar("par-ou-impar", [str(n)]).linhas[-1] == esperado

def _tabela(linhas):
    return [l for l in linhas if " x " in l]


@pytest.mark.parametrize("n", [1, 7, 10])
def test_tabuada_valida(n):
    r = rodar("tabuada", [str(n)])
    assert _tabela(r.linhas) == [f"{n} x {i} = {n * i}" for i in range(1, 11)]
    assert "Número inválido" not in r.linhas


@pytest.mark.parametrize("invalidos", [["0"], ["11"], ["-5"], ["0", "11"]])
def test_tabuada_rejeita_fora_do_intervalo_e_pede_de_novo(invalidos):
    r = rodar("tabuada", invalidos + ["5"])
    assert r.linhas.count("Número inválido") == len(invalidos)
    assert _tabela(r.linhas) == [f"5 x {i} = {5 * i}" for i in range(1, 11)]

def _esperado_operacoes(soma, sub, mul, div):
    return [
        "A soma dos 2 números é: ", soma,
        "A subtração dos 2 números é: ", sub,
        "A multiplicação dos 2 números é: ", mul,
        "A divisão dos 2 números é: ", div,
    ]


@pytest.mark.parametrize("a, b, resultados", [
    (12, 4, ("16", "8", "48", "3.0")),
    (7, 2, ("9", "5", "14", "3.5")),
    (-6, 3, ("-3", "-9", "-18", "-2.0")),
    (0, 5, ("5", "-5", "0", "0.0")),
])
def test_operacoes(a, b, resultados):
    r = rodar("operacoes", [str(a), str(b)])
    assert r.linhas[4:] == _esperado_operacoes(*resultados)

@pytest.mark.parametrize("n", [2, 3, 5, 7, 97, 997])
def test_primo_reconhece_primos(n):
    r = rodar("primo", [str(n)])
    assert r.linhas[-1] == "O número é primo."
    assert not any("não é primo" in l for l in r.linhas)


@pytest.mark.parametrize("n, menor_divisor", [(4, 2), (9, 3), (91, 7), (1000, 2)])
def test_primo_reconhece_nao_primos(n, menor_divisor):
    r = rodar("primo", [str(n)])
    assert r.linhas[-1] == f"O número não é primo. É divisível por {menor_divisor} também."
    assert "O número é primo." not in r.linhas


def test_primo_rejeita_fora_do_intervalo_e_pede_de_novo():
    r = rodar("primo", ["1", "0", "1001", "7"])
    assert r.linhas.count("Número inválido") == 3
    assert r.linhas[-1] == "O número é primo."

def test_adivinhar_numero_dicas_e_acerto():
    r = rodar("adivinhar-numero", ["3", "9", "7", "N"], sorteios=[7])
    dicas = [l for l in r.linhas if l.startswith("Número errado")]
    assert dicas == [
        "Número errado. É um pouco maior",   # chute 3 < 7
        "Número errado. É um pouco menor",   # chute 9 > 7
    ]
    assert "Parabéns, você acertou em 3 tentativa(s)! o número era 7" in r.linhas
    assert r.linhas[-1] == "Fim de jogo"


def test_adivinhar_numero_sorteia_entre_1_e_10():
    r = rodar("adivinhar-numero", ["7", "N"], sorteios=[7])
    assert r.chamadas_sorteio == [(1, 10)]


def test_adivinhar_numero_jogar_novamente_sorteia_outro_e_zera_tentativas():
    r = rodar("adivinhar-numero", ["7", "S", "3", "N"], sorteios=[7, 3])
    assert [l for l in r.linhas if l.startswith("Parabéns")] == [
        "Parabéns, você acertou em 1 tentativa(s)! o número era 7",
        "Parabéns, você acertou em 1 tentativa(s)! o número era 3",
    ]
    assert len(r.chamadas_sorteio) == 2
    assert r.linhas[-1] == "Fim de jogo"


def test_adivinhar_numero_so_aceita_S_maiusculo_para_continuar():
    # a comparação com "S" diferencia maiúsculas de minúsculas
    r = rodar("adivinhar-numero", ["7", "s"], sorteios=[7])
    assert len([l for l in r.linhas if l.startswith("Parabéns")]) == 1
    assert r.linhas[-1] == "Fim de jogo"


def test_comentario_de_linha_e_ignorado():
    fonte = ler("adivinhar-numero")
    assert "#" in fonte  # o programa tem mesmo um comentário
    sem_comentarios = "\n".join(l for l in fonte.splitlines() if not l.strip().startswith("#"))
    assert transpilar(fonte) == transpilar(sem_comentarios)


def test_comentario_no_fim_da_linha_e_ignorado():
    assert transpilar("mba'e a îar 1; # um comentário\n") == "katu_a = 1"


def test_apostrofo_em_nome_de_variavel_vira_sublinhado():
    assert transpilar("mba'e parar' îar eté;") == "katu_parar_ = True"


def test_precedencia_dos_operadores():
    assert transpilar("mba'e x îar 2 + 3 * 4;") == "katu_x = (2 + (3 * 4))"


def test_sorteio_adiciona_import_random():
    codigo = transpilar("mba'e x îar katu'ok(1, 6);")
    assert codigo.splitlines()[0] == "import random"
    assert "random.randint(1, 6)" in codigo


@pytest.mark.parametrize("fonte", [
    "mba'e x îar 1",
    "mba'e x îar ;",
    "mba'e x îar @;",
    "emonãneme (eté) kûatiar(1);",
])
def test_programa_invalido_e_rejeitado(fonte):
    with pytest.raises(UnexpectedInput):
        transpilar(fonte)
