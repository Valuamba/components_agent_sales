from typing import List, Any

from sqlalchemy import text
from sqlalchemy.orm import Session
from models import Embedding


class EmbeddingRepository:
    def __init__(self, session: Session, vector_collection_name, similarity_search_limit):
        self.session = session
        self.vector_collection_name = vector_collection_name
        self.similarity_search_limit = similarity_search_limit

    def get_top_relevant_messages(self, embeddings, k=3):
        try:
            query = f"""
WITH vector_matches AS (
    SELECT brand_id, name, embedding <=> '{embeddings}' AS distance
    FROM {self.vector_collection_name}
)
SELECT brand_id, name, distance
FROM vector_matches
ORDER BY distance
LIMIT '{k}';
"""

            result = self.session.execute(text(query), {"embeddings": embeddings, "k": k})
            all_matches = result.fetchall()

            relevant_matches = []
            print('All matches:')
            for doc in all_matches:
                print(f'-- {round(doc[2], 2)}: {doc[1]}')

                if round(doc[2], 2) <= float(self.similarity_search_limit):
                    relevant_matches.append({
                        "document": doc,
                        "score": doc[2]
                    })

            if len(relevant_matches) == 0:
                print("No relevant matches found")
            else:
                print("Relevant matches: ")
                [print(f'-- {round(doc["score"], 2)}: {doc["document"][2]}') for doc in relevant_matches]
            return relevant_matches
        except Exception as e:
            print(f"[get_top_relevant_messages] {type(e).__name__} exception: {e}")
            raise e
            return []
