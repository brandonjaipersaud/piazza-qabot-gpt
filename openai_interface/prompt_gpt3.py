import openai
import openai.error 

from experiments.hyperparameters import *

def gpt3_embeddings(input, model="text-embedding-ada-002", print_response=False):
    response = openai.Embedding.create(
        input=input,
        model=model
    )

    if print_response:
        print(response)

    embeddings = response['data'][0]['embedding']
    return embeddings




def prompt_gpt3(prompt, model=model_params['model'], max_tokens=model_params['max_tokens'], \
                top_p=model_params['top_p'], temperature=model_params['temperature'], n=model_params['n'], \
                logprobs=model_params['logprobs'], echo=model_params['echo'], config=None, max_attempts=3):

    """Prompt gpt3 based on model parameters specified in hyperparameter.py
        TODO
        - change so it loads from config. set defaults.
    """

    
    response = None

    if config:
        model = config['model']
        # prompt = config['prompt']
        max_tokens = config['max_tokens']
        top_p = config['top_p']
        temperature = config['temperature']
        n = config['n'],
        echo = config['echo']

    while(response == None and max_attempts > 0):
        try:
            response = openai.Completion.create(
                model=model,
                prompt=prompt,
                max_tokens=max_tokens,
                top_p=top_p,
                temperature=temperature,
                n=n,
                logprobs=logprobs,
                echo=echo
            )

        except openai.error.RateLimitError:
            print(f'Rate Limited. Max attempts: {max_attempts}. Trying again')
            max_attempts -= 1


    return response





def prompt_gpt3_test(prompt, model="text-davinci-003", max_tokens=200, \
                top_p=1, temperature=0.7, n=1, config=None, return_text=False):

    """Prompt gpt3 based on model parameters specified in hyperparameter.py
        TODO
        - change so it loads from config. set defaults.
    """

    if config:
        model = config['model']
        # prompt = config['prompt']
        max_tokens = config['max_tokens']
        top_p = config['top_p']
        temperature = config['temperature']
        n = config['n']


    response = openai.Completion.create(
        model=model,
        prompt=prompt,
        max_tokens=max_tokens,
        top_p=top_p,
        temperature=temperature,
        n=n
    )
    if return_text:
        return response['choices'][0]['text']

    return response