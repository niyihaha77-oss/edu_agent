import asyncio

from fastapi import FastAPI, Depends
from pydantic import BaseModel,Field
app = FastAPI()
@app.get('/article')
async def get_article_list():
    return [{"id": 1, "title": "Article 1"}, {"id": 2, "title": "Article 2"}]
class Login_request(BaseModel):
    username: str = Field(description='用户名')
    password: str = Field(description='密码')
# c r u d
# c --> post
# r --> get

  # u --> put(全量更新)/patch(增量更新)
# 请求体参数
@app.post('/login')
async def login(req:Login_request):
    if req.username == 'admin' and req.password == '123456':
        return {'code': 200, 'msg': '登录成功'}
    return {'code': 400, 'msg': '用户名或密码错误'}
    ...
# 路径参数
@app.get('/user/{user_id}/{user_name}')
async def get_user_info(user_id:str, user_name:str):
    return {"user_id": user_id, "user_name": user_name}
# 查询参数
@app.get('/goods')
async def get_goods_list(goods_id:str, goods_name:str):
    return {"goods_id": goods_id, "goods_name": goods_name}
# 依赖注入
def get_user_token() -> str:
    return '123456'
    ...
async def get_user_async() -> str:
    await asyncio.sleep(4)
    return '123456221'
# ===== 问题 1：路由路径缺少开头的 "/" =====
# 原写法 'users/chat/' 只补了结尾斜杠，开头仍然没有 "/"。
# FastAPI 会把它原样注册成 users/chat/，而请求进来的是 /users/chat/，
# Starlette 用 ^users/chat/$ 去匹配，永远匹配不上 → 访问一律 404。
# 原代码：
# @app.get('users/chat/')
#
# ===== 问题 2：函数名与上方的路径参数接口重名 =====
# 上方已有 async def get_user_info(...)，这里再定义会覆盖模块级同名函数。
# 目前只是靠 FastAPI 注册路由时已保存了函数引用才没出错，但后患很大。
# 原代码：
# async def get_user_info(token:str = Depends(get_user_token)):
#
# ===== 修正后：路径以 "/" 开头，函数名改为不重名的 get_user_chat =====
@app.get('/users/chat')
async def get_user_chat(token:str = Depends(get_user_token)):
    return {'token': token}
    ...
# ===== 问题 3：路径 "users/async/" 同样缺少开头的 "/" =====
# 注册出来的字面量是 users/async/，请求 /users/async/ 时匹配不上，返回 404。
# 原代码：
# @app.get("users/async/")
#
# ===== 修正后：路径以 "/" 开头；函数名 get_user_info_async 不与他人重名，保留 =====
@app.get('/users/async')
async def get_user_info_async(token:str = Depends(get_user_async)):
    return {'token': token}
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
