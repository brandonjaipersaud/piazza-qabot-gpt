"""
Stores hyperparameters associated with a single experiment.
"""

# added relative import
from experiments.prompts import * 


general_params = {

  "run_dir" : "./paper_data/important/",  # directory to store experiment runs
  "run_suffix_tag" : "",  # a way of easily identifying run. alter to name your run
#"run_suffix_tag" : "plot-everything",  # a way of easily identifying run. alter to name your run
  "openai-key-path": "./sensitive/openai_api_key.txt",
  "run_info" : "binary classification",
  "save_run" : True, # keep on for now
  "verbose" : True

}


control_params = {

    "generate_instructor_answer_logprobs" : True,

    "classify" : False, # whether we are classifying or answering a question

    "evaluate" : False,
    "inference" : True, 
   
    "reuse_run" : False,
    "reuse_run_dir" : None,

    "plot_metrics" : False,  # useful to toggle on plot_metrics and toggle off eval + inf. eval + inf usually done together. 
    "plot_dirs" : ['20221129-143038', '20221129-143351', '20221129-143624', '20221129-143914', '20221129-144250', '20221129-144405' ]  # array of run dirs whose eval metrics to plot. only specify timestamps
}



model_params = {
    "model":"text-davinci-003", 
    "max_tokens":0, 
    "top_p":1, 
    "temperature":0.7, 
    "n":1,
    "logprobs":5,
    # modify from external file
    "prompt" : LOGPROB_PROMPT,  # change this to your prompt
    "echo" : True
}


dataset_params = {

  "shuffle":False, # don't shuffle to keep consistent dataset between runs
  "num_samples":None, # None -> use all samples. Set low by default to avoid doing expensive forward pass
  "stratified":False,  # unused
  # also be able to set this as a pd dataframe
  "dataset_path" : "datasets/311/csc311_f22_lisa_feedback_embeddings.csv",  # path to dataset to classify
  
  "dataset_info": "",

  #"labels" : ['answerable', 'unanswerable', 'answerable with the right context'] 
  "labels" : ["conceptual", "homework", "logistics", "not answerable"]  # dataset classification labels

}