

from fastapi import FastAPI,File,UploadFile,HTTPException
from pathlib import Path
MAX_SIZE:int = 1024*1024*5
app = FastAPI()
@app.post('/upload',status_code=202)
async def upload(file:UploadFile = File(...)):
    # 文件上传要校验
    if Path(file.filename).suffix  == '.pdf' and file.size<MAX_SIZE:
        return {"filename":file.filename,"size":file.size}
    raise HTTPException(status_code=400,detail="Invalid file")
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app,host='127.0.0.1',port=8000)



#