import pandas as pd

def load_alpha_relationship(csv_path):
    """
    Load historical DLNA-to-model-loss ratios from v1.2 master file.
    Returns mean alpha for HWE and raw losses.
    """
    df = pd.read_csv(csv_path)

    event = df.groupby(['sid', 'cyclone_name', 'year']).agg(
        model_loss_hwe=('loss_usd_hwe', 'sum'),
        dlna=('dlna_total', 'first')
    ).reset_index()

    event['alpha'] = event['dlna'] / event['model_loss_hwe']

    event_raw = df.groupby(['sid', 'cyclone_name', 'year']).agg(
        raw_loss=('loss_usd_raw', 'sum'),
        dlna=('dlna_total', 'first')
    ).reset_index()

    event_raw['alpha_raw'] = event_raw['dlna'] / event_raw['raw_loss']

    return event['alpha'].mean(), event_raw['alpha_raw'].mean()


def estimate_dlna_from_model_loss(model_loss, alpha_mean):
    """
    Estimate DLNA for synthetic cyclone using historical alpha.
    """
    return model_loss * alpha_mean
