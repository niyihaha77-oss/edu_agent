create table user_info(
                          id uuid primary key default uuid_generate_v4(),
                          name varchar(30) not null ,
                          age int default 0,
                          email varchar(20),
                          phone varchar(11) unique
);

insert into user_info (name, age, email, phone) values
    ('王5', 21, 'zhangsan@example.com', '12345678901')
on conflict (phone) do update set
                                  name = excluded.name,
                                  age = excluded.age
;

select * from user_info;
