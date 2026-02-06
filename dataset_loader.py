import os
import pandas as pd

def load_csv_dataset(filename: str) -> pd.DataFrame:
    """
    Load CSV dataset from project root directory.
    """

    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )

    dataset_path = os.path.join(project_root, filename)

    print(f"Looking for dataset at: {dataset_path}")

    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"{dataset_path} not found")

    return pd.read_csv(dataset_path)
