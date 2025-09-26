import sys
import pandas as pd


def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Normalize column names/ordering consistently
    return df


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 verify_csv.py <expected_csv> <actual_csv>")
        sys.exit(2)

    expected_path, actual_path = sys.argv[1], sys.argv[2]
    exp = load_csv(expected_path)
    act = load_csv(actual_path)

    # If the actual has Latitude/Longitude columns but expected doesn't, drop them for comparison
    for col in ["Latitude", "Longitude"]:
        if col in act.columns and col not in exp.columns:
            act = act.drop(columns=[col])

    # Align columns by name; ensure same order
    if list(exp.columns) != list(act.columns):
        print("Column mismatch:")
        print(" expected:", list(exp.columns))
        print(" actual:  ", list(act.columns))
        sys.exit(3)

    # Reset index to avoid index label mismatches
    exp = exp.reset_index(drop=True)
    act = act.reset_index(drop=True)

    # Shape check
    if exp.shape != act.shape:
        print(f"Shape mismatch: expected {exp.shape}, actual {act.shape}")
        sys.exit(4)

    # Compare dataframes exactly
    if not exp.equals(act):
        # Find and print first few diffs
        diffs = exp.ne(act)
        # Handle NaNs: treat both NaNs as equal
        diffs = diffs & ~(exp.isna() & act.isna())
        rows, cols = diffs.to_numpy().nonzero()
        print(f"Found {len(rows)} mismatched cells; showing up to 10:")
        for i in range(min(10, len(rows))):
            r, c = rows[i], cols[i]
            print(f" row {r}, col '{exp.columns[c]}': expected={exp.iloc[r, c]!r} actual={act.iloc[r, c]!r}")
        sys.exit(4)

    print("CSV verification passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()


