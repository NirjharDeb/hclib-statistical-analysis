# hclib-statistical-analysis
Repository of scripts that can be used to conduct statistical analysis on performance of different benchmark algorithms in HClib, a C/C++ programming system for distributed systems.

## toposort_stats_analysis
This folder contains a suite of 2-sample t-tests that are run to assess if the difference between the average performance of the original and modified (i.e., two-mailbox) toposort algorithms is statistically significant. In conclusion, even though the performance improvement is positive on average, and it is statistically significant (alpha = 0.05) for all but 1 node/PE combination. The samples were gathered using the following node/PE configurations, recommended by my mentor Dr. Akihiro Hayashi (with an matrix input size of 100,000 rows and 100,000 columns): 

- 1 node, 24 PEs --> statistically insignificant
- 2 nodes, 48 PEs --> statistically significant
- 4 nodes, 96 PEs --> statistically significant
- 8 nodes, 192 PEs --> statistically significant
- 16 nodes, 384 PEs --> statistically significant

### performance_data file structure
This data folder is made up of two smaller sub-folders, **modified_toposort** and **original_toposort**. Both folders contain the laptimes for different runs. For example, in **modified_toposort**, the file *mod_1.txt* contains all the laptimes for each time the modified toposort algorithm was run on 1 node. The data in these files originated from running toposort on Georgia Tech's PACE supercomputer.