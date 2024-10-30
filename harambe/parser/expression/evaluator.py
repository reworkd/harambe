from functools import wraps
from typing import Any


class ExpressionEvaluator:
    functions = {}

    @classmethod
    def register(cls, func_name: str):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            cls.functions[func_name.upper()] = wrapper
            return wrapper

        return decorator

    @staticmethod
    def evaluate(expression: str, obj: Any) -> Any:
        expression = expression.strip()

        if not expression:
            raise ValueError("Empty expression")

        if "(" not in expression and ")" not in expression:
            return ExpressionEvaluator._get_field_value(expression, obj)

        func_name = expression.split("(", 1)[0].strip().upper()
        if not func_name:
            raise ValueError("Invalid function name")

        if func_name not in ExpressionEvaluator.functions:
            raise ValueError(f"Unknown function: {func_name}")

        remaining = expression[len(func_name) :].strip()
        if not (remaining.startswith("(") and remaining.endswith(")")):
            raise SyntaxError(f"Invalid function call syntax: {expression}")

        args_str = remaining[1:-1]

        # Parse arguments handling nested functions
        args = []
        current_arg = ""
        paren_count = 0

        for char in args_str:
            if char == "(" and current_arg.strip():
                paren_count += 1
            elif char == ")":
                paren_count -= 1
            elif char == "," and paren_count == 0:
                if current_arg.strip():
                    args.append(current_arg.strip())
                current_arg = ""
                continue

            current_arg += char

        if paren_count != 0:
            raise SyntaxError(f"Invalid function call syntax: {expression}")

        if current_arg.strip():
            args.append(current_arg.strip())

        evaluated_args = []
        for arg in args:
            arg = arg.strip()
            if ExpressionEvaluator._is_string_literal(arg):
                evaluated_args.append(arg[1:-1])
            elif "(" in arg:
                evaluated_args.append(ExpressionEvaluator.evaluate(arg, obj))
            else:
                evaluated_args.append(ExpressionEvaluator._get_field_value(arg, obj))

        return ExpressionEvaluator.functions[func_name](*evaluated_args)

    @staticmethod
    def _is_string_literal(arg: str):
        return (arg.startswith("'") and arg.endswith("'")) or (
            arg.startswith('"') and arg.endswith('"')
        )

    @staticmethod
    def _get_field_value(field_path: str, obj: Any) -> Any:
        parts = field_path.strip().split(".")
        current = obj

        for part in parts:
            if "[" in part and "]" in part:
                split = part.split("[")
                part = split[0]

                if part not in current or not isinstance(current[part], list):
                    return None

                idx = split[1].rstrip("]")
                current = current[part][int(idx)]
            elif hasattr(current, part):
                current = getattr(current, part)
            elif isinstance(current, dict):
                current = current.get(part)
            else:
                return None

        return current
