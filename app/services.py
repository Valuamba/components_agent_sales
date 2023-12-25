from models import Detail

from psycopg2.extensions import cursor as CursorType


class DetailInfoRepository:

    def __init__(self, cursor, vector_collection_name, similarity_search_limit):
        self.cursor: CursorType = cursor
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
            
            self.cursor.execute(query)
            all_matches = self.cursor.fetchall()
            
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
            return []

    def select_detail_by_part_number(self, part_number: str):
        query = f"select * from details_info where part_number='{part_number}'"

        try:
            self.cursor.execute(query)

            all_matches = self.cursor.fetchall()

        
            details = []
            for match in all_matches:
                details.append(Detail(
                    id=match[0],
                    part_number=match[1],
                    brand_name=match[4],
                    description=match[5]
                ))
            return details
        except:
            return []
