from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

_model = None


def get_model():
    # load the embedding model only once
    global _model
    if _model is None:
        _model = DefaultEmbeddingFunction()
    return _model


def embed_texts(texts):
    # returns one list of numbers for every text
    vectors = get_model()(texts)
    return [[float(x) for x in v] for v in vectors]