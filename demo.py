import pandas as pd
from dsl_parser import parse_dsl
from code_generator import PandasCodeGenerator
from backtest import run_backtest, print_results
from nl_to_structured import nl_to_dsl

# --- 1. Define Strategy in Natural Language ---
strategy_nl = "Buy when SMA(close, 10) crosses above SMA(close, 30) and sell when SMA(close, 30) crosses below SMA(close, 10)"

def main():
    """Main function to run the demonstration."""
    print("--- Starting Trading Strategy Engine Demo ---")
    print(f"\nNatural Language Input:\n'{strategy_nl}'")

    # --- Step 1: Convert Natural Language to DSL ---
    print("\n[Step 1/5] Converting Natural Language to DSL...")
    strategy_dsl = nl_to_dsl(strategy_nl)
    if not strategy_dsl:
        print("Failed to convert NL to DSL. Exiting.")
        return
    print("DSL generated successfully.")
    print(f"\nGenerated DSL:\n{strategy_dsl}")

    # --- Step 2: Load Data ---
    print("\n[Step 2/5] Loading historical data from sample_data_long.csv...")
    try:
        df = pd.read_csv('sample_data_long.csv', parse_dates=['Date'])
    except FileNotFoundError:
        print("sample_data_long.csv not found, trying sample_data.csv...")
        try:
            df = pd.read_csv('sample_data.csv', parse_dates=['Date'])
        except FileNotFoundError:
            print("Error: No sample data file found.")
            return
    print(f"Data loaded successfully. {len(df)} rows.")

    # --- Step 3: Parse DSL to AST ---
    print("\n[Step 3/5] Parsing DSL string into an Abstract Syntax Tree (AST)...")
    ast_tree = parse_dsl(strategy_dsl)
    if not ast_tree:
        print("Failed to parse DSL. Exiting.")
        return
    print("AST created successfully.")

    # --- Step 4: Generate Code from AST ---
    print("\n[Step 4/5] Generating Python/pandas code from AST...")
    generator = PandasCodeGenerator()
    generated_code = generator.generate(ast_tree)
    print("Code generated successfully.")
    print(f"\n--- Generated Indicator Code ---\n{generated_code['indicators']}")
    print(f"\n--- Generated Entry Code ---\n{generated_code['entry']}")
    print(f"\n--- Generated Exit Code ---\n{generated_code['exit']}")

    # --- Step 5: Run Backtest ---
    print("\n[Step 5/5] Running backtest simulation...")
    results = run_backtest(
        df=df.copy(),
        indicator_code=generated_code['indicators'],
        entry_code=generated_code['entry'],
        exit_code=generated_code['exit'],
        initial_capital=10000.0
    )

    # --- 6. Print Results ---
    print("\n--- Backtest Results ---")
    print_results(results)
    
    print("\n--- Demo Finished ---")

if __name__ == "__main__":
    main()