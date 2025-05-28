import dagster as dg
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_squared_error, r2_score, root_mean_squared_log_error
import xgboost as xgb
import os
import pickle

@dg.asset
def xgboost_model(training_data, X_train_processed) -> xgb.XGBRegressor:
    """Train XGBoost model."""
    X_train, y_train = training_data

    model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42
    )
    model.fit(X_train_processed, y_train)
    return model

@dg.asset
def model_evaluation(test_data, X_test_processed, xgboost_model: xgb.XGBRegressor) -> dict:
    """Evaluate model performance."""
    X_test, y_test = test_data

    y_pred = xgboost_model.predict(X_test_processed)

    y_pred_clipped = np.maximum(0, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    rmsle = root_mean_squared_log_error(y_test, y_pred_clipped)

    metrics = {'mse': mse,
               'r2': r2,
               'rmsle': rmsle,
               'rmse': np.sqrt(mse)
    }
    return metrics

@dg.asset
def model_artifacts(xgboost_model: xgb.XGBRegressor, preprocessor: ColumnTransformer) -> str:
    """Save trained model and preprocessor"""

    os.makedirs('models', exist_ok=True)

    model_path = 'models/xgboost_model.pkl'
    with open(model_path, 'wb') as f:
        pickle.dump(xgboost_model, f)

    preprocesor_path = 'models/preprocessor.pkl'
    with open(preprocesor_path, 'wb') as f:
        pickle.dump(preprocessor, f)

    return f"Models saved to {model_path}, Preprocessor saved to {preprocesor_path}"