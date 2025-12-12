import json
import re

def parse_number(s):
    """Converts numbers like '1M' to 1000000 or '10k' to 10000."""
    s = str(s).lower().strip()
    if s.endswith('m'):
        return int(float(s[:-1]) * 1_000_000)
    if s.endswith('k'):
        return int(float(s[:-1]) * 1_000)
    try:
        return float(s)
    except ValueError:
        return s

def parse_operand(op_str):
    """Parses an operand string, which can be a number, an indicator, or a column name."""
    op_str = op_str.strip()
    
    # Check for indicator first
    indicator_match = re.match(r'(SMA|RSI)\s*\(([^)]*)\)', op_str, re.IGNORECASE)
    if indicator_match:
        name, params_str = indicator_match.groups()
        params = [p.strip() for p in params_str.split(',')]
        return {"indicator": name.upper(), "params": [params[0].lower(), int(params[1])]}

    # Check for number
    if re.fullmatch(r'[\d\.]+[mk]?', op_str, re.IGNORECASE):
        return parse_number(op_str)
        
    # Assume column name
    return op_str.lower()


def nl_to_json(nl_query):
    """Converts a natural language query to a structured JSON format."""
    structured_query = {"entry": [], "exit": []}
    
    operator_map = {
        "crosses above": "CROSS_ABOVE",
        "crosses below": "CROSS_BELOW",
        "is above": ">",
        "is below": "<",
        "above": ">",
        "below": "<",
        "equals": "==",
        ">": ">",
        "<": "<",
        "==": "==",
    }
    operators_regex = '|'.join(sorted(operator_map.keys(), key=len, reverse=True))

    exit_keywords = r'\s+(?:and\s+)?(?:sell|exit)(?:\s+(?:when|if))?\s+'
    parts = re.split(exit_keywords, nl_query, maxsplit=1, flags=re.IGNORECASE)

    entry_text = parts[0]
    exit_text = parts[1] if len(parts) > 1 else ""
    entry_text = re.sub(r'^(?:buy|entry)(?:\s+(?:when|if))?\s+', '', entry_text, flags=re.IGNORECASE).strip()

    clauses = []
    if entry_text:
        clauses.append(("entry", entry_text))
    if exit_text:
        clauses.append(("exit", exit_text))
    
    for action, clause_text in clauses:
        conditions = re.split(r'\s+and\s+', clause_text.strip(), flags=re.IGNORECASE)
        for cond_text in conditions:
            cond_text = cond_text.strip()
            if not cond_text:
                continue
            
            match = re.match(r'(.*?)\s+(' + operators_regex + r')\s+(.*)', cond_text, re.IGNORECASE)

            if match:
                left_str, op_str, right_str = match.groups()
                condition = {
                    "left": parse_operand(left_str),
                    "operator": operator_map[op_str.lower()],
                    "right": parse_operand(right_str),
                }
                structured_query[action].append(condition)
    return structured_query

def format_operand(operand):
    """Converts a JSON operand object back into a DSL string fragment."""
    if isinstance(operand, str):
        return operand
    if isinstance(operand, (int, float)):
        return str(operand)
    if 'indicator' in operand:
        params = ', '.join(map(str, operand['params']))
        return f"{operand['indicator']}({params})"
    return ""

def json_to_dsl(structured_json):
    """Converts the structured JSON object into a DSL string."""
    dsl_parts = []
    for action in ['entry', 'exit']:
        if structured_json.get(action):
            conditions = []
            for cond in structured_json[action]:
                op = cond['operator']
                left = format_operand(cond['left'])
                right = format_operand(cond['right'])
                
                if op == "CROSS_ABOVE":
                    conditions.append(f"CROSSOVER({left}, {right})")
                elif op == "CROSS_BELOW":
                    conditions.append(f"CROSSUNDER({left}, {right})")
                else:
                    conditions.append(f"{left} {op} {right}")
            
            dsl_parts.append(f"{action.upper()}: {' AND '.join(conditions)}")
    return '\n'.join(dsl_parts)

def nl_to_dsl(nl_query):
    """
    High-level function to convert a natural language query directly into a 
    dictionary of DSL strings for entry and exit.
    """
    structured_json = nl_to_json(nl_query)
    return json_to_dsl(structured_json)
