create database test;
CREATE TABLE IF NOT EXISTS student(
                                      id serial PRIMARY KEY,
                                      name varchar(100),
                                      age int
);
INSERT INTO student(name, age) values ('帅军',20),('老高',18);
SELECT * FROM student;

update student set age = 23 where name = '帅军';

delete from student where name = '帅军';

