# Expense Tracker

A working command-line expense tracker using Python 3 and a JSON file for persistence.

## Requirements

- Python 3.9+
- No external dependencies

## Run

```bash
./expense-tracker add --description "Lunch" --amount 20
./expense-tracker add --description "Dinner" --amount 10
./expense-tracker list
./expense-tracker summary
./expense-tracker update --id 1 --amount 25
./expense-tracker delete --id 2
./expense-tracker summary --month 9
```

On Windows, use:

```powershell
python src/expense_tracker.py add --description "Lunch" --amount 20
```

Data is stored in `data/expenses.json`.

## Validation

- Amount must be greater than zero.
- Amount supports at most two decimal places.
- Expense IDs must exist for update/delete.
- Month must be 1-12.
- Empty descriptions are rejected.
