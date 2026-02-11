import pandas as pd

def compute_poisson_lambda(path):
    df = pd.read_csv(path)

    # number of years
    n_years = df.shape[0]

    # total storms
    total_storms = df["storm_count"].sum()

    return total_storms / n_years

if __name__ == "__main__":
    path = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\processed\ibtracs_frequency.csv"
    lam = compute_poisson_lambda(path)
    print("λ =", lam)
