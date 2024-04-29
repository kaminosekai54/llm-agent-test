# Conda Environment Setup and Package Installation Tutorial

This tutorial guides you through the process of setting up a Conda environment, installing necessary packages, and setting up a project from GitHub. It is tailored for Windows users but can be adapted for other operating systems with minor adjustments.

## Step 1: Install Miniconda

1. Visit the [Miniconda installation page](https://docs.anaconda.com/free/miniconda/) and select the appropriate version for your operating system. For saving space on your hard drive, Miniconda is recommended over the full Anaconda distribution.
2. Click on the desired installer to begin the download.
3. Once downloaded, navigate to your download folder (or wherever the installer was saved) and double-click on the installer.
4. Follow the on-screen instructions to complete the installation.

## Step 2: Create a Conda Environment

### Option A: Create Manually

1. Press the Windows button and search for "Anaconda Prompt" to open the Anaconda Prompt application.
2. In the Anaconda Prompt, create a new Conda environment by typing:
    ```
    conda create -n crewAI
    ```
3. Accept the installation prompts and wait for the environment creation process to complete.
4. To activate your newly created environment, type:
    ```
    conda activate crewAI
    ```
   If you have chosen a different name for your environment, replace `crewAI` with the name of your environment.

### Option B: Create from `.yml` File

1. Ensure you have a `.yml` file that defines the environment setup. This file typically includes the environment name, dependencies, and potentially other configurations.
2. To create and activate the environment from the `.yml` file, use the following commands in the Anaconda Prompt:
    ```
    conda env create -f env.yml
    conda activate crewAI
    ```
   Replace `environment.yml` with the path to your `.yml` file. The environment name inside the `.yml` file will be used automatically.

## Step 3: Install Required Packages

Inside the activated Conda environment, install the following packages:

```shell
conda install conda-forge::biopython
conda install anaconda::pandas
pip install crewai[tools]
pip install streamlit
pip install xmltodict
pip install langchain_community
```

If you installed the environment with the yml file, this step can be ignored.

## Step 4: Download and Install Ollama (if you are using ollama, other wise, skip this step)

1. Navigate to the [Ollama download page](https://ollama.com/download) and click on the Windows version to start the download.
2. Once downloaded, go to your download folder and double-click on the Ollama installer.
3. Follow the on-screen instructions to complete the installation.
4. Return to your Anaconda Prompt and type `ollama` to check if it's correctly installed. If you encounter issues, try closing and reopening the Anaconda Prompt, reactivating your environment, and retrying. If it still does not work, a system reboot may be necessary.

## Step 5: Run Ollama Commands

With Ollama installed and your Conda environment activated, you can run specific Ollama commands. For instance:

```shell
ollama run mistrale
```

This command downloads and runs the Mistrale model from Ollama's servers. Press `Ctrl + D` to quit once it's running.

## Step 6: Clone and Run a GitHub Project

1. In the Anaconda Prompt, navigate to the directory where you wish to clone the GitHub project. Use the `cd` command to change directories, e.g., `cd desktop`.
2. Clone the GitHub repository by typing:
    ```
    git clone https://github.com/kaminosekai54/llm-agent-test
    ```
3. Navigate into the repository folder:
    ```
    cd llm-agent-test
    ```
4. Finally, run the Streamlit application by typing:
    ```
    streamlit run streamlit-app.py
    ```

If everything is set up correctly, the application should run without issues.
