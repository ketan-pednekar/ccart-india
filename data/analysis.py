import pandas as pd

df = pd.read_csv("district_relationships_master_v1_2.csv")

# event-level aggregation
event = df.groupby(['sid', 'cyclone_name', 'year']).agg(
    model_loss_hwe = ('loss_usd_hwe', 'sum'),
    dlna = ('dlna_total', 'first')
).reset_index()

# calibration factor
event['alpha'] = event['dlna'] / event['model_loss_hwe']

event
