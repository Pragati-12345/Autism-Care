import pandas as pd

def clean_dataset(df):
    """
    Clean and normalize tabular autism screening data.
    """
    df = df.copy()

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Fill numeric columns
    for col in df.select_dtypes(include=["number"]).columns:
        df[col] = df[col].fillna(df[col].median())

    # Fill categorical columns
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].fillna("Unknown")

    return df
