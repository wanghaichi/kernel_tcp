Code for research paper: An Empirical Study of Test Case Prioritization on the Linux Kernel

Main scripts for studied TCP approaches are as follows:

- IR-based : ir_main.py

- similarity-based : similarity_main.py

- coverage-based : coverage_main.py

- ML-based : ml_main.py


## Dataset

All collected dataset are stored in a sql file. We use mysql as the SQL backend. 
The structure of dataset can be found at database_structure.sql.
The full dataset can be downloaded at [dataset.sql](https://www.alipan.com/s/FFxRPVDgSkw)

We provide a script to access the dataset. See liebes/CiObjects.py for more details. 
The usage of the script can be found at every beginning of the main script.

The dataset is managed as a tree-like structure:

Checkout: (each commit for kernel)
 - Builds

Build: (different compilations for commits)
 - testruns

TestRun: (A group of test cases)
 - tests

Test: (Detail test case execution result)