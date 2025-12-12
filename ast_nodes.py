class Node:
    """Base class for all AST nodes."""
    def __repr__(self):
        return f"{self.__class__.__name__}(...)"

class Strategy(Node):
    """Root node of the AST, containing a list of rules."""
    def __init__(self, rules):
        self.rules = rules  # List of EntryRule or ExitRule

class EntryRule(Node):
    """Represents an 'ENTRY' clause and its condition."""
    def __init__(self, condition):
        self.condition = condition

class ExitRule(Node):
    """Represents an 'EXIT' clause and its condition."""
    def __init__(self, condition):
        self.condition = condition

class LogicalOperation(Node):
    """Represents a logical 'AND' or 'OR' operation with multiple operands."""
    def __init__(self, operator, operands):
        self.operator = operator # "AND" or "OR"
        self.operands = operands

class Comparison(Node):
    """Represents a comparison (e.g., 'close > 100')."""
    def __init__(self, operator, left, right):
        self.operator = operator  # ">", "<", "==", etc.
        self.left = left
        self.right = right

class Cross(Node):
    """Represents a 'CROSS' operation."""
    def __init__(self, left, right):
        self.left = left
        self.right = right

class CrossOver(Node):
    """Represents a 'CROSSOVER' operation (left crosses above right)."""
    def __init__(self, left, right):
        self.left = left
        self.right = right

class CrossUnder(Node):
    """Represents a 'CROSSUNDER' operation (left crosses below right)."""
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Indicator(Node):
    """Represents an indicator call (e.g., 'SMA(close, 20)')."""
    def __init__(self, name, params):
        self.name = name.upper()
        self.params = params

class Identifier(Node):
    """Represents a column name or other identifier."""
    def __init__(self, name):
        self.name = name

class Number(Node):
    """Represents a numeric literal."""
    def __init__(self, value):
        self.value = float(value)

