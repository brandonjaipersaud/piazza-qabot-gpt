import numpy as np

def is_empty(text):
    if type(text) == float and np.isnan(text):
        return True
    if text == "" or text == None:
        return True
   
    return False