from scipy import stats
import pandas as pd

def tTest(nodes):
    # Set number of cores
    cores = nodes * 24
    
    # Set alpha value
    alpha = 0.05
    
    # set null hypothesis
    null_hypothesis = "There is no significant difference between original toposort and modified toposort for " + str(nodes) + " nodes and " + str(cores) + " PEs"

    # read csv files of outputs to series (not dataframes)
    original_toposort_filepath = "toposort_stats_analysis\performance_data\original_toposort\og_" + str(nodes) + ".txt"
    modified_toposort_filepath = "toposort_stats_analysis\performance_data\modified_toposort\mod_" + str(nodes) +".txt"

    original_toposort_sample = pd.read_csv(original_toposort_filepath).squeeze()
    modified_toposort_sample = pd.read_csv(modified_toposort_filepath).squeeze()

    # run the t-test
    t_stat, p_value = stats.ttest_ind(original_toposort_sample, modified_toposort_sample)

    # print out results of t-test
    print("t-statistic: " + str(t_stat))
    print("p-value: " + str(p_value))

    # print out means
    og_mean = original_toposort_sample.mean()
    mod_mean = modified_toposort_sample.mean()

    print("Original mean laptime: " + str(og_mean))
    print("Modified mean laptime: " + str(mod_mean))

    # print out performance improvement in percentage
    performance_improvement = (mod_mean - og_mean) / (og_mean) * 100
    print("Performance improvement: " + str(round(performance_improvement, 2)) + "%")

    if p_value >= alpha:
        print("FAIL to reject the following null hypothesis: " + null_hypothesis)
    else:
        print("REJECT the following null hypothesis: " + null_hypothesis)
        
    print()
##################################################
# Run t-tests with the following options

# Choose which node and PE/core combination to compare (for example, node N = 1 and pe n = 24)
# In HClib, PE = number of nodes * 24

tTest(1)
tTest(2)
tTest(4)
tTest(8)
tTest(16)



