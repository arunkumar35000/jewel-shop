"""
👑 AURA Jewellery - Standalone Interactive Terminal Database Explorer
Works in ANY Python environment (with or without venv/django activated).
Uses Python's built-in sqlite3 standard library with zero external dependencies.

Usage:
  python db_cli.py
  or
  .\venv\Scripts\python.exe db_cli.py
"""
import os
import sys
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Check if running outside venv, and try to re-exec with venv python if available
venv_python = BASE_DIR / 'venv' / 'Scripts' / 'python.exe'
if venv_python.exists() and sys.executable.lower() != str(venv_python).lower():
    try:
        import subprocess
        # Re-launch with project virtual environment
        sys.exit(subprocess.call([str(venv_python)] + sys.argv))
    except Exception:
        pass

# If here, connect directly using Python's built-in sqlite3 (requires ZERO external packages)
db_path = BASE_DIR / 'db.sqlite3'
if not db_path.exists():
    print(f"Error: Database file not found at {db_path}")
    sys.exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

def print_help():
    print("""
Available Commands:
  tables             - List all database tables and row counts
  describe <table >  - Show table columns and data types
  select ...         - Execute any SQL query (e.g. SELECT * FROM products_product LIMIT 3;)
  products           - Quick view of products
  orders             - Quick view of recent orders
  payments           - Quick view of payment transactions
  users              - Quick view of registered users
  help               - Show this help menu
  exit / quit        - Exit the shell
""")

def list_tables():
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE 'django_%' AND name NOT LIKE 'auth_permission%' AND name NOT LIKE 'auth_group%' ORDER BY name;")
    tables = [row[0] for row in cursor.fetchall()]
    print("\n--- DATABASE TABLES ---")
    for t in tables:
        cursor.execute(f'SELECT COUNT(*) FROM [{t}]')
        cnt = cursor.fetchone()[0]
        print(f"  {t:<35} : {cnt:>4} rows")
    print(f"\nTotal Application Tables: {len(tables)}\n")

def describe_table(table_name):
    try:
        cursor.execute(f"PRAGMA table_info([{table_name}])")
        columns = cursor.fetchall()
        if not columns:
            print(f"Table '{table_name}' not found.\n")
            return
        print(f"\n--- COLUMNS IN [{table_name}] ---")
        for col in columns:
            # col[1] is name, col[2] is type, col[5] is primary key
            pk = " (PK)" if col[5] else ""
            print(f"  Column: {col[1]:<25} | Type: {col[2]}{pk}")
        print()
    except Exception as e:
        print(f"Error: {e}\n")

def run_query(query):
    try:
        cursor.execute(query)
        if cursor.description:
            headers = [d[0] for d in cursor.description]
            rows = cursor.fetchall()
            if not rows:
                print("\n(0 rows returned)\n")
                return
            print("\n" + " | ".join(f"{h:<20}" for h in headers))
            print("-" * (len(headers) * 23))
            for row in rows[:20]:
                print(" | ".join(f"{str(val)[:18]:<20}" for val in row))
            if len(rows) > 20:
                print(f"... and {len(rows) - 20} more rows")
            print(f"\n({len(rows)} rows returned)\n")
        else:
            conn.commit()
            print("Query executed successfully.\n")
    except Exception as e:
        print(f"SQL Error: {e}\n")

def main():
    print("=" * 65)
    print("👑 AURA JEWELLERY - TERMINAL DATABASE EXPLORER (SQLITE)")
    print(f"Database File: {db_path.name}")
    print("=" * 65)
    print_help()

    while True:
        try:
            cmd = input("AuraDB> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not cmd:
            continue

        lower_cmd = cmd.lower()
        if lower_cmd in ['exit', 'quit', 'q']:
            print("Goodbye!")
            break
        elif lower_cmd == 'help':
            print_help()
        elif lower_cmd in ['tables', 'show tables']:
            list_tables()
        elif lower_cmd.startswith('describe '):
            tbl = cmd.split(None, 1)[1].strip()
            describe_table(tbl)
        elif lower_cmd == 'products':
            run_query("SELECT id, name, metal_type, purity, base_price, stock FROM products_product LIMIT 10")
        elif lower_cmd == 'orders':
            run_query("SELECT order_number, customer_name, grand_total, order_status, payment_status FROM orders_order LIMIT 10")
        elif lower_cmd == 'payments':
            run_query("SELECT transaction_id, payment_method, amount, status, created_at FROM orders_payment LIMIT 10")
        elif lower_cmd == 'users':
            run_query("SELECT id, username, email, is_staff, date_joined FROM auth_user")
        else:
            run_query(cmd)

if __name__ == '__main__':
    main()
