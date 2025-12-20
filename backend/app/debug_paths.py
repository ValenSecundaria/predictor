
from pathlib import Path

# Simulate main.py / deps.py logic
SCRIPT_DIR = Path(__file__).resolve().parent
DATASETS_DIR = SCRIPT_DIR / "data" / "datasets"

print(f"Script: {SCRIPT_DIR}")
print(f"Datasets: {DATASETS_DIR}")
print(f"Exists: {DATASETS_DIR.exists()}")

def get_available_years(datasets_dir: Path):
    years = []
    if datasets_dir.exists():
        for item in datasets_dir.iterdir():
            if item.is_dir() and item.name.isdigit():
                if (item / "worldcup.json").exists():
                    years.append(item.name)
    return sorted(years)

years = get_available_years(DATASETS_DIR)
print(f"Available years: {years}")
