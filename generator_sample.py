import pandas as pd

def generate_samples(generator, num_samples: int) -> pd.DataFrame:
    """
    Generate synthetic samples using a trained SDV synthesizer.
    """

    synthetic_df = generator.sample(num_samples)
    return synthetic_df
