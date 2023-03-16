
# Introduction

This repo allows you to run experiments (question classification/answering) and perform various other tasks such as csv augmentation and computing metrics. For now, I will focus on running experiments.


## Environment Setup

1. Create a new Python virtual environment by doing: ```python -m venv [VIRTUALENV-NAME]```
   - ensure you are using python3.9 or higher
   - if you are using Vector machines which have python version == 3.6.9. you might want to use Anaconda to install python3.9 first
2. Activate the virtual environment: ```source <venv>/bin/activate```
3. Install dependencies: ```python -m pip install -r ./requirements.txt ```
4. Store your openai api key in a text file and set general_params['openai-key-path'] to point to it. Alternatively, you can set the `OPENAI_API_KEY` environment variable. 
5. Try running ``` python main.py experiments -re ``` which will classify 2 samples in: `datasets/sample-data.csv` and save the results in ```datasets/runs/```



# Experiment Running Framework

At a high-level, my framework takes a CSV file and performs question classification/answering across rows on the CSV. Experiment stats and the CSV file augmented with model classifications/answers gets saved to a directory. `experiments/` contains all files associated with running experiments.

## Directory Structure


 `experiments/`
 - `hyperparameters.py` : Classify hyperparameters
 - `answer_hyperparameters.py` : Answer hyperparameters
 - `logprobs_hyperparameters.py` : Instructor answer log probabilities hyperparameters
 - `prompts.py` : Prompts used for the above 3 hyperparameter files
 - `run_experiments.py` : Main script for running experiments

## Usage

``` python main.py experiments -re ```

This will run `run_experiments.py` using the parameters in `hyperparameters.py`. The default hyperparameters are for the classification task. To do question-answering, rename `answer_hyperparameters.py` to `hyperparameters.py`. 

## How it works

`hyperparameters.py` contains all the parameters associated with an experiment. Running the above command will perform classification/question-answering on dataset_params['dataset_path'] using dataset_params['num_samples']. Experiment info gets saved in general_params['run_dir]. 

### Classification

dataset_params['dataset_path'] should include a label called *target* (can be empty) which is the ground truth question category. The script will take this dataset, create a new column called *classification* and populate it with model classifications.


## Improvements

- makes more sense for `hyperparameters.py` to be a YAML file










