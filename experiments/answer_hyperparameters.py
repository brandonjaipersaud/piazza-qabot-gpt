"""
Answering hyperparameters.
Stores hyperparameters associated with a single experiment.
"""

# added relative import
from experiments.prompts import * 


general_params = {

  "run_dir" : "./datasets/20230311-140017_/",  # directory to store experiment runs
  "run_suffix_tag" : "",  # a way of easily identifying run. alter to name your run
  "openai-key-path": "",
  "save_run" : True, # keep on for now
  "verbose" : True

}


control_params = {

    "generate_instructor_answer_logprobs" : False,

    "classify" : False, # whether we are classifying or answering a question

    "evaluate" : False,
    "inference" : True, 
   
    "plot_metrics" : False,  # useful to toggle on plot_metrics and toggle off eval + inf. eval + inf usually done together. 
}



model_params = {
    "model":"text-davinci-003", 
    "max_tokens":200, 
    "top_p":1, 
    "temperature":0.7, 
    "n":1,
    "logprobs":None,
    "echo" : False,
    # modify from external file
    "prompt" : ANSWER_PROMPT  # change this to your prompt
    
}


dataset_params = {

  "shuffle":False, # don't shuffle to keep consistent dataset between runs
  "num_samples":2, # None -> use all samples. Set low by default to avoid doing expensive forward pass
  "stratified":False,  # unused
  # also be able to set this as a pd dataframe
  "dataset_path" : "./datasets/runs/20230313-133454_/classify_inference.csv",  # path to dataset to classify
  
  "labels" : ["conceptual", "homework", "logistics", "not answerable"]  # dataset classification labels

}