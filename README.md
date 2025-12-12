# Artifact - Action Required: A Mixed-Methods Study of Security Practices in GitHub Actions
This repository contains the research artifacts associated with our NDSS 2026 paper, "Action Required: A Mixed-Methods Study of Security Practices in GitHub Actions."

## Overview
This repository provides research scripts for analyzing security practices in GitHub Actions.  
Using these scripts, you can perform the following tasks:
* Create a dataset of repositories that use GitHub Actions (Feature-1)
* Analyze the adoption of security practices in the collected repositories (Feature-2)

The security practices investigated in these scripts are as follows:
* [P1] Using CODEOWNERS to monitor changes
* [P2] Good practices for mitigating script injection attacks
* [P3] Using OpenSSF Scorecard to secure workflows and repositories
* [P4]Using third-party actions
  * Pin third-party actions to a full-length commit SHA
  * Pin third-party actions to a tag only if you trust the creator
* [P5] Using Dependabot version updates to keep actions up to date

For clarity, each practice is assigned an identifier (P1–P5), which is also used consistently in this repository.

These practices are based on GitHub’s official documentation:  
https://docs.github.com/en/actions/reference/security/secure-use


This repository also contains supplementary materials related to the user study, including questionnaires, email templates, and detailed study results, in the `supplementary_materials` directory.  
The directory also includes acknowledgements.


## Environment
The scripts have been tested and verified under the following environment:

- OS: Ubuntu 22.04  
- Python: 3.13.9  
- Storage: 30 GB (for DEBUG mode)

The scripts are designed for Unix-based systems (e.g., Linux, macOS). Due to path handling differences, they may not work properly on Windows.  

Hardware specifications (CPU, memory, storage) should be adjusted according to the scale of your experiment. Since the tool clones repositories locally, sufficient storage capacity is recommended.

## How to setup
### 1. Install Dependencies
Install the required Python packages:
```{bash}
pip install -r requirements.txt
```

### 2. Add Execution Permission
Grant execute permission to all shell scripts in the project:
```{bash}
chmod +x *.sh
```

### 3. Create Fine-grained Personal Access Token (PAT)
Please create a Fine-grained Personal Access Token (PAT) by following the official GitHub documentation:  
https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token

When creating the token, keep the repository access setting as the default (“Public repositories”) and no additional permissions are required.

If you do not have a GitHub account, please create one first at https://github.com/signup.

> [!NOTE]
> Although a Classic Personal Access Token also works, it grants broad access permissions to every repository that you can access.
> Therefore, we strongly recommend using a Fine-grained Personal Access Token.


### 4. Copy and modify `settings.py`
Create the settings file from the template:
```{bash}
cp src/template_settings.py src/settings.py
```

Then, open `src/settings.py` and set the Personal Access Token you created in the previous step.
```{python}
PERSONAL_ACCESS_TOKEN = "github_pat__xxxxxxxxxxxxxxxxxxxxx"
```

> [!NOTE]
> This tool also supports authentication via a [GitHub App](https://docs.github.com/en/apps/creating-github-apps).
> For details on how to use this mode, please refer to the comments in `settings.py`

## How to Use
### [Feature-1] Create Repsotirory Dataset
This section explains how to create a dataset of repositories that use GitHub Actions.  

#### • Prepare Input Data
Access [SEART-GHS](https://seart-ghs.si.usi.ch/) and specify the "Created Between" period (e.g., January 1, 2024 – December 31, 2024) to search for repositories.
Once the search results are displayed, click “Download CSV” to download the results in CSV format.  

The file will be downloaded as a `.tar.gz` archive.  
Please extract it and save the resulting file as: `./data/raw/results.csv`

> [!NOTE]
> The 'Created Between' filter is the minimum requirement for this tool since it organises repositories on a time-based axis (monthly split).
> Depending on your analysis goals or dataset scope, you can also apply other filters, such as the number of stars, commits, or programming language.

#### • Execution
You can execute this process either automatically (recommended) or manually, depending on your workflow preferences.

Option A: Automatic Execution (Recommended).  
Run the provided shell script `./create_dataset.sh`.  
It takes two arguments that specify the start and end months of the analysis period, written in the `YYYY-MM` format.   
When executed, the shell script automatically runs a series of Python scripts to create the dataset.

```bash
./create_dataset.sh YYYY-MM YYYY-MM
```

Option B: Step-by-step Execution.  
If you prefer to run each stage manually for debugging or partial reruns, execute the Python scripts in the following order.  
Each script performs a specific part of the dataset creation process, and they can be run either in sequence or independently when needed.

 ```bash
# Step 1: Split SEART-GHS dataset by month
python ./src/create_dataset/1_split_seartghs_by_month.py --start YYYY-MM --end YYYY-MM

# Step 2: Retrieve workflow files for repositories
python ./src/create_dataset/2_get_workflows_for_repos.py --start YYYY-MM --end YYYY-MM

# Step 3: Clone repositories and check usage
python ./src/create_dataset/3_clone_and_check_repository.py --start YYYY-MM --end YYYY-MM

# Step 4: Show the summary of dataset
python ./src/create_dataset/show_result.py --start YYYY-MM --end YYYY-MM
```

#### • Output
After successfully running `./create_dataset.sh` or executing `./src/create_dataset/show_result.py` directly, a summary like the following will be displayed.  
This summary shows the proportion of repositories that use GitHub Actions among all the repositories included in the dataset.
```
=== GitHub Actions Usage Summary ===
Total Repositories: 596
Repositories Using GitHub Actions: 192
GitHub Actions Usage Percentage: 32.21%
```

In addition, various files are generated under the `./data/dataset` directory, which constitute the contents of the dataset. 
For details, see Dataset Structure.


### [Feature-2] Analyze Security Practices
This section explains how to analyze the adoption of security practices in repositories that use GitHub Actions.  

#### • Prepare Input Data
Before starting the analysis, make sure that the repository dataset has been created by completing **Create Repository Dataset**.  
The analysis scripts rely on the data generated in that step.

Next, run `pre_analysis.sh` to prepare intermediate data required for practice analysis.  
This script takes two arguments representing the start and end months of the analysis period in the `YYYY-MM` format.
```bash
./pre_analysis.sh YYYY-MM YYYY-MM
```
The script automatically collects and organizes additional metadata necessary for evaluating the security practices.
Although each process in `pre_analysis.sh` can be executed individually, its detailed is omitted in this README.

#### • Execution
You can execute the analysis either automatically (recommended) or for each practice individually.

Option A: Automatic Execution (Recommended).  
Run the provided shell script `./analyze_security_practices.sh`.  
It takes two arguments that specify the start and end months of the analysis period, written in the `YYYY-MM` format. 
When executed, the shell script automatically runs all five practice analyses and summarizes the results.

```bash
./analyze_security_practices.sh YYYY-MM YYYY-MM
```

Option B: Practice-by-Practice Execution.  
If you prefer to run specific analyses individually, each practice can be executed separately using the corresponding Python script.
This is useful when re-analyzing only part of the dataset or debugging a specific module.

```bash
# Practice 1: CODEOWNERS
python src/analyze_security_practices/analyze_p1_codeowners.py --start YYYY-MM --end YYYY-MM

# Practice 2: Mitigating Script Injection
python src/analyze_security_practices/analyze_p2_mitigating_injection.py --start YYYY-MM --end YYYY-MM

# Practice 3: OpenSSF Scorecard
python src/analyze_security_practices/analyze_p3_scorecard.py --start YYYY-MM --end YYYY-MM

# Practice 4: Pinning Third-Party Actions
python src/analyze_security_practices/analyze_p4_pinning_actions.py --start YYYY-MM --end YYYY-MM

# Practice 5: Dependabot
python src/analyze_security_practices/analyze_p5_dependabot.py --start YYYY-MM --end YYYY-MM
```

After running one or more analyses, you can aggregate and display the overall results using the following commands:
```bash
python src/analyze_security_practices/get_result.py --start YYYY-MM --end YYYY-MM
python src/analyze_security_practices/show_result.py --start YYYY-MM --end YYYY-MM
```



#### • Output
After successfully running `analyze_security_practices.sh` or executing individual analysis scripts, a summary of the implementation rates for each security practice will be displayed at the end of the process.

```
=== Security Practice Implementation Results ===
practice1:
  Target Repositories: 192
  Implemented Repositories: 17
  Implementation Rate: 8.85%

practice2:
  Target Repositories: 39
  Implemented Repositories: 18
  Implementation Rate: 46.15%

...
```

The resulting data are stored under the `./data/analyzed_data/` directory.  
Each security practice has its own subdirectory (e.g., `./data/analyzed_data/practice1`), and the results are organized by month within those folders.
For details, see Dataset Structure.


## Appendix
### Example Data
As a small-scale example, we provide a set of five repositories with different patterns,  
along with their corresponding analysis data, in the `example_data` directory.  

These examples are limited in scope and are intended primarily for testing the analysis scripts  
and demonstrating how the framework identifies whether each security practice is implemented or not,  
rather than serving as a full benchmark dataset.

You can test the script using the following command:
```bash
$ ./test_example.sh
```

### DEBUG Mode
A debug mode is provided for development and quick testing.  
By default, the number of repositories collected per month is limited to **up to 50**, which allows for lightweight execution and easy verification of functionality.  

These settings can be modified in `settings.py`:
```python
DEBUG = True
DEBUG_DATA_NUM = 50
```


Disabling the debug mode enables large-scale data collection and experiment. However, please note the following considerations:
* API Rate Limit
  * The GitHub REST API imposes a limit of 5,000 requests per hour for regular users.
  * Running large-scale analyses under this limit will take a very long time.
  * GitHub Enterprise users have a higher limit of 15,000 requests per hour, which is recommended for large-scale studies.
  * See the GitHub API rate limit documentation

* Storage Requirements
  * The scrips clones all target repositories locally.
  * Conducting large-scale analyses will therefore consume substantial disk space.
  * In our study, analyzing approximately 340,000 repositories required about 30 TB of storage.
  * Ensure that you have sufficient storage capacity before running the full experiment.


### Dataset Structure
The organizes data under the `data/` directory as follows:

```
data/
├── raw/
│   └── results.csv                     # Downloaded from SEART GHS
├── dataset/
│   ├── seartghs_by_month/              # Split datas SEART-GHS by month
│   ├── gha_check/                      # List of repositories identified as using GitHub Actions
│   ├── repo_workflows/                 # Results obtained from the GitHub API for workflow data
│   └── cloned_repos/
│       └── {owner}/{repository}/       # Locally cloned repositories
└── analyzed_data/
    ├── repository_data/                # Collected and analyzed repository data 
    ├── actions_data/                   # Collected and analyzed actions data
    ├── results/                        # Aggregated result
    ├── practice1/                      # Analysis result for Practice 1
    ├── practice2/                      # Analysis result for Practice 2
    ├── practice3/                      # Analysis result for Practice 3
    ├── practice4/                      # Analysis result for Practice 4
    └── practice5/                      # Analysis result for Practice 5

```
