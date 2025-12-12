# Trading Strategy DSL Specification

This document outlines the syntax and structure of the Domain-Specific Language (DSL) used for defining trading strategies. The DSL provides a simple, human-readable format to specify entry and exit conditions for a backtesting engine.

## 1. Syntax Format

A strategy is defined by at least one of two main clauses: `ENTRY` and `EXIT`.

-   **`ENTRY`**: Defines the conditions under which a long position should be opened.
-   **`EXIT`**: Defines the conditions under which a long position should be closed.

Each clause is followed by a colon (`:`) and one or more conditions.

```
ENTRY: <conditions>
EXIT: <conditions>
```

## 2. Grammar Rules

### 2.1. Conditions

Conditions are boolean expressions that evaluate to true or false. Multiple conditions can be combined using logical operators.

-   **Logical Operators**: `AND`, `OR`
-   Parentheses `()` can be used to group conditions and control the order of evaluation.

### 2.2. Expressions

The fundamental building block of a condition is a comparison expression.

-   **Structure**: `operand operator operand`
-   **Comparison Operators**: `>`, `<`, `>=`, `<=`, `==`

### 2.3. Operands

Operands can be one of the following:

-   **Identifier**: Represents a data column from the input dataset (e.g., `close`, `open`, `high`, `low`, `volume`).
-   **Number**: An integer or floating-point value (e.g., `100`, `3.14`).
-   **Indicator**: A function call that calculates a technical indicator value.

### 2.4. Indicators

Indicators are specified with a function-call syntax.

-   **Syntax**: `INDICATOR_NAME(param1, param2, ...)`

**Supported Indicators:**

-   `SMA(source, period)`: Simple Moving Average.
    -   `source`: The data column to use (e.g., `close`).
    -   `period`: The lookback window (integer).
-   `RSI(source, period)`: Relative Strength Index.
    -   `source`: The data column to use (e.g., `close`).
    -   `period`: The lookback window (integer).
-   `CROSS(series1, series2)`: A special boolean expression that returns `true` on the bar where `series1` crosses above `series2`.
    -   `series1`, `series2`: Can be identifiers or other indicators.

## 3. Examples

### Example 1: Simple SMA Crossover and Volume

Buy when the closing price is above its 20-period SMA and trading volume is over 1 million. Exit when the 14-period RSI is below 30.

```
ENTRY: close > SMA(close, 20) AND volume > 1000000
EXIT: RSI(close, 14) < 30
```

### Example 2: Golden Cross

A classic "golden cross" strategy. Buy when the 50-period SMA crosses above the 200-period SMA. Exit when the opposite "death cross" occurs.

```
ENTRY: CROSS(SMA(close, 50), SMA(close, 200))
EXIT: CROSS(SMA(close, 200), SMA(close, 50))
```

### Example 3: Combined Logic with OR

Enter a position if the RSI is overbought or if the price breaks a key resistance level.

```
ENTRY: RSI(close, 14) > 70 OR close > 150.50
EXIT: close < SMA(close, 10)
```

### Example 4: Grouped Conditions

A more complex strategy combining multiple conditions with grouping.

```
ENTRY: (SMA(close, 10) > SMA(close, 20) AND RSI(close, 14) > 50) OR (close > 100 AND volume > 500000)
EXIT: RSI(close, 14) < 40
```
