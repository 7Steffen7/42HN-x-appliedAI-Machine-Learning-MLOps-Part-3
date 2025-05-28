import numpy as np
import pandas as pd

def split_csv_into_parts(df: pd.DataFrame, n_parts):
    chunks = np.array_split(df, n_parts)
    for i, chunk in enumerate(chunks, 1):
        chunk.to_csv(f'raw_data_{i}.csv', index=False)


def main():
    df = pd.read_csv('hour.csv')
    split_csv_into_parts(df, 5)
    # df.to_csv('raw_data.csv', index=False)

if __name__ == "__main__":
    main()