import sys
from lark import Lark, Transformer, v_args


with open("grammar.lark", encoding="utf-8") as f:
    GRAMMAR = f.read()

parser = Lark(GRAMMAR, parser="lalr")


def _indent_block(code: str) -> str:
    return "\n".join("    " + line for line in code.split("\n"))

OPS = {
    "îakatutenhẽ": "==",
    "oîkoé": "!=",
    "a'yrĩ-eté": "<",
    "turusu-eté": ">",
}


@v_args(inline=True)
class ToPython(Transformer):

    def __init__(self):
        super().__init__()
        self.imports = set()

    def number(self, tok):
        v = float(tok)
        return str(int(v)) if v == int(v) else str(v)

    def string(self, tok):
        return repr(tok[1:-1])  

    def true(self):
        return "True"

    def false(self):
        return "False"

    def ident(self, tok):
        return str(tok)

    def add(self, a, b):
        return f"({a} + {b})"

    def sub(self, a, b):
        return f"({a} - {b})"

    def mul(self, a, b):
        return f"({a} * {b})"

    def div(self, a, b):
        return f"({a} / {b})"

    def mod(self, a, b):
            return f"({a} % {b})"

    def comparison(self, left, op=None, right=None):
        if op is None:
            return left
        return f"({left} {OPS[str(op)]} {right})"

    def import_stmt(self, name):
        return f"import {name}"

    def let_stmt(self, name, value):
        return f"{name} = {value}"

    def assign_stmt(self, name, value):
        return f"{name} = {value}"

    def print_stmt(self, value):
        return f"print({value})"
    
    def input_func(self, alternate=None):
        if alternate is not None:
            return f"input({alternate})"
        return f"input()"
    
    def rand_func(self, start, end):
        self.imports.add("random")
        return f"random.randint({start}, {end})"

    def to_str(self, value):
        return f"str({value})"

    def block(self, *stmts):
        return "\n".join(str(s) for s in stmts)

    def if_stmt(self, test, consequent, alternate=None):
        code = f"if {test}:\n{_indent_block(str(consequent))}"
        if alternate is not None:
            code += f"\n{alternate}"
        return code
    
    def else_if(self, test, consequent, alternate=None):
        code = f"elif {test}:\n{_indent_block(str(consequent))}"
        if alternate is not None:
            code += f"\n{alternate}"
        return code
    
    def else_block(self, body):
        code = f"else:\n{_indent_block(str(body))}"
        return code
    
    def or_op(self, a, b):
        return f"({a} or {b})"

    def and_op(self, a, b):
        return f"({a} and {b})"

    def not_op(self, a):
        return f"(not {a})"

    def while_stmt(self, test, body):
        return f"while {test}:\n{_indent_block(str(body))}"

    def stmt(self, s):
        return s

    def start(self, *stmts):
        header = "\n".join(f"import {m}" for m in sorted(self.imports))
        body = "\n".join(str(s) for s in stmts)
        return f"{header}\n{body}" if header else body


def transpile(source: str) -> str:
    tree = parser.parse(source)
    return ToPython().transform(tree)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python tupi_lark.py arquivo.tupi")
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        src = f.read()

    py_code = transpile(src)
    print(f"--- código Python gerado ---\n{py_code}\n")
    print("--- saída do programa ---")
    exec(py_code, {})
