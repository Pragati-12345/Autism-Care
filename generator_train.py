import pandas as pd
from sdv.single_table import CTGANSynthesizer
from sdv.metadata import SingleTableMetadata

def train_generator(df: pd.DataFrame):
    """
    Train a CTGAN synthesizer using inferred metadata.
    """

    # 1. Infer metadata from dataframe
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(data=df)

    # 2. Initialize CTGAN with metadata
    synthesizer = CTGANSynthesizer(
        metadata=metadata,
        epochs=300,
        verbose=True
    )

    # 3. Train model
    synthesizer.fit(df)

    return synthesizer
