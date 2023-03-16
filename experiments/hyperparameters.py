"""
Classify hyperparameters.
Stores hyperparameters associated with a single experiment.
"""

# added relative import
from experiments.prompts import * 


general_params = {

  "run_dir" : "./datasets/runs/",  # directory to store experiment runs
  "run_suffix_tag" : "",  # a way of easily identifying run. alter to name your run
  "openai-key-path": None, # set to "" or None if setting environment variable
  "save_run" : True, 
  "verbose" : True

}


control_params = {

    # if this is True, set classify to False.  
    "generate_instructor_answer_logprobs" : False,

    # True -> question classification, False -> question answering
    "classify" : True, 

    # For classification. Whether to compute accuracy + confusion matrix between model_answer and target (ground truth)
    # ** toggle to True only if the target column in dataset_path is filled out **
    "evaluate" : False,
    # leave this at True
    "inference" : True, 
    "plot_metrics" : False
  
}


# these vary depending on task. For q&a, temp=0.7 and prompt=ANSWER_PROMPT
model_params = {
    "model":"text-davinci-003", 
    "max_tokens":200, 
    "top_p":1, 
    "temperature":0, 
    "n":1,
    "logprobs":None,
    "echo" : False,
    "prompt" : CLASSIFY_PROMPT  # change this to your prompt
}


dataset_params = {
  "shuffle" : False, # whether to shuffle the dataset before doing inference. For now, keep this False. 
  "num_samples":2, # None -> use all samples. Set low by default to avoid doing expensive forward pass
  "dataset_path" : "./datasets/sample_data.csv",  # path to dataset to classify or answer
  "labels" : ["conceptual", "homework", "logistics", "not answerable"]  # dataset classification labels

}