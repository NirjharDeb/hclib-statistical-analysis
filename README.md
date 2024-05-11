# hclib-statistical-analysis
Repository of scripts that can be used to conduct statistical analysis on performance of different benchmark algorithms in HClib, a C/C++ programming system for distributed systems.

## toposort_stats_analysis
This contains a suite of 2-sample t-tests that are run to assess if the difference between the average performance of the original and modified (i.e., two-mailbox) toposort algorithms have a significant difference. In conclusion, even though the performance improvement is positive on average, it is not statistically significant in any of the following cases: 

- 1 node, 24 PEs
- 2 nodes, 48 PEs
- 4 nodes, 96 PEs
- 8 nodes, 192 PEs
- 16 nodes, 384 PEs