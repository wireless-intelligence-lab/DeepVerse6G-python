DeepVerse 6G: Python Data Generator
===========================================================================
Welcome to the python data generator repository for the **DeepVerse 6G** dataset. DeepVerse 6G is a framework designed to generate synthetic yet high-fidelity multi-modal sensing and communication datasets, tailored for 6G research and development involving digital twins.

This repository specifically contains the python scripts used to generate the multi-modal data using the scenario files presented in the main project website.
The repository is also available via pypi and can be directly installed via `pip install deepverse`.

**Main Dataset Website:** [`https://deepverse6g.net/`](https://deepverse6g.net/)

Features of DeepVerse 6G Framework
----------------------------------
* **High-Fidelity:** Leverages ray-tracing (via Remcom Wireless InSite) for realistic channel modeling.
* **Multi-Modal:** Integrates communication channel data with sensing modalities (e.g., lidar, vision).
* **Synthetic & Controllable:** Enables generation of diverse datasets tailored to specific research needs.
* **Digital Twin Focused:** Designed to support research in digital twin applications for wireless systems.

Dataset Access
--------------
The datasets using DeepVerse 6G dataset scenarios are generated with these scripts (including channel data, sensor data, etc.). The scenarios can be explored from the main website under the scenarios tab.

**Example Scenarios:**
- Outdoor 1: https://deepverse6g.net/scenario/O1
- Indoor 1: https://deepverse6g.net/scenario/I1
- Carla Town 1: https://deepverse6g.net/scenario/Carla-Town1
- Carla Town 5: https://deepverse6g.net/scenario/Carla-Town5
- Digital Twin 1: https://deepverse6g.net/scenario/DT1
  - Digital Twin to real world dataset: [DeepSense Scenario 1](https://www.deepsense6g.net/scenarios/scenario-1/)
- Digital Twin 31: https://deepverse6g.net/scenario/DT31
  - Digital Twin to real world dataset: [DeepSense Scenario 31](https://www.deepsense6g.net/scenarios/scenario-31/)

Generator Code (This Repository)
--------------------------------
This repository provides the python scripts to reproduce or generate the DeepVerse 6G datasets.

**Installation:**

There are two primary ways to install the necessary Python code:

1.  **From PyPI (Recommended for general users):**
    This installs the latest stable release of the ``deepverse`` package directly from the Python Package Index.

        pip install deepverse

2.  **From this Repository (Recommended for developers or latest version):**
    This method allows you to install the package directly from a cloned copy of this repository. This is useful for development, contributing, or accessing the absolute latest changes.

    a. Clone this repository:

           git clone https://github.com/wireless-intelligence-lab/DeepVerse6G-python.git

    b. Navigate into the cloned directory:
       *(Note: The directory name is typically the repository name)*

           cd DeepVerse6G-python

    c. Install the package locally:
       * For a standard install from the local source code:

               pip install .
       * For an "editable" install (recommended for development, where changes in your local source code are immediately reflected in the installed package without needing to reinstall):

               pip install -e .


**Setup: Scenario Files:**

1.  Select a scenario and download its associated files from the DeepVerse 6G website: (https://deepverse6g.net/)
2.  Create a folder named `scenarios` in the root directory of this cloned repository (or another `scenarios` folder location to be specified in the parameter configuration).
3.  Extract the downloaded scenario files into the `scenarios` folder.

Note: This manual step is required because the scenario files are large and the users can only pick/download the desired scenarios and modalities.

**Usage:**

The primary steps involve configuring parameters and calling the generation functions provided by the `deepverse` package.

1.  **Detailed Configuration & Generation:**
    Please refer to the official documentation for comprehensive instructions on configuring parameters and initiating dataset generation:
    * [Starting with DeepVerse6G](https://deepverse6g.net/documentation)

2.  **Basic Example (Illustrative):**

        import deepverse as dv
  
        # Load configuration
        # Example config files are available for each scenario on their page, please set the file path accordingly.
        config_path = "../params/config.m"
        param_manager = dv.ParameterManager(config_path)
    
        # Set path to scenario files and selected scenario
        # The following path needs to be updated as the `scenario` folder mentioned in the `Setup: Scenario Files` step above.
        param_manager.params['dataset_folder'] = r'D:\DeepVerse\scenarios'
        param_manager.params['scenario'] = 'Town01-Carla'
  
        # Run generation
        # dataset = dv.Dataset(param_manager)


License & Citation
------------------
The code in this repository is licensed under the [`Attribution-NonCommercial-ShareAlike 4.0 International`](https://creativecommons.org/licenses/by-nc-sa/4.0/).

If you use the DeepVerse 6G dataset, the generation framework, or these scripts (or any modified part of them) in your research or work, please cite the following:

1.  **The DeepVerse 6G Paper:**
    U. Demirhan, A. Taha, S. Jiang, and A. Alkhateeb "DeepVerse 6G: A Dataset Generation Framework for Multi-Modal Sensing and Communication Digital Twins," *preprint*, Feb. 2025.

    *BibTeX:*

        @article{DeepVerse,
          author  = {Demirhan, U. and Taha, A. and Jiang, S. and Alkhateeb, A.},
          title   = {{DeepVerse 6G}: A Dataset Generation Framework for Multi-Modal Sensing and Communication Digital Twins},
          journal = {preprint},
          year    = {2025},
          month   = {Feb}
        }

2.  **The Ray-Tracing Software used for the Scenarios:**
    Remcom, Wireless InSite: https://www.remcom.com/wireless-insite

    *BibTeX:*

        @article{Remcom,
          author = {Remcom},
          title  = {{Wireless InSite}},
          note   = {\url{https://www.remcom.com/wireless-insite}}
        }
