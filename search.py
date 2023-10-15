import torch
from sentence_transformers import SentenceTransformer, util



TOP_K = 10 

class VectorSearch:
    def __init__(self, embedder, threshold_percentage=0.03):
        self.embedder = embedder
        self.threshold_percentage = threshold_percentage

    def search(self, corpus, embeddings, queries):
        # Initialize lists to store scores and indices for each query
        all_scores = []
        all_indices = []

        for query in queries:
            # Encode the user query
            query_embedding = self.embedder.encode(query, convert_to_tensor=True)

            # Calculate cosine similarity and find the top-k results
            top_k = min(200, len(corpus))
            scores = []
            indices = []

            for i, emb in enumerate(embeddings):
                cos_score = util.pytorch_cos_sim(query_embedding, emb)[0]
                scores.append(cos_score.item())  # Convert tensor to a scalar
                indices.append(i)

            # Sort by scores
            sorted_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)

            query_scores = []
            query_indices = []
            highest_score = max(scores)
            threshold = (1 - self.threshold_percentage) * highest_score  # Set threshold as 2 percent below the highest score

            for i in sorted_indices:
                score = scores[i]
                if score >= threshold:
                    idx = indices[i]
                    query_scores.append(score)
                    query_indices.append(idx)

            all_scores.append(query_scores)
            all_indices.append(query_indices)

        # Return the highest results for each query
        results = []
        for query, scores, indices in zip(queries, all_scores, all_indices):
            query_results = []
            for score, idx in zip(scores, indices):
                result = {
                    'Query': query,
                    'Job Position': corpus.iloc[idx],
                    'Score': score
                }
                query_results.append(result)
            results.append(query_results)

        return results
