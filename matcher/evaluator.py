def evaluate_precision_at_k(predicted: list, relevant_ids: set, k=10):
    top_k = predicted[:k]
    hits = sum(1 for cand_id in top_k if cand_id in relevant_ids)
    return hits / k

def dummy_relevant_ids(df):
    # For mock testing: assume top viewed candidates are relevant
    return set(df.sort_values(by="Views_norm", ascending=False).head(10).index)
