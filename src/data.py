"""
Module for loading and processing combined data from a parquet file.
"""
import os
from pathlib import Path
from functools import cache

import polars as pl


DEFAULT_LOCAL_PATH = Path().resolve() / 'data'
DATA_DIR = os.getenv('DATA_DIR', DEFAULT_LOCAL_PATH)
DATA_PATH = DATA_DIR / 'combined_data.parquet'


def get_df() -> pl.DataFrame:
    """Loads the combined data from the parquet file."""
    df = pl.read_parquet(DATA_PATH)
    return df


@cache
def get_categories_table() -> pl.DataFrame:
    """Get the initial categories table with group codes and names."""
    df = get_df()

    # Get unique group codes and names, filtering and sorting them appropriately
    df_categories = (
        df
        .select(['Group Code', 'Group Name'])
        .unique()
        .filter(pl.col('Group Code').str.contains(r'^\d+(\.\d+)*\.?$'))  # Remove group codes that don't look like x.y.z
        .with_columns(  # Sort lexicographically by group code
            pl.col("Group Code")
            .str.strip_chars(".")
            .str.split(".")
            .list.eval(pl.element().cast(pl.Int64))
            .alias("_sort_key")
        )
        .sort("_sort_key")
        .drop("_sort_key")
    )

    # Add initial values for the input table
    df_init = df_categories.with_columns([
        pl.lit(None, dtype=pl.Float32).alias('Use level (mg/kg)'),
        pl.lit(False, dtype=pl.Boolean).alias('Consumers of')
    ])

    return df_init
