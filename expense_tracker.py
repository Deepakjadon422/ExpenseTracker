#!/usr/bin/env python3
import argparse
import json
import sys
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "expenses.json"

def load_expenses():
    if not DATA_FILE.exists():
        return []
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("Data file must contain a JSON array.")
        return data
    except (json.JSONDecodeError, OSError, ValueError) as e:
        print(f"Error reading expense data: {e}", file=sys.stderr)
        sys.exit(1)

def save_expenses(expenses):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = DATA_FILE.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(expenses, f, indent=2)
        f.write("\n")
    tmp.replace(DATA_FILE)

def next_id(expenses):
    return max((int(e["id"]) for e in expenses), default=0) + 1

def parse_amount(value):
    try:
        amount = Decimal(str(value))
    except InvalidOperation:
        raise ValueError("Amount must be a valid number.")
    if amount <= 0:
        raise ValueError("Amount must be greater than 0.")
    if amount.as_tuple().exponent < -2:
        raise ValueError("Amount can have at most 2 decimal places.")
    return float(amount)

def find_expense(expenses, expense_id):
    for e in expenses:
        if int(e["id"]) == expense_id:
            return e
    return None

def add(args):
    if not args.description.strip():
        raise ValueError("Description cannot be empty.")
    expenses = load_expenses()
    expense = {
        "id": next_id(expenses),
        "date": date.today().isoformat(),
        "description": args.description.strip(),
        "amount": parse_amount(args.amount),
    }
    expenses.append(expense)
    save_expenses(expenses)
    print(f"Expense added successfully (ID: {expense['id']})")

def update(args):
    expenses = load_expenses()
    expense = find_expense(expenses, args.id)
    if not expense:
        raise ValueError(f"Expense with ID {args.id} does not exist.")
    if args.description is None and args.amount is None:
        raise ValueError("Provide --description and/or --amount.")
    if args.description is not None:
        if not args.description.strip():
            raise ValueError("Description cannot be empty.")
        expense["description"] = args.description.strip()
    if args.amount is not None:
        expense["amount"] = parse_amount(args.amount)
    save_expenses(expenses)
    print(f"Expense updated successfully (ID: {args.id})")

def delete(args):
    expenses = load_expenses()
    expense = find_expense(expenses, args.id)
    if not expense:
        raise ValueError(f"Expense with ID {args.id} does not exist.")
    expenses.remove(expense)
    save_expenses(expenses)
    print("Expense deleted successfully")

def list_expenses(args):
    expenses = load_expenses()
    if not expenses:
        print("No expenses found.")
        return
    print(f"{'ID':<5}{'Date':<12}{'Description':<25}{'Amount':>12}")
    for e in sorted(expenses, key=lambda x: (x["date"], int(x["id"]))):
        print(f"{e['id']:<5}{e['date']:<12}{e['description'][:24]:<25}${e['amount']:>11.2f}")

def summary(args):
    expenses = load_expenses()
    if args.month is not None:
        if not 1 <= args.month <= 12:
            raise ValueError("Month must be between 1 and 12.")
        current_year = date.today().year
        matching = [
            e for e in expenses
            if datetime.strptime(e["date"], "%Y-%m-%d").year == current_year
            and datetime.strptime(e["date"], "%Y-%m-%d").month == args.month
        ]
        total = sum(Decimal(str(e["amount"])) for e in matching)
        month_name = date(current_year, args.month, 1).strftime("%B")
        print(f"Total expenses for {month_name}: ${total:.2f}")
    else:
        total = sum(Decimal(str(e["amount"])) for e in expenses)
        print(f"Total expenses: ${total:.2f}")

def build_parser():
    parser = argparse.ArgumentParser(prog="expense-tracker", description="Simple command-line expense tracker")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add", help="Add an expense")
    p.add_argument("--description", required=True)
    p.add_argument("--amount", required=True)
    p.set_defaults(func=add)

    p = sub.add_parser("update", help="Update an expense")
    p.add_argument("--id", required=True, type=int)
    p.add_argument("--description")
    p.add_argument("--amount")
    p.set_defaults(func=update)

    p = sub.add_parser("delete", help="Delete an expense")
    p.add_argument("--id", required=True, type=int)
    p.set_defaults(func=delete)

    p = sub.add_parser("list", help="List all expenses")
    p.set_defaults(func=list_expenses)

    p = sub.add_parser("summary", help="Show expense summary")
    p.add_argument("--month", type=int, help="Month number (1-12) for the current year")
    p.set_defaults(func=summary)

    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
