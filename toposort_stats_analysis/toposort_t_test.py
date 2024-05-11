from scipy import stats
import pandas as pd

print("Starting t-test for toposort benchmark algorithm...\n")

# set alpha value
alpha = 0.05

# set null hypothesis
null_hypothesis = "There is no significant difference between original toposort and modified toposort."

# read csv files of outputs
original_toposort_sample = pd.read_csv('toposort_stats_analysis\performance_data\original_toposort_data.txt')
modified_toposort_sample = pd.read_csv('toposort_stats_analysis\performance_data\modified_toposort_data.txt')

# run the t-test
t_stat, p_value = stats.ttest_ind(original_toposort_sample, modified_toposort_sample)

# print out results of t-test
print("t-statistic: " + str(t_stat))
print("p-value: " + str(p_value))

if p_value >= alpha:
    print("Fail to reject null hypothesis: " + null_hypothesis)
else:
    print("Reject null hypothesis: " + null_hypothesis)