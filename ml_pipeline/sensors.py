import dagster as dg
from ml_pipeline.assets import constants
from ml_pipeline.jobs import individual_job, combined_job, full_ml_pipeline_job
from ml_pipeline.fileConfig import FileConfig
import os


@dg.sensor(
    job=individual_job,
    minimum_interval_seconds=30
    # default_status=dg.DefaultSensorStatus.RUNNING
)
def updated_file_sensor(context):
    """Sensor that monitors file changes and triggers processing"""
    last_mtime = float(context.cursor) if context.cursor else 0
    max_mtime = last_mtime

    for filename in os.listdir(constants.MY_DIRECTORY):
        filepath = os.path.join(constants.MY_DIRECTORY, filename)
        if os.path.isfile(filepath) and filename.endswith('.csv'):
            fstats = os.stat(filepath)
            file_mtime = fstats.st_mtime

            if file_mtime <= last_mtime:
                continue

            run_key = f"{filename}:{file_mtime}"
            run_config = dg.RunConfig(
                ops={
                    "individual_csv_data": FileConfig(filename=filename)
                }
            )
            yield dg.RunRequest(run_key=run_key, run_config=run_config)
            max_mtime = max(max_mtime, file_mtime)

    context.update_cursor(str(max_mtime))

# Asset sensor to trigger combined job when individual files are processed
@dg.asset_sensor(
    asset_key=dg.AssetKey("individual_csv_data"),
    job=combined_job,
    minimum_interval_seconds=30
)
def combine_files_sensor(context: dg.SensorEvaluationContext, asset_event: dg.EventLogEntry):
    """Trigger combined data job when individual CSV is processed"""
    yield dg.RunRequest(run_key=context.cursor)

@dg.asset_sensor(
    asset_key=dg.AssetKey("combined_csv_data"),
    job=full_ml_pipeline_job,
    minimum_interval_seconds=30
)
def full_ml_pipeline_sensor(context: dg.SensorEvaluationContext, asset_event: dg.EventLogEntry):
    """Trigger entire ML pipeline when combined CSV is processed"""
    yield dg.RunRequest(run_key=context.cursor)