import ast_nodes as ast
from dsl_parser import parse_dsl

class PandasCodeGenerator:
    """
    A visitor that traverses the AST and generates a Python/pandas expression.
    """
    def __init__(self):
        self.generated_indicators = set()
        self.indicator_code = []

    def generate(self, strategy_node):
        """
        Generates the full Python code for a given strategy AST.
        Returns a dictionary with code for pre-computation, entry, and exit signals.
        """
        self.generated_indicators = set()
        self.indicator_code = []
        
        entry_code = "False"
        exit_code = "False"

        for rule in strategy_node.rules:
            if isinstance(rule, ast.EntryRule):
                entry_code = self.visit(rule.condition)
            elif isinstance(rule, ast.ExitRule):
                exit_code = self.visit(rule.condition)
        
        return {
            "indicators": "\n".join(self.indicator_code),
            "entry": entry_code,
            "exit": exit_code
        }

    def visit(self, node):
        """Generic visit method that dispatches to the specific node visitor."""
        method_name = f"visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"No visit_{node.__class__.__name__} method")

    def visit_LogicalOperation(self, node):
        op = " & " if node.operator == "AND" else " | "
        # Visit each operand to generate its code
        operand_codes = [self.visit(operand) for operand in node.operands]
        # Join the codes with the operator
        return f"({op.join(operand_codes)})"

    def visit_Comparison(self, node):
        left_code = self.visit(node.left)
        right_code = self.visit(node.right)
        return f"({left_code} {node.operator} {right_code})"

    def visit_Cross(self, node):
        # Generic cross - defaults to crossover behavior
        left_code = self.visit(node.left)
        right_code = self.visit(node.right)
        return f"(({left_code}) > ({right_code})) & (({left_code}).shift(1) <= ({right_code}).shift(1))"

    def visit_CrossOver(self, node):
        # Crossover: left crosses ABOVE right
        left_code = self.visit(node.left)
        right_code = self.visit(node.right)
        return f"(({left_code}) > ({right_code})) & (({left_code}).shift(1) <= ({right_code}).shift(1))"

    def visit_CrossUnder(self, node):
        # Crossunder: left crosses BELOW right
        left_code = self.visit(node.left)
        right_code = self.visit(node.right)
        return f"(({left_code}) < ({right_code})) & (({left_code}).shift(1) >= ({right_code}).shift(1))"

    def visit_Indicator(self, node):
        params_str = '_'.join(str(p.name if isinstance(p, ast.Identifier) else p.value) for p in node.params)
        indicator_col_name = f"{node.name.lower()}_{params_str}"

        if indicator_col_name not in self.generated_indicators:
            param_code = ', '.join([self.visit(p) for p in node.params])
            code = f"df['{indicator_col_name}'] = indicators.{node.name.lower()}({param_code})"
            self.indicator_code.append(code)
            self.generated_indicators.add(indicator_col_name)
        
        return f"df['{indicator_col_name}']"

    def visit_Identifier(self, node):
        return f"df['{node.name}']"

    def visit_Number(self, node):
        return str(node.value)