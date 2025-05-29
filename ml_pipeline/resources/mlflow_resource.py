import dagster as dg
import mlflow
from dagster import ConfigurableResource, InitResourceContext
from typing import Optional, Dict, Any

class MLflowResource(ConfigurableResource):
    experiment_name: str
    tracking_uri: Optional[str] = None
    run_name: Optional[str] = None
    tags: Optional[Dict[str, str]] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.run = None

    # def setup_for_execution(self, context: InitResourceContext) -> 'MLFlowResource':
    def setup_for_execution(self, context) -> 'MLflowResource':
        """Initialize MLflow run when the resource is first used"""
        if self.tracking_uri:
            mlflow.set_tracking_uri(self.tracking_uri)

        # set or create experiment
        mlflow.set_experiment(self.experiment_name)

        # start a new run if one isn't already active
        if not mlflow.active_run():
            self._run = mlflow.start_run(
                run_name=self.run_name or f'dagster_run_{context.run_id}',
                tags=self.tags or {}
            )
        return self

    def log_params(self, key: str, value: Any):
        """Log a parameter to MLflow"""
        mlflow.log_param(key, value)

    def autolog(self):
        """Enable automatic logging of metrics and parameters"""
        mlflow.autolog()

    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None):
        """Log a local file or directory as an artifact"""
        mlflow.log_artifact(local_path, artifact_path)

    def log_model(self, model, artifact_path: str, **kwargs):
        """Log a model to MLflow"""
        mlflow.sklearn.log_model(model, artifact_path, **kwargs)

    def get_run_id(self) -> Optional[str]:
        """Get the ID of the active MLflow run"""
        return mlflow.active_run().info.run_id if mlflow.active_run() else None

    def end_run(self):
        """End the active MLflow run"""
        if mlflow.active_run():
            mlflow.end_run()