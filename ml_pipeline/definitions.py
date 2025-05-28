import dagster as dg
from ml_pipeline.assets import rentals, processing, model
from ml_pipeline.jobs import individual_job, combined_job, full_ml_pipeline_job
from ml_pipeline.sensors import updated_file_sensor, combine_files_sensor, full_ml_pipeline_sensor

rental_assets = dg.load_assets_from_modules([rentals])
processing_assets = dg.load_assets_from_modules([processing])
model_assets = dg.load_assets_from_modules([model])

all_jobs = [individual_job, combined_job, full_ml_pipeline_job]
all_sensors = [updated_file_sensor, combine_files_sensor, full_ml_pipeline_sensor]

defs = dg.Definitions(
    assets=[*rental_assets, *processing_assets, *model_assets],
    jobs=all_jobs,
    sensors=all_sensors
)
