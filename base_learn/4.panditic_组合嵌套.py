from pydantic import BaseModel, Field


class Edu(BaseModel):
    school:str = Field(description='学校名称')
    major:str = Field(description='专业名称')

class Resume(BaseModel):
    name:str = Field(description='姓名')
    age:int = Field(description='年龄')
    education : list[Edu] = Field(description='教育背景')
