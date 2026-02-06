import pandas as pd

def validate_distribution(real_df: pd.DataFrame, synthetic_df: pd.DataFrame):
    """
    Simple statistical validation comparing real and synthetic data.
    Prints mean differences for numeric columns.
    """

    numeric_cols = real_df.select_dtypes(include="number").columns

    print("\nValidation: Mean comparison (Real vs Synthetic)\n")

    for col in numeric_cols:
        real_mean = real_df[col].mean()
        synth_mean = synthetic_df[col].mean()
        diff = abs(real_mean - synth_mean)

        print(f"{col}: Real={real_mean:.4f}, Synthetic={synth_mean:.4f}, Diff={diff:.4f}")
