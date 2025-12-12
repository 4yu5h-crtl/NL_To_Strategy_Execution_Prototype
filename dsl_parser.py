from lark import Lark, Transformer
import ast_nodes as ast

dsl_grammar = r"""
    ?start: strategy

    strategy: rule+

    rule: "ENTRY:"i expression -> entry_rule
        | "EXIT:"i expression -> exit_rule

    ?expression: or_expr

    or_expr: and_expr (OR and_expr)*
    and_expr: comparison (AND comparison)*

    ?comparison: crossover_expr
               | crossunder_expr
               | cross_expr
               | simple_comp
               | "(" expression ")"

    simple_comp: atom COMP_OP atom
    cross_expr: "CROSS" "(" atom "," atom ")"
    crossover_expr: "CROSSOVER" "(" atom "," atom ")"
    crossunder_expr: "CROSSUNDER" "(" atom "," atom ")"

    ?atom: indicator
         | CNAME -> identifier
         | NUMBER -> number

    indicator: CNAME "(" [atom ("," atom)*] ")"

    COMP_OP: ">" | "<" | ">=" | "<=" | "=="
    OR: "OR"i
    AND: "AND"i

    %import common.CNAME
    %import common.NUMBER
    %import common.WS
    %ignore WS
"""

class AstTransformer(Transformer):
    """
    Transforms the parse tree created by Lark into a custom AST.
    """
    def strategy(self, items):
        return ast.Strategy(items)

    def entry_rule(self, items):
        return ast.EntryRule(items[0])

    def exit_rule(self, items):
        return ast.ExitRule(items[0])

    def or_expr(self, items):
        if len(items) == 1:
            return items[0]
        left, op, right = items
        return ast.LogicalOperation(op, left, right)

    def and_expr(self, items):
        if len(items) == 1:
            return items[0]
        left, op, right = items
        # Build a left-associative tree for chains of ANDs
        if isinstance(left, ast.LogicalOperation) and left.operator == op:
             left.operands.append(right)
             return left
        return ast.LogicalOperation(op, [left, right])
    
    def simple_comp(self, items):
        return ast.Comparison(items[1].value, items[0], items[2])

    def cross_expr(self, items):
        return ast.Cross(items[0], items[1])

    def crossover_expr(self, items):
        return ast.CrossOver(items[0], items[1])

    def crossunder_expr(self, items):
        return ast.CrossUnder(items[0], items[1])

    def indicator(self, items):
        return ast.Indicator(items[0].value, items[1:])

    def identifier(self, items):
        return ast.Identifier(items[0].value)
    
    def number(self, items):
        return ast.Number(float(items[0].value))

    # Define tokens so they can be used in the transformer
    def AND(self, token):
        return token.value

    def OR(self, token):
        return token.value

# Create the parser instance
dsl_parser = Lark(dsl_grammar, start='start', parser='lalr', transformer=AstTransformer())

def parse_dsl(dsl_string):
    """
    Parses a DSL string and returns the corresponding AST.
    """
    try:
        return dsl_parser.parse(dsl_string)
    except Exception as e:
        print(f"Error parsing DSL: {e}")
        return None