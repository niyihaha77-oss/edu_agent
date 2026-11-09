create table interview_profile(
    id uuid primary key default uuid_generate_v4(),
    name varchar(30) not null ,
    profile jsonb
);
insert into interview_profile (name,profile)
values ('张三','{"age":30,"city":"北京"}');


select name from interview_profile where name = '张三';

select name,interview_profile.profile ->> 'age' as age from
interview_profile where name = '张三';

select name,profile from interview_profile;

select profile ->> 'city' as 城市 from interview_profile;
