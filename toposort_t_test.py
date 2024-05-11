from scipy import stats

print("Starting t-test...\n")

# Set sample names
sample_a_name = "Sample A"
sample_b_name = "Sample B"

# set alpha value
alpha = 0.05

# set null hypothesis
null_hypothesis = "There is no significant difference between " + sample_a_name + " and " + sample_b_name + "."

# set samples
sample_a = [1,2,3,4,5]
sample_b = [6,6,6,6,6]

t_stat, p_value = stats.ttest_ind(sample_a, sample_b)

# print out results of t-test
print("t-statistic: " + str(t_stat))
print("p-value: " + str(p_value))

if p_value >= alpha:
    print("Fail to reject null hypothesis: " + null_hypothesis)
else:
    print("Reject null hypothesis: " + null_hypothesis)