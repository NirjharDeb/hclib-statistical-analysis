# hclib-statistical-analysis
Repository of scripts that can be used to conduct statistical analysis on performance of different benchmark algorithms in HClib, a C/C++ programming system for distributed systems.

## statistical_tests
This folder contains a script to run a suite of 2-sample t-tests to assess if the difference between the average performance of the different variants of an algorithm is statistically significant. It generates a PDF file with a table indicating the results of the two-sample t-tests along with a graph comparing the laptimes of the algorithms across different node configurations.

## toposort_mailbox_spring_2024
This folder contains the laptimes for the original and the modified (two-mailbox) variants of the HClib topological sorting algorithm. 

In conclusion, even though the performance improvement is positive on average, and it is statistically significant (alpha = 0.05) for all but 1 node/PE combination. The samples were gathered using the following node/PE configurations, recommended by my mentor Dr. Akihiro Hayashi (with an matrix input size of 100,000 rows and 100,000 columns): 

- 1 node, 24 PEs --> statistically insignificant
- 2 nodes, 48 PEs --> statistically significant
- 4 nodes, 96 PEs --> statistically significant
- 8 nodes, 192 PEs --> statistically significant
- 16 nodes, 384 PEs --> statistically significant