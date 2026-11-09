CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

create table if not exists teacher(
                                      id uuid primary key default uuid_generate_v4(),
                                      teacher_name varchar(20) not null ,
                                      experience int default 0
);
insert into teacher(teacher_name, experience) values
                                                  ('老高', 15),('老黎',20) ;
insert into teacher(teacher_name, experience) values
                                                  ('老周', 15) returning id;
select * from teacher;