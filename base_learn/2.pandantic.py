from pydantic import BaseModel


class Student(BaseModel):
    name:str
    age:int
    sex:str
    pass
s1 = Student(name = 'tp',age=20,sex = '男')
print(s1)
