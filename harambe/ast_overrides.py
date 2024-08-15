import ast
import inspect
import textwrap
from _ast import AST
from ast import NodeTransformer
from collections.abc import Callable
from typing import Any, TypedDict


class Locals(TypedDict):
    SDK: Any
    observer: Any


def float_override(value: Any) -> float:
    if isinstance(value, str):
        value = value.strip().replace("$", "").replace(",", "")
    return float(value)


class OverrideBuiltinsVisitor(NodeTransformer):
    def __init__(self) -> None:
        super().__init__()
        self.builtins = {}

    def register(self, builtin: Callable, replacement: Callable) -> None:
        self.builtins[builtin.__name__] = replacement.__name__

    def should_override(self, source_code: str) -> bool:
        for k in self.builtins.keys():
            if k in source_code:
                return True
        return False

    def visit_Name(self, node: AST) -> AST:
        if node.id in self.builtins:
            return ast.Name(id=self.builtins[node.id], ctx=node.ctx)
        return node


transformer = OverrideBuiltinsVisitor()
transformer.register(float, float_override)


def override_builtins(func: callable, locals_: Locals) -> callable:
    source_code = inspect.getsource(func)

    if not transformer.should_override(source_code):
        return func

    normalized_source = textwrap.dedent(source_code)
    tree = ast.parse(normalized_source)

    transformer.visit(tree)
    compiled = compile(ast.fix_missing_locations(tree), filename="<ast>", mode="exec")

    exec_globals = locals_.copy()
    exec_globals.update(
        {
            "float_override": float_override,
            func.__name__: func,
        }
    )

    exec(compiled, exec_globals)
    return exec_globals[func.__name__]
