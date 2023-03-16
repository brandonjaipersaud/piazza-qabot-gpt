import numpy as np


def compute_perplexity(logprobs:list):
    """Dfn 2 in blog post"""
    sum_probs = -1 * (np.sum(logprobs) / len(logprobs))
    return 2 ** sum_probs


def compute_perplexity_sanity(logprobs:list):
    """
    Another dfn based on directly computing entropy.
    Entropy = negated avg log prob. Assumes each token is equally likely (uniform distribution).
    """
    logprobs = np.asarray(logprobs)
    probs = 2 ** logprobs

    # entropy = -1 * (np.sum(logprobs * probs))
    entropy = -1 * ((np.sum(logprobs)) / len(logprobs))

    return 2 ** entropy


def compute_perplexity_sanity2(logprobs:list):
    """ Dfn 1 in blog post
        https://towardsdatascience.com/perplexity-in-language-models-87a196019a94#
    
    """
    logprobs = np.asarray(logprobs)
    probs = 2 ** logprobs
    perplexity = (1 / np.prod(probs)) ** (1/len(probs))
    return perplexity