import uuid

from pydantic import BaseModel,Field

class Student(BaseModel):
    name:str = Field(default='',description='学生姓名')
    age:int = Field(default=0,description='学生年龄')
    sex:str = Field(default='',description='学生性别')
    id:str = Field(default_factory=uuid.uuid4,description='学生ID')
    pass
s1 = Student(name = 'tp',age=20,sex = '男')
print(s1)
