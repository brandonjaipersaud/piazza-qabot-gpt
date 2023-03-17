
# Introduction

This repo implements a question-answering system that uses decomposed prompting [1] to answer questions on the Piazza discussion board. We have a paper that is currently under review at AIED and ITiCSE 2023 which will be linked here after it is finished being reviewed.

This repo allows you to perform tasks such as the following:
- question classification/answering 
- csv augmentation 
- computing metrics
- deploy the bot on your Piazza instance
- scrape Piazza posts

## Environment Setup

1. Create a new Python virtual environment by doing: ```python -m venv <VIRTUALENV-NAME>```
   - ensure you are using python3.9 or higher
2. Activate the virtual environment: ```source <venv>/bin/activate```
3. Install dependencies: ```python -m pip install -r ./requirements.txt ```
4. Store your openai api key in a text file and set general_params['openai-key-path'] to point to it. Alternatively, you can set the `OPENAI_API_KEY` environment variable. 
5. Try running ``` python main.py experiments -re ``` which will classify 2 samples in: `datasets/sample-data.csv` and save the results in ```datasets/runs/```

# General Usage

The entry point of this program is in `main.py`. To see all options do:
```
python main.py -h
```

# Question Classification and Answering Framework

My framework takes a CSV file and performs question classification/answering across rows on the CSV. Experiment stats and the CSV file augmented with model classifications/answers gets saved to a directory. `experiments/` contains all files associated with running experiments.

## Directory Structure


 `experiments/`
 - `hyperparameters.py` : Classify hyperparameters
 - `answer_hyperparameters.py` : Answer hyperparameters
 - `logprobs_hyperparameters.py` : Instructor answer log probabilities hyperparameters
 - `prompts.py` : Prompts used for the above 3 hyperparameter files
 - `run_experiments.py` : Main script for running experiments

## Usage

``` 
python main.py experiments -re 
```


This will run `run_experiments.py` using the parameters in `hyperparameters.py`. The default hyperparameters are for the classification task. To do question answering, rename `answer_hyperparameters.py` to `hyperparameters.py`. 

## How it works

`hyperparameters.py` contains all the parameters associated with an experiment. Running the above command will perform classification/question answering on dataset_params['dataset_path'] using dataset_params['num_samples']. Experiment info gets saved in general_params['run_dir]. 

### Classification

dataset_params['dataset_path'] should include a label called *target* (can be empty) which is the ground truth question category. The script will take this dataset, create a new column called *classification* and populate it with model classifications.

# Computing Metrics

## Usage

To see csv metric computation options do:

``` 
python main.py metrics -h
```

This tool allows you to:

- Compute ROUGE score and cosine similarity between instructor and model answer. You can also compute perplexity of the instructor answer.

Doing:
``` 
python main.py metrics -m all
```

computes all metrics


# CSV Augmentation

## Usage

To see csv augmentation options do:

``` 
python main.py augment -h
```

This tool allows you to:

- perform general csv augmentations such as selecting certain columns, merging the columns of two csvs, etc. 
- generate OpenAI and Cohere embeddings of the instructor and model answer.
- Add timestamps to Piazza posts. 
- Compare timestamps between model and instructor answer to determine if the instructor answer comes before/after the model answer



# Deployment

To deploy the bot on a Piazza instance do:

``` 
python deployment/run_bot.py
```

Configure the deployment parameters in `deployment/config.yaml`

The deployment does two things. First, it classifies questions. Questions that are classified as *conceptual* will get answered and responded to on Piazza using the answer prompt in `experiments/prompts.py`.


# Scraping Piazza posts

`piazza_api_utils/scrape_posts.py` is a tool you can use to scrape Piazza posts.

## Usage

Scrape Piazza posts and save it to a file called csc311.json:

```
python3 scrape_posts.py creds-template.json -s -js ./csc311.json -ni 5 -t 2.5
```

-ni indicates how much posts to scrape. -t 2.5 means to set a 2.5s delay between scraping Piazza posts due to throttling. Do `scrape_posts.py -h` for a more detailed description of all options.

To convert the above json file to a nicely formatted csv file do:
```
python3 scrape_posts.py creds-template.json -c -cp csc311.csv  -jl csc311.json
```

For instructors, the csv schema will look like:

```
(post_id,is_private,question_title,question,folders,student_poster_name,date_question_posted, student_answer,student_answer_name,date_student_answer_posted,is_student_endorsed,is_student_helpful,instructor_answer,instructor_answer_name,date_instructor_answer_posted,is_instructor_helpful,is_followup)
```

For students, the csv schema will look like:
```
(post_id,question_title,question,folders,student_answer,instructor_answer)
```


## Future Directions

**Note that this is still a work in progress!** We are currently investigating:
- GPT Index (renamed to LlamaIndex) for answering questions that rely on context [2]
- GPT3.5 instead of text-davinci003
- prompt engineering strategies

## References

[1] [Decomposed Prompting: A Modular Approach for Solving Complex Tasks](https://arxiv.org/abs/2210.02406) 
[2] https://gpt-index.readthedocs.io/en/latest/index.html










