import pandas as pd

def remove_identifiers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove or anonymize direct identifiers from the dataset.
    This ensures privacy before synthetic generation.
    """

    df = df.copy()

    # Common identifier columns to drop if present
    identifier_columns = [
        "name",
        "full_name",
        "email",
        "phone",
        "phone_number",
        "address",
        "id",
        "patient_id",
        "user_id"
    ]

    existing_cols = [col for col in identifier_columns if col in df.columns]
    df = df.drop(columns=existing_cols, errors="ignore")

    return df
