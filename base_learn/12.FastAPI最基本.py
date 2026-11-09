
from fastapi import FastAPI
from pydantic import BaseModel,Field
app = FastAPI()
@app.get('/article')
async def get_article_list():
    return [{"id": 1, "title": "Article 1"}, {"id": 2, "title": "Article 2"}]



if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)



