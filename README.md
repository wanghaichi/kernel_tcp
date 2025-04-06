Code for research paper: An Empirical Study of Test Case Prioritization on the Linux Kernel

Main scripts for studied TCP approaches are as follows:

- IR-based : ir_main.py

- similarity-based : similarity_main.py

- coverage-based : coverage_main.py (the coverage data is collected by gcov, related logic is located in collect_coverage.py)

- ML-based : ml_tcp.py


## Dataset

All collected dataset are stored in a sql file. We use mysql as the SQL backend. 
The structure of dataset can be found at database_structure.sql.
The full dataset can be downloaded at [dataset.sql](https://www.alipan.com/s/FFxRPVDgSkw)

The dataset contains the regression results collected from LKFT (Linux Kernel Functional Testing) project. 
The dataset involves various kernel versions across different architectures. 
See [Database Structure](https://github.com/wanghaichi/kernel_tcp?tab=readme-ov-file#database-structure) for details.

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

## Database Structure

Detailed of each table (only necessary fields are presented, also see database_structure.sql):

### Checkout

| Column Name     | Comment                  |
|-----------------|--------------------------|
| id              | unique id for checkout   |
| status          | status for this checkout |
| git_repo        | kernel git repository    |
| git_repo_branch | kernel git branch        |
| git_sha         | signature of git version |
| git_describe    | name for this checkout   |
| kernel_version  | label of kernel version  |

### Build

| Column Name  | Comment                        |
|--------------|--------------------------------|
| id           | unique id for build            |
| checkout_id  | belonging Checkout id          |
| plan         | name for build plan            |
| kconfig      | kernel config name             |
| arch         | kernel architecture            |
| build_name   | name for this build            |
| status       | status of this build           |
| duration     | total time spent on this build |
| start_time   | start time                     |

### TestRun

| Column Name  | Comment                        |
|--------------|--------------------------------|
| id           | unique id for each test run    |
| build_id     | belonging build id             |
| tests_file   | configuration file             |
| log_file     | log file                       |
| test_url     | url for this test run          |
| job_url      | url for the test job           |

### Test

| Column Name  | Comment                                           |
|--------------|---------------------------------------------------|
| id           | unique id for a test                              |
| testrun_id   | belonging testrun id                              |
| status       | status of test                                    |
| path         | name of test                                      |
| log_url      | url of execution log                              |
| environment  | kernel environment                                |
| suite        | belong test suite name                            |
| file_path    | added by authors, the file path mapped by `path`  |
| TP           | added by authors, mark whether it is a flaky test |