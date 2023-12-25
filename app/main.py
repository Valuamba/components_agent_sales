from fastapi import FastAPI, Depends
from config import app_settings
from services import DetailInfoRepository

import psycopg2


app = FastAPI()


def get_db_connection():
    db_connection = psycopg2.connect(app_settings.famaga_db_url)
    db_connection.autocommit = True
    try:
        yield db_connection
    finally:
        db_connection.close()

def get_famaga_repository(db_connection=Depends(get_db_connection)):
    db_cursor = db_connection.cursor()
    try:
        repository = DetailInfoRepository(
            cursor=db_cursor,
            similarity_search_limit=app_settings.similarity_search_limit,
            vector_collection_name=app_settings.vector_collection_name
        )
        yield repository
    finally:
        db_cursor.close()

@app.get("/")
async def root(famaga_repo: DetailInfoRepository = Depends(get_famaga_repository)):

    details = famaga_repo.select_detail_by_part_number('snM-98-1E8')

    return {
        "message": "Hello World",
        "key": app_settings.openai_api_key,
        "count": len(details)
    }