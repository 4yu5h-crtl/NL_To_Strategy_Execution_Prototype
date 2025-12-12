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

For complete DSL documentation including grammar rules, operators, indicators, cross detection logic, design decisions, and extension guide, see **[dsl_spec.md](dsl_spec.md)**.

**Quick Reference:**
```
ENTRY: close > SMA(close, 20) AND volume > 1000000
EXIT: RSI(close, 14) < 30
```

---

## Architecture Overview

### **Pipeline Components**

1. **Natural Language Parser** (`nl_to_structured.py`)
   - Converts natural language to structured JSON representation
   - Uses regex-based pattern matching for common trading phrases
   - Preserves semantic meaning (e.g., "crosses above" vs "crosses below")

2. **DSL Generator** (`nl_to_structured.py`)
   - Transforms structured JSON into DSL text
   - Emits directional cross operators (`CROSSOVER`/`CROSSUNDER`)

3. **DSL Parser** (`dsl_parser.py`)
   - Lark-based LALR parser with formal grammar
   - Validates syntax and builds Abstract Syntax Tree
   - Provides informative error messages

4. **AST Nodes** (`ast_nodes.py`)
   - Defines typed node classes for the AST
   - Node types: `Strategy`, `EntryRule`, `ExitRule`, `CrossOver`, `Comparison`, `LogicalOperation`, `Indicator`, etc.

5. **Code Generator** (`code_generator.py`)
   - Visitor pattern to traverse AST
   - Generates executable pandas/Python expressions
   - Pre-computes indicators and handles signal logic

6. **Backtest Simulator** (`backtest.py`)
   - Event-driven backtesting engine
   - Tracks positions, entry/exit signals
   - Calculates performance metrics: P&L, drawdown, win rate

---

## Backtest Metrics

The backtest simulator calculates the following metrics:

- **Entry/Exit Dates**: Timestamp of each trade
- **Entry/Exit Prices**: Execution price (close price)
- **Profit/Loss**: Dollar and percentage return per trade
- **Total Return**: Overall portfolio performance
- **Max Drawdown**: Largest peak-to-trough decline
- **Number of Trades**: Total completed trades
- **Win Rate**: Percentage of profitable trades

---

## Sample Data

`sample_data_long.csv` contains 200 rows of synthetic OHLCV data:
- **Date range**: 2023-01-01 to 2023-07-19
- **Price range**: ~$93 to ~$119
- **Characteristics**: Trending behavior to ensure SMA crossovers occur

**Format:**
```csv
Date,open,high,low,close,volume
2023-01-01,100.5,102.3,99.8,101.2,1050000
...
```

---

## Extending the System

### **Add a New Indicator**

1. Implement function in `utils/indicators.py`
2. Update NL parser in `nl_to_structured.py` to recognize the indicator
3. Add visitor method in `code_generator.py`
4. Update DSL grammar in `dsl_parser.py` if needed
5. Document in `dsl_spec.md`

### **Add a New Operator**

1. Update DSL grammar in `dsl_parser.py`
2. Add corresponding AST node in `ast_nodes.py`
3. Implement visitor method in `code_generator.py`
4. Document in `dsl_spec.md`

See `dsl_spec.md` for detailed extension examples.

---

## Testing

Run the demo script to validate the entire pipeline:

```bash
python demo.py
```

**What it tests:**
- ✅ Natural language → DSL conversion
- ✅ DSL parsing and validation
- ✅ AST construction
- ✅ Python code generation
- ✅ Indicator computation
- ✅ Entry/exit signal detection
- ✅ Backtest execution and metrics

**Expected output:**
- Generated DSL text
- Generated Python code
- Signal counts
- Trade log with entry/exit details
- Performance summary

---

## Limitations & Assumptions

### **Natural Language Parsing**
- Supports specific patterns (not a full NLP engine)
- Uses regex-based matching for common trading phrases
- See `nl_to_structured.py` for supported patterns

### **Backtesting**
- Simple event-driven model
- No slippage, commissions, or position sizing
- Assumes fills at close price
- Long-only positions (no short selling)

### **Data Requirements**
- OHLCV format with columns: `Date`, `open`, `high`, `low`, `close`, `volume`
- Assumes daily frequency (can be adapted)
- No handling of missing data

### **Indicators**
- Currently supports SMA and RSI
- Easily extensible (see "Extending the System")

---

## Dependencies

- **pandas**: Data manipulation and time-series operations
- **lark**: DSL parsing with LALR grammar
- **numpy**: Numerical computations (used in indicators)

Install all dependencies:
```bash
pip install -r requirements.txt
```

---

## Assignment Deliverables

This project fulfills all required deliverables:

1. ✅ **DSL Design Document** - See `dsl_spec.md`
2. ✅ **NL → Structured Representation** - `nl_to_structured.py`
3. ✅ **DSL Parser + AST Builder** - `dsl_parser.py` + `ast_nodes.py`
4. ✅ **AST → Python Generator** - `code_generator.py`
5. ✅ **Backtest Simulator** - `backtest.py`
6. ✅ **End-to-End Demo** - `demo.py`
7. ✅ **README with Instructions** - This file

---
