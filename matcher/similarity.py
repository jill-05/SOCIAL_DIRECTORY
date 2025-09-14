from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

def embedding_similarity(text1, text2):
    if not text1 or not text2:
        return 0.0
    emb1 = model.encode(text1, convert_to_tensor=True)
    emb2 = model.encode(text2, convert_to_tensor=True)
    return float(util.cos_sim(emb1, emb2))
