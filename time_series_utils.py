import sys
import pandas as pd
import numpy as np
import collections
from scipy.signal import argrelextrema

def N_common_occurrences(df, N, ascending=False): 
    """
    Returns list of N most/least common values by total occurrence.
    
    O(n logn) where n is # of sig_values
    
    Variables:
    - df [Pandas DataFrame]
    - N [int]
    - ascending [Boolean]: 
        Setting to False (default) will return the N most common values
        Setting to True will return the N least common values
    """
    if not ascending: 
        frequencies = collections.Counter(df["sig_value"])
    
        return [val for val, _ in frequencies.most_common(N)]
    else:
        frequencies = collections.Counter(df["sig_value"])
    
        return [val for val, _ in frequencies.most_common()[-N:]]


def N_common_duration(df, N, ascending=False):
    """
    Returns list of N most/least common values by time spent. Duration is calculated as time 
    elapsed until a change in recorded value.
    
    O(n logn) where n is # of sig_values
    
    Variables:
    - df [Pandas DataFrame]: 
        - sig_value [float64]
        - timestamp_utc [datetime64]
    - N [int]
    - ascending [Boolean]
        Setting to False (default) will return the N values w/ the longest duration
        Setting to True will return the N values w/ the shortest duration
    """  
    # format timestamp
    df['timestamp_utc'] = pd.to_datetime(df['timestamp_utc'], format='%Y-%m-%d %H:%M:%S.%f')
    
    # calculate elapsed time between rows
    df["time_elapsed"] = df["timestamp_utc"].diff().shift(-1)
    
    # aggregate time by value
    total_time = df[["sig_value", "time_elapsed"]].groupby(['sig_value'], sort=False).sum() \
                    .sort_values(by="time_elapsed", ascending=False)
    
    return total_time.index[0:N] if not ascending else total_time.index[-N:]


def N_ranked_cycles(df, N, ascending=False):
    """
    Returns lists of amplitude, minima, maxima, and duration (ns) for the N largest/smallest cycles. 
    
    O(n logn) where n is # of sig_values
    
    Variables:
    - df [Pandas DataFrame]
    - N [int]
    - ascending [Boolean]: 
        Setting to False (default) will return details on the N cycles w/ largest amplitudes
        Setting to True will return details on the N cycles w/ smallest amplitudes
    """
    # format timestamp
    df['timestamp_utc'] = pd.to_datetime(df['timestamp_utc'], format='%Y-%m-%d %H:%M:%S.%f')
    
    # drop subsequent consecutive sig_values to get timestamps for value changes
    df["prev_sig_value"] = df["sig_value"].shift(1)
    df = df.loc[df.loc[:, "sig_value"] != df.loc[:, "prev_sig_value"]] \
            .drop(columns="prev_sig_value").reset_index(drop=True)

    # Find local extrema
    df['local_min'] = df.iloc[argrelextrema(df["sig_value"].values, np.less_equal)[0]]["sig_value"]
    df['local_max'] = df.iloc[argrelextrema(df["sig_value"].values, np.greater_equal)[0]]["sig_value"]
    extrema = df.loc[df["local_min"].notnull() | df["local_max"].notnull()].reset_index(drop=True)

    # calculate amplitude and duration
    extrema.loc[:, "amplitude"] = extrema.loc[:, "sig_value"].diff().abs().shift(-1)
    extrema.loc[:, "cycle_duration"] = extrema.loc[:, "timestamp_utc"].diff(periods=2).shift(-2)

    # fill in corresponding local min/max for local max/min data points
    extrema.loc[extrema["local_min"].isnull(), "local_min"] = extrema.loc[:, "sig_value"] - extrema.loc[:, "amplitude"]
    extrema.loc[extrema["local_max"].isnull(), "local_max"] = extrema.loc[:, "sig_value"] + extrema.loc[:, "amplitude"]

    # sort complete cycles
    N_extrema = extrema.dropna(subset="cycle_duration").sort_values(by="amplitude", ascending=ascending) \
                        .head(N).reset_index(drop=True)
    
    return N_extrema.loc[:, ["amplitude", "local_min", "local_max", "cycle_duration"]]


def example_N_common_occurrences(file_path, N, ascending=False):
    df = pd.read_csv(file_path, index_col=0)
    N_values = N_common_occurrences(df, N, ascending=ascending)
    
    measure = "most" if not ascending else "least"

    print(f"{N} {measure} common values by occurrences: {list(N_values)}\n")
    
    
def example_N_common_duration(file_path, N, ascending=False):
    df = pd.read_csv(file_path, index_col=0)
    N_values = N_common_duration(df, N, ascending=ascending)
    
    measure = "most" if not ascending else "least"

    print(f"{N} {measure} common values by duration: {list(N_values)}\n")
    
    
def example_N_ranked_cycles(file_path, N, ascending=False):
    df = pd.read_csv(file_path, index_col=0)
    N_cycles = N_ranked_cycles(df, N, ascending=ascending)
    
    measure = "largest" if not ascending else "smallest"
    
    print(f"{N} {measure} cycles: ")
    print(N_cycles)
    
    
if __name__ ==  "__main__":
    file_path = sys.argv[1]
    print(f"File path: {file_path}\n")
    
    example_N_common_occurrences(file_path, 5, ascending=True)
    example_N_common_duration(file_path, 3)
    example_N_ranked_cycles(file_path, 3)
    
    