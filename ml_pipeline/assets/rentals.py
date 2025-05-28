import dagster as dg
import pandas as pd
import os

from ml_pipeline.assets import constants
from ml_pipeline.fileConfig import FileConfig

#TODO INPUT VALIDATION

@dg.asset
def individual_csv_data(context: dg.AssetExecutionContext, config: FileConfig) -> pd.DataFrame:
    """Process individual CSV files based on sensor trigger"""
    filepath = os.path.join(constants.MY_DIRECTORY, config.filename)
    df = pd.read_csv(filepath)
    context.log.info(f"Processed file: {config.filename}")
    return df


@dg.asset(
    deps=[individual_csv_data]
)
def combined_csv_data(context: dg.AssetExecutionContext) -> pd.DataFrame:
    """Combine all CSV files from the directory into a single DataFrame"""
    combined_df = pd.DataFrame()

    # Get all CSV files in the directory
    csv_files = [f for f in os.listdir(constants.MY_DIRECTORY) if f.endswith('.csv')]

    for filename in csv_files:
        filepath = os.path.join(constants.MY_DIRECTORY, filename)
        if os.path.isfile(filepath):
            df = pd.read_csv(filepath)
            # Add source filename as a column for tracking
            df['source_file'] = filename
            combined_df = pd.concat([combined_df, df], ignore_index=True)
            context.log.info(f"Added {filename} to combined dataset")

    context.log.info(f"Combined {len(csv_files)} CSV files into DataFrame with {len(combined_df)} rows")
    return combined_df

