import dagster as dg

individual = dg.AssetSelection.assets(['individual_csv_data'])

combined = dg.AssetSelection.assets(['combined_csv_data'])

individual_job = dg.define_asset_job(
    name= 'individual_job',
    selection= individual
)

combined_job = dg.define_asset_job(
    name ='combined_job',
    selection= combined
)

full_ml_pipeline_job = dg.define_asset_job(
    name='full_ml_pipeline_job',
    selection= dg.AssetSelection.all() - individual - combined
)