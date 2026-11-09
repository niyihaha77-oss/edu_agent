create table user_xx
(
    id uuid primary key default uuid_generate_v4(),
    name varchar(30) not null ,
    age int default 0,
    email varchar(20),
    role varchar(20) not null check ( role in ('admin', 'user') )
);

insert into user_xx (name, age, email, role) values
('张三', 20, 'zhangsan@example.com', 'admin'),
('李四', 21, 'lisi@example.com', 'users');