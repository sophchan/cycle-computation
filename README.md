# cycle-computation
Drive unit torque time series analysis

## Necessary Dependencies

To install dependencies, run `pip install -r ./requirements.txt`

* **pandas**

* **numpy**

* **collections**

* **scipy**: I used the `argrelextrema` method to calculate relative extrema for identifying cycles in question 1. The resulting list of extrema is almost equivalent to identifying minima with the condition `current <= next & current <= prev` and vice versa for maxima. However, there is additional functionality that assigns endpoints as local extrema and that filters for noise (evaluating a larger window than consecutive values). These make future adaptations easier. 

* **sys**: I used the `argv` method from sys to take in arguments from the command line for both questions. This decision was to avoid hard-coding file paths.

* **os**: I used the `listdir` and `endswith` methods from os to iterate through the files in a directory path. Similarly, this was to avoid hard-coding file names. 

## Question 1 - Time Series Utilities

### Solution

* 5 least common values by total occurrence: [428.5, -182.0, 246.75, 187.75, 222.25]

* 3 most common values by duration: [0.0, -0.25, 0.25]

* 3 cycles with the largest amplitude: 
  
  |     | Amplitude | Min     | Max    | Duration (sec) |
  | --- | --------- | ------- | ------ | -------------- |
  | 0   | 1251.00   | -1024.0 | 227.00 | 8.657          |
  | 1   | 1241.25   | -1024.0 | 218.25 | 6.048          |
  | 2   | 1226.75   | -1024.0 | 202.75 | 11.346         |

To reproduce the solutions, run `python time_series_utils.py ./Data/car_0.csv`.

The runtime was 1.3 sec on real time and 4.1 sec on user+sys time.

### Methods

<u>Most/least common by occurrence</u>: 

* Count occurrences of each value and sort (top N) frequencies.

* Output the desired number of values. (Ties by occurrences are broken randomly.)

<u>Most/least common by duration</u>: 

* Calculate duration for each value. Assumption: The recorded value is sustained until a recorded value change.

* Group by value and sum duration. Sort frequencies.

* Output the desired number of values. (Ties by duration are broken randomly.)

<u>Largest/smallest cycles by amplitude</u>: 

* Calculate duration for each value. 

* Identify local minima/maxima. Assumption: I did not consider sustained values as multiple local minima/maxima.

* Calculate duration of each cycle. Duration is calculated as time elapsed between consecutive minima (maxima) such that the cycle's start and end points are both minima (maxima).

* Calculate amplitudes from consecutive extrema and sort amplitudes.

* Output the details for the desired number of cycles. (Ties by amplitude are broken randomly.)

### Potential Improvements

For the cycle-identifying function, an improvement could be to differentiate between sustained non-zero and zero values. Since the data represents torque, a sustained zero value would indicate a resting state. Depending on the problem at hand, it might be more representative to exclude time elapsed at the resting state when looking at cycles. The option to toggle between the two options could be beneficial. 

An improvement to runtimes would be to implement a heap-like function to sort the series in a more efficient manner. Particularly for this dataset, when ranking the least common values, many values have frequencies of 1. The new function could avoid sorting the entire list of unique values if N unique values of frequency 1 have been identified before sorting the entire series. 

## Question 2 - Detect Outliers

### Solution

Car 3 and Car 7

To reproduce the solutions, run `python outlier_detection.py ./Data`.

The runtime was 3.6 sec on real time and 5.4 sec on user+sys time. 

### Methods

To determine which vehicles are behaving differently from the rest, I identified outliers from the sampled cars using different statistics on the cars' time series. 

Using IQR = 75th %ile - 25th %ile, any data point that fell outside the range of [25th %ile - 1.5 x IQR, 75th %ile + 1.5x IQR] would be deemed an outlier with respect to the specific metric. The identified outliers across the metrics are aggregated as the final answer.

I ran the test on the samples' means, standard deviations, skews, and the three functions from question 1. These metrics were intended to capture differences in trends due to higher accrued damage. 

### Potential Improvements

The runtime can be improved if the vehicle malfunctions are known and side effects are predictable.  

For example, if the damaged vehicles are expected to have larger fluctuations or must require larger torques to achieve the same results, selecting standard deviation and/or N largest amplitudes may be sufficient to detect anomalies. 

As another example, if the damaged vehicle is no longer calibrated to the resting state of 0 anymore, the mean and N common values by occurrence/duration  metrics may be sufficient to detect which car(s) may have issues. 
