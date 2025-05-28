import dagster as dg
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from ml_pipeline.assets import constants

@dg.multi_asset(
    outs={
        'training_data': dg.AssetOut(),
        'test_data': dg.AssetOut()
    },
    deps=[dg.AssetKey("combined_csv_data")],
)
def split_data(context: dg.AssetExecutionContext ,combined_csv_data: pd.DataFrame):
    """Split data into training and test sets."""

    # X = raw_data[NUMERICAL_FEATURES + CATEGORICAL_FEATURES]
    # y = raw_data['cnt']
    X = combined_csv_data[constants.NUMERICAL_FEATURES + constants.CATEGORICAL_FEATURES]
    y = combined_csv_data['cnt']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    return (X_train, y_train), (X_test, y_test)

@dg.asset
def preprocessor(training_data) -> ColumnTransformer:
    """"Create and fit preprocessing pipeline."""

    X_train, y_train = training_data
    numerical_transformer = Pipeline([
        ('scaler', StandardScaler())
    ])
    categorical_transformer = Pipeline([
        ('encoder', OneHotEncoder(sparse_output=False, handle_unknown='ignore'))
    ])
    preprocessor = ColumnTransformer([
        ('numerical', numerical_transformer, constants.NUMERICAL_FEATURES),
        ('categorical', categorical_transformer, constants.CATEGORICAL_FEATURES)
    ])
    preprocessor.fit(X_train)
    return preprocessor

@dg.multi_asset(
    outs={
        'X_train_processed': dg.AssetOut(),
        'X_test_processed': dg.AssetOut()
        }
)
def processed_featutures(training_data, test_data, preprocessor: ColumnTransformer):
    """Apply preprocessing to training and test data."""
    X_train, y_train = training_data
    X_test, y_test = test_data

    X_train_processed = preprocessor.transform(X_train)
    X_test_processed = preprocessor.transform(X_test)

    return X_train_processed, X_test_processed