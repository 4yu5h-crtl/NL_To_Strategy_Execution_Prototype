# NLP → DSL → Strategy Execution Prototype

This project implements a complete pipeline to convert natural language trading instructions into a domain-specific language (DSL), parse it into an Abstract Syntax Tree (AST), generate executable Python code, and run a backtest simulation.

---

## Project Structure

```
.
├── ast_nodes.py              # AST node definitions
├── backtest.py               # Backtest simulator
├── code_generator.py         # AST → Python code generator
├── demo.py                   # End-to-end demonstration script
├── dsl_parser.py             # DSL parser (uses Lark)
├── dsl_spec.md               # DSL grammar specification
├── nl_to_structured.py       # Natural language → DSL converter
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── sample_data_long.csv      # Sample OHLCV data (200 rows)
└── utils/
    └── indicators.py         # Indicator functions (SMA, RSI)
```

---

## Setup

**Requirements**: Python 3.7+

1. **Clone or download** this repository
2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

Run the end-to-end demonstration:

```bash
python demo.py
```

This will:
1. Accept a natural language trading strategy
2. Convert it to DSL format
3. Parse DSL into an AST
4. Generate Python/pandas code
5. Execute the code over sample OHLCV data
6. Run a backtest simulation
7. Display performance results

---

## Example Pipeline

### **Input: Natural Language**
```
Buy when SMA(close, 10) crosses above SMA(close, 30) and 
sell when SMA(close, 30) crosses below SMA(close, 10)
```

### **Step 1: Generated DSL**
```
ENTRY: CROSSOVER(SMA(close, 10), SMA(close, 30))
EXIT: CROSSUNDER(SMA(close, 30), SMA(close, 10))
```

### **Step 2: Parsed AST**
```python
Strategy(
  rules=[
    EntryRule(condition=CrossOver(...)),
    ExitRule(condition=CrossUnder(...))
  ]
)
```

### **Step 3: Generated Python Code**
```python
# Indicators
df['sma_close_10.0'] = indicators.sma(df['close'], 10.0)
df['sma_close_30.0'] = indicators.sma(df['close'], 30.0)

# Entry signal
entry = ((df['sma_close_10.0']) > (df['sma_close_30.0'])) & \
        ((df['sma_close_10.0']).shift(1) <= (df['sma_close_30.0']).shift(1))

# Exit signal
exit = ((df['sma_close_30.0']) < (df['sma_close_10.0'])) & \
       ((df['sma_close_30.0']).shift(1) >= (df['sma_close_10.0']).shift(1))
```

### **Step 4: Backtest Results**
```
--- Backtest Performance Summary ---
Final Equity:      $10,007.55
Total Profit:      $7.55 (0.08%)
Max Drawdown:      0.12%
------------------------------
Total Trades:      3
Winning Trades:    2
Win Rate:          66.67%
```

---

## DSL Specification

See **[dsl_spec.md](dsl_spec.md)** for complete grammar documentation.

### **Supported Features**

**Operators:**
- Comparison: `>`, `<`, `>=`, `<=`, `==`
- Logical: `AND`, `OR`
- Cross: `CROSSOVER`, `CROSSUNDER`, `CROSS`

**Indicators:**
- `SMA(series, period)` - Simple Moving Average
- `RSI(series, period)` - Relative Strength Index

**Data Fields:**
- `close`, `open`, `high`, `low`, `volume`

**Example DSL:**
```
ENTRY: close > SMA(close, 20) AND volume > 1000000
EXIT: RSI(close, 14) < 30
```

---

## Architecture

### **1. Natural Language Parsing** (`nl_to_structured.py`)
- Uses regex-based pattern matching
- Converts NL to structured JSON
- Preserves semantic meaning (e.g., "crosses above" vs "crosses below")

### **2. DSL Generation** (`nl_to_structured.py`)
- Converts structured JSON to DSL text
- Emits `CROSSOVER`/`CROSSUNDER` for directional crosses

### **3. DSL Parsing** (`dsl_parser.py`)
- Uses Lark parser with LALR grammar
- Validates syntax
- Builds Abstract Syntax Tree

### **4. AST Nodes** (`ast_nodes.py`)
- Defines node types: `Strategy`, `EntryRule`, `ExitRule`, `CrossOver`, `CrossUnder`, `Comparison`, `LogicalOperation`, `Indicator`, etc.

### **5. Code Generation** (`code_generator.py`)
- Visitor pattern to traverse AST
- Generates pandas/Python expressions
- Handles indicator pre-computation

### **6. Backtesting** (`backtest.py`)
- Simple event-driven simulator
- Tracks entry/exit signals
- Calculates P&L, drawdown, win rate

---

## Cross Detection Logic

**Crossover** (A crosses above B):
```python
(A > B) & (A.shift(1) <= B.shift(1))
```

**Crossunder** (A crosses below B):
```python
(A < B) & (A.shift(1) >= B.shift(1))
```

This ensures we detect the exact moment when one series crosses another.

---

## Sample Data

`sample_data_long.csv` contains 200 rows of synthetic OHLCV data with:
- Date range: 2023-01-01 to 2023-07-19
- Price range: ~$93 to ~$119
- Trending behavior to ensure SMA crossovers occur

Format:
```csv
Date,open,high,low,close,volume
2023-01-01,100.5,102.3,99.8,101.2,1050000
...
```

---

## Design Decisions

### **1. Why CROSSOVER/CROSSUNDER instead of CROSS?**
- Preserves semantic direction from natural language
- Avoids ambiguity in cross detection
- Makes DSL more explicit and readable

### **2. Why Lark for parsing?**
- Clean grammar definition
- Built-in AST transformation
- Good error messages
- LALR parser is efficient

### **3. Why visitor pattern for code generation?**
- Clean separation of concerns
- Easy to extend with new node types
- Follows compiler design best practices

### **4. Why pandas for backtesting?**
- Vectorized operations are fast
- Natural fit for time-series data
- Easy indicator computation with `.rolling()`, `.shift()`, etc.

---

## Extending the System

### **Add a new indicator:**

1. Add function to `utils/indicators.py`:
```python
def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period).mean()
```

2. Update NL parser to recognize "EMA" patterns

3. Add visitor method to code generator:
```python
def visit_Indicator(self, node):
    if node.name == 'EMA':
        # handle EMA
```

### **Add a new operator:**

1. Update DSL grammar in `dsl_parser.py`
2. Add AST node in `ast_nodes.py`
3. Add visitor method in `code_generator.py`

---

## Limitations & Assumptions

1. **Natural Language Parsing**: 
   - Supports specific patterns (see examples)
   - Not a full NLP engine
   - Uses regex-based matching

2. **Backtesting**:
   - Simple event-driven model
   - No slippage, commissions, or position sizing
   - Assumes fills at close price

3. **Data**:
   - Requires OHLCV format
   - Assumes daily frequency
   - No handling of missing data

4. **Indicators**:
   - Currently supports SMA and RSI
   - Can be extended easily

---

## Testing

The demo script (`demo.py`) serves as the main test. It demonstrates:
- ✅ NL → DSL conversion
- ✅ DSL parsing
- ✅ AST construction
- ✅ Code generation
- ✅ Indicator computation
- ✅ Signal detection
- ✅ Backtest execution

Expected output shows:
- Generated DSL
- Generated code
- Signal counts
- Trade details
- Performance metrics

---
