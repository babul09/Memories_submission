from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# Text normalization
# ---------------------------------------------------------------------------

def normalize_text(value: object) -> str:
    """
    Conservative text normalization.

    Keeps the underlying meaning intact:
    - Unicode normalization
    - case folding
    - whitespace normalization
    - basic punctuation normalization

    Does NOT:
    - correct spelling
    - remove legal suffixes
    - transliterate
    - use external data
    """
    if pd.isna(value):
        return ""

    text = str(value)

    # Normalize Unicode representations.
    text = unicodedata.normalize("NFKC", text)

    # Case-insensitive comparison.
    text = text.casefold()

    # Normalize common whitespace characters.
    text = re.sub(r"\s+", " ", text)

    # Normalize whitespace around punctuation while keeping
    # the punctuation readable in the primary representation.
    text = re.sub(r"\s+([,.;:/#&()\-])", r"\1", text)
    text = re.sub(r"([,.;:/#&()\-])(?=\S)", r"\1 ", text)

    # Clean up any whitespace introduced above.
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def compact_text(value: object) -> str:
    """
    Remove non-alphanumeric characters from normalized text.

    Example:
        "ABC Corp." -> "abccorp"
    """
    text = normalize_text(value)
    return re.sub(r"[^\w]+", "", text, flags=re.UNICODE)


def tokenize(value: object) -> list[str]:
    """
    Convert normalized text into whitespace-separated tokens.
    """
    text = normalize_text(value)

    if not text:
        return []

    return text.split()


def extract_numbers(value: object) -> list[str]:
    """
    Extract numeric components from a field.

    Example:
        "123 Main St, Apt 45" -> ["123", "45"]
    """
    text = normalize_text(value)

    if not text:
        return []

    return re.findall(r"\d+", text)


# ---------------------------------------------------------------------------
# Source preprocessing
# ---------------------------------------------------------------------------

def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add normalized representations while preserving all original columns.
    """

    required_columns = {
        "entity_id",
        "business_name",
        "business_address",
        "country",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    result = df.copy()

    # -----------------------------------------------------------------------
    # Business name
    # -----------------------------------------------------------------------

    result.loc[:, "name_norm"] = result["business_name"].map(normalize_text)
    result.loc[:, "name_compact"] = result["business_name"].map(compact_text)
    result.loc[:, "name_tokens"] = result["business_name"].map(tokenize)

    # -----------------------------------------------------------------------
    # Business address
    # -----------------------------------------------------------------------

    result.loc[:, "address_missing"] = result["business_address"].isna()
    result.loc[:, "address_norm"] = result["business_address"].map(normalize_text)
    result.loc[:, "address_compact"] = result["business_address"].map(compact_text)
    result.loc[:, "address_tokens"] = result["business_address"].map(tokenize)
    result.loc[:, "address_numbers"] = result["business_address"].map(
        extract_numbers
    )

    # -----------------------------------------------------------------------
    # Country
    # -----------------------------------------------------------------------

    result.loc[:, "country_norm"] = result["country"].map(normalize_text)

    return result


# ---------------------------------------------------------------------------
# File processing
# ---------------------------------------------------------------------------

def preprocess_file(
    input_path: str | Path,
    output_path: str | Path,
) -> None:
    """
    Read a TSV file, preprocess it, and save the result as Parquet.
    """

    input_path = Path(input_path)
    output_path = Path(output_path)

    print(f"Reading: {input_path}")

    df = pd.read_csv(
        input_path,
        sep="\t",
        dtype=str,
        keep_default_na=False,
    )

    # Convert empty strings in address to missing values.
    if "business_address" in df.columns:
        df.loc[df["business_address"].eq(""), "business_address"] = pd.NA

    processed = preprocess_dataframe(df)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if output_path.exists():
        print(f"Overwriting existing file: {output_path}")

    processed.to_parquet(
        output_path,
        index=False,
    )

    print(f"Saved: {output_path}")
    print(f"Rows: {len(processed):,}")
    print(f"Columns: {len(processed.columns)}")


# ---------------------------------------------------------------------------
# Dataset paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATASET_ROOT = PROJECT_ROOT / "dataset_nd_resources" / "dataset"

OUTPUT_ROOT = PROJECT_ROOT / "output" / "processed"


FILES = {
    "train_source1": (
        DATASET_ROOT / "train" / "train_source1.tsv",
        OUTPUT_ROOT / "train_source1.parquet",
    ),
    "train_source2": (
        DATASET_ROOT / "train" / "train_source2.tsv",
        OUTPUT_ROOT / "train_source2.parquet",
    ),
    "train_source3": (
        DATASET_ROOT / "train" / "train_source3.tsv",
        OUTPUT_ROOT / "train_source3.parquet",
    ),
    "test_source1": (
        DATASET_ROOT / "test" / "test_source1.tsv",
        OUTPUT_ROOT / "test_source1.parquet",
    ),
    "test_source2": (
        DATASET_ROOT / "test" / "test_source2.tsv",
        OUTPUT_ROOT / "test_source2.parquet",
    ),
    "test_source3": (
        DATASET_ROOT / "test" / "test_source3.tsv",
        OUTPUT_ROOT / "test_source3.parquet",
    ),
}


def main() -> None:
    for name, (input_path, output_path) in FILES.items():
        print(f"\n{'=' * 70}")
        print(f"Processing {name}")
        print(f"{'=' * 70}")

        preprocess_file(
            input_path=input_path,
            output_path=output_path,
        )


if __name__ == "__main__":
    input_path = DATASET_ROOT / "train" / "train_source1.tsv"
    output_path = OUTPUT_ROOT / "train_source1_test.parquet"

    preprocess_file(
        input_path=input_path,
        output_path=output_path,
    )