import numpy as np


def my_euclidean_distance(v1, v2):
    """Compute the Euclidean distance between two vectors."""
    if len(v1) != len(v2):
        raise ValueError("Vectors must have the same length")
    return sum((x - y) ** 2 for x, y in zip(v1, v2)) ** 0.5

def my_cosine_similarity(A, B):
    dot_product = np.dot(A, B)

    # calculate magnitude of A and B
    magnitude_A = np.linalg.norm(A)
    magnitude_B = np.linalg.norm(B)

    # calculate cosine similarity
    cosine_similarity = dot_product / (magnitude_A * magnitude_B)

    # get the angle. take inverse cosine to get angle

    return cosine_similarity