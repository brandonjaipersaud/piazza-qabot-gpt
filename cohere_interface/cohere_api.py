import cohere


def cohere_embeddings(text:str,api_key:str, model_size:str='large'):
    co = cohere.Client(api_key) # This is your trial API key

    response = co.embed(
        model=model_size,
        texts=[text])
    return response.embeddings[0]