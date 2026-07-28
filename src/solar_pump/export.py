import os

# Exports csv and excel files to the outputs folder. This is temporary.
def export_csv(df):
    os.makedirs("outputs", exist_ok=True)

    filename = input("File name: ").strip()

    if not filename:
        filename = "results"

    filepath = os.path.join("outputs", f"{filename}.csv")

    df.to_csv(filepath, index=False)

    print(f"\nCSV exported successfully to:\n{filepath}")

def export_excel(df):

    os.makedirs("outputs", exist_ok=True)

    filename = input("File name: ").strip()

    if not filename:
        filename = "results"

    filepath = os.path.join("outputs", f"{filename}.xlsx")

    df.to_excel(filepath, index=False)

    print(f"\nExcel exported successfully to:\n{filepath}")