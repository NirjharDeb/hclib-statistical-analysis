from scipy import stats
import pandas as pd
import matplotlib.pyplot as plt

# Initialize lists to store data for plotting
nodes_list = []
og_means = []
mod_means = []
performance_improvements = []

def tTest(nodes):
    # Set number of cores
    cores = nodes * 24
    
    # Set alpha value
    alpha = 0.05
    
    # Set null hypothesis
    null_hypothesis = "There is no significant difference between original toposort and modified toposort for " + str(nodes) + " nodes and " + str(cores) + " PEs"

    # Read csv files of outputs to series (not dataframes)
    original_toposort_filepath = "toposort_stats_analysis/performance_data/original_toposort/og_" + str(nodes) + ".txt"
    modified_toposort_filepath = "toposort_stats_analysis/performance_data/modified_toposort/mod_" + str(nodes) + ".txt"

    original_toposort_sample = pd.read_csv(original_toposort_filepath).squeeze()
    modified_toposort_sample = pd.read_csv(modified_toposort_filepath).squeeze()

    # Run the t-test
    t_stat, p_value = stats.ttest_ind(original_toposort_sample, modified_toposort_sample)

    # Print out results of t-test
    print("t-statistic: " + str(t_stat))
    print("p-value: " + str(p_value))

    # Print out means
    og_mean = original_toposort_sample.mean()
    mod_mean = modified_toposort_sample.mean()

    print("Original mean laptime: " + str(og_mean))
    print("Modified mean laptime: " + str(mod_mean))

    # Print out performance improvement in percentage
    performance_improvement = (mod_mean - og_mean) / (og_mean) * 100
    print("Performance improvement: " + str(round(performance_improvement, 2)) + "%")

    # Print out conclusion of t-test
    if p_value >= alpha:
        print("FAIL to reject the following null hypothesis: " + null_hypothesis)
    else:
        print("REJECT the following null hypothesis: " + null_hypothesis)
    
    print()

    # Append data to lists for plotting
    nodes_list.append(nodes)
    og_means.append(og_mean)
    mod_means.append(mod_mean)
    performance_improvements.append(performance_improvement)
    
##################################################
# Run t-tests with the following number of nodes
tTest(1)
tTest(2)
tTest(4)
tTest(8)
tTest(16)

# Plot the results
plt.figure(figsize=(10, 5))

# Plot mean laptimes
plt.subplot(1, 2, 1)
plt.plot(nodes_list, og_means, label="Modified Toposort", marker='o')
plt.plot(nodes_list, mod_means, label="Original Toposort", marker='o')
plt.xlabel("Number of Nodes")
plt.ylabel("Mean Laptime")
plt.title("Mean Laptimes for Original vs Modified Toposort")
plt.legend()

# Plot performance improvements
plt.subplot(1, 2, 2)
plt.plot(nodes_list, performance_improvements, label="Performance Improvement", marker='o', color='green')
plt.xlabel("Number of Nodes")
plt.ylabel("Performance Improvement (%)")
plt.title("Performance Improvement Percentage")
plt.legend()

plt.tight_layout()
plt.show()
