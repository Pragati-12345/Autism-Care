from synthetic_pipeline.dataset_loader import load_csv_dataset
from synthetic_pipeline.preprocessing import clean_dataset
from synthetic_pipeline.privacy_filter import remove_identifiers
from synthetic_pipeline.generator_train import train_generator
from synthetic_pipeline.generator_sample import generate_samples
from synthetic_pipeline.validation import validate_distribution
from synthetic_pipeline.registry import register_synthetic_dataset


def run_pipeline(dataset_file):
    print("Loading dataset...")
    df = load_csv_dataset(dataset_file)

    print("Cleaning dataset...")
    df = clean_dataset(df)

    print("Removing identifiers...")
    df = remove_identifiers(df)

    print("Training generator...")
    generator = train_generator(df)   # ← MUST EXIST

    print("Generating synthetic samples...")
    synthetic = generate_samples(generator, 500)  # ← USES generator

    print("Validating synthetic data...")
    validate_distribution(df, synthetic)

    register_synthetic_dataset(synthetic)


if __name__ == "__main__":
    run_pipeline("autism_screening.csv")
