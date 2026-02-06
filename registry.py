import os
import pandas as pd
from datetime import datetime

def register_synthetic_dataset(df: pd.DataFrame, output_dir="synthetic_output"):
    """
    Save synthetic dataset with timestamp for traceability.
    """

    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"synthetic_dataset_{timestamp}.csv"
    output_path = os.path.join(output_dir, filename)

    df.to_csv(output_path, index=False)

    print(f"\nSynthetic dataset registered at:\n{output_path}\n")

    return output_path
