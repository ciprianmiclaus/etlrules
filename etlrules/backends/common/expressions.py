import ast

from typing import Optional

from etlrules.exceptions import ExpressionSyntaxError


class Expression:
    def __init__(self, expression_str: str, filename: Optional[str]) -> None:
        self.filename = filename or "Expression.py"
        assert expression_str and isinstance(expression_str, str), f"expression_str cannot be empty in {self.filename}"
        self.expression_str = expression_str
        try:
            self._ast_expr = ast.parse(
                self.expression_str, filename=self.filename, mode='eval'
            )
            self._compiled_expr = compile(self._ast_expr, filename=self.filename, mode='eval')
        except SyntaxError as exc:
            raise ExpressionSyntaxError(f"Error in expression '{self.expression_str}': {str(exc)}")

    def eval(self, df):
        try:
            expr_series = eval(self._compiled_expr, {}, {'df': df})
        except TypeError:
            # attempt to run a slower apply
            expr = self._compiled_expr
            expr_series = df.apply(lambda df: eval(expr, {}, {'df': df}), axis=1)
        return expr_series
