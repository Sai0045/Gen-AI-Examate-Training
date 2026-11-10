from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SmartSearch:
    def __init__(self, records):
        self.records = records

        # join all the text fields of a record into one string
        texts = []
        for r in records:
            text = (r["vaccine"] + " " + r["due_age"] + " " + r["latest_age"] + " "
                    + r["dose"] + " " + r["route_site"] + " " + r["protects_against"])
            texts.append(text)

        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform(texts)

    def search(self, query, top_k=5):
        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix)[0]

        # best scores first
        order = scores.argsort()[::-1]
        results = []
        for i in order[:top_k]:
            if scores[i] > 0:
                item = dict(self.records[i])
                item["score"] = round(float(scores[i]), 3)
                results.append(item)
        return results
