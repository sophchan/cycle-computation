import os
import sys
import pandas as pd

from time_series_utils import N_common_duration, N_ranked_cycles

def construct_summary_stats(dir_path, metrics):
    """
    Construct data frame summarizing sig_value column for all csv files in provided file path.
    
    O(sum_i n_i log n_i) where n_i is the # of sig_values for car i
    
    Variables:
    - dir_path [string]: User-provided input file path to folder with desired csv files
    - metrics [list]: List of metrics to calculate per series. Must be one of pre-determined metrics
    """

    stats_by_car = []
    for file in os.listdir(dir_path):
        if file.endswith(".csv"):
            df = pd.read_csv(f"{dir_path}/{file}", index_col=0)
            sig_series = df.sig_value
            
            # similar to .describe method but with more specific metrics
            summary_dict = {}
            if "mean" in metrics: 
                summary_dict["mean"] = sig_series.mean()
            if "std" in metrics: 
                summary_dict["std"] = sig_series.std()
            if "skew" in metrics: 
                summary_dict["skew"] = sig_series.skew()
            if "most common occurrence" in metrics: 
                summary_dict["most common occurrence"] = sig_series.mode()[0]
            if "most common duration" in metrics: 
                summary_dict["most common duration"] = N_common_duration(df, 1)[0]
            if "largest amplitude" in metrics: 
                summary_dict["largest amplitude"] = N_ranked_cycles(df, 1).iloc[0]["amplitude"]
            
            stats_by_car.append(pd.Series(summary_dict, name=file[:-4]))
    
    return pd.concat(stats_by_car, axis=1)


def identify_outliers(dir_path, metrics):
    """
    Identify outliers using logic that data points outside of the 
    [25th %ile - 1.5 x IQR, 7th %ile + 1.5 x IQR] range are outliers
    
    O(sum_i n_i log n_i) where n_i is the # of sig_values for car i
    
    Variables:
    - dir_path [string]: User-provided input to folder with desired csv
    - metrics [list]: List of metrics to test for outliers
    """
    
    summary_stats = construct_summary_stats(dir_path, metrics)
    
    combined_outliers = set([])
    
    print(f"Outliers where metric is not within [25th %ile - 1.5 x IQR, 7th %ile + 1.5 x IQR] range: \n")
    
    for metric in metrics:
        metric_samples = summary_stats.loc[metric, :]

        samples_75_pctl = metric_samples.quantile(0.75)
        samples_25_pctl = metric_samples.quantile(0.25)
        samples_iqr = samples_75_pctl - samples_25_pctl

        outlier_lb = samples_25_pctl - 1.5 * samples_iqr
        outlier_ub = samples_75_pctl + 1.5 * samples_iqr

        outliers = metric_samples.loc[(metric_samples < outlier_lb) | (metric_samples > outlier_ub)].index
        combined_outliers.update(list(outliers))
    
        print(f"{metric}: {list(outliers)}")
    
    print(f"\n Of total {len(summary_stats.columns)} samples, have identified {len(combined_outliers)} outliers: {list(combined_outliers)}")
    
    return combined_outliers
    
    
if __name__ ==  "__main__":
    dir_path = sys.argv[1]
    
    default_metrics = ["mean", "std", "skew", "most common occurrence", \
                        "most common duration", "largest amplitude"]
    metrics = default_metrics if len(sys.argv)==2 else sys.argv[2:]
    
    identify_outliers(dir_path, metrics)
    
    