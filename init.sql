create database nogimono;

use nogimono;

create table user(
id int(8) zerofill not null auto_increment,
email varchar(50) not null,
phone varchar(20) not null,
password varchar(40) not null,
token varchar(100) not null,
nickname varchar(40) not null,
introduction varchar(400) not null,
status tinyint(1) not null,
primary key(id)
-- unique(phone),
-- unique(email),
-- unique(nickname)
);

create table feed(
id int(8) zerofill not null auto_increment,
uid int(8) zerofill not null,
post datetime not null,
type tinyint(2) not null,
title varchar(500) not null,
subtitle varchar(500) not null,
snippet varchar(250) not null,
images varchar(800) not null,
referer varchar(250) not null,
cdn tinyint(1) not null,
status tinyint(1) not null,
index(post),
primary key(id),
foreign key(uid) references user(id) on delete cascade on update cascade
);

create table article(
id int(8) zerofill not null,
text mediumtext,
raw mediumtext,
primary key(id),
foreign key(id) references feed(id) on delete cascade
);

alter table article modify column id int(8) zerofill not null;
alter table article add constraint sync foreign key article(id) references feed(id) on delete cascade;
select * from INFORMATION_SCHEMA.TABLES where TABLE_SCHEMA = 'nogimono' order by create_time desc;

-- create table photo(
-- name varchar(32) not null,
-- fid int(8) zerofill not null,
-- type varchar(4) not null,
-- status tinyint(1) not null,
-- primary key(name,fid),
-- foreign key(fid) references feed(id) on delete cascade
-- );

create table tag(
fid int(8) zerofill not null,
name varchar(40) not null,
primary key(fid,name),
foreign key(fid) references feed(id) on delete cascade
);

create table captcha(
phone varchar(20) not null,
random varchar(6) not null,
expiration varchar(10) not null,
primary key(phone),
foreign key(phone) references user(phone) on delete cascade
);

create table commentx(
cid int(8) zerofill auto_increment,
uid int(8) zerofill not null,
fid int(8) zerofill not null,
rid int(8) zerofill not null,
root int(8) zerofill not null,
floor int(4) not null,
post datetime not null, 
message varchar(200) not null,
unread tinyint(1) not null,
status tinyint(1) not null,
index(post),
primary key(cid),
foreign key(uid) references user(id) on delete cascade,
foreign key(fid) references feed(id) on delete cascade
);

-- create table reply(
-- rid int(8) zerofill not null,
-- cid int(8) zerofill not null,
-- unread tinyint(1) not null,
-- primary key(rid),
-- foreign key(rid) references comment(cid) on delete cascade, 
-- foreign key(cid) references comment(cid) on delete cascade
-- );


create table member(
id int(4) zerofill not null,
name varchar(15) not null,
romaji varchar(25) not null,
furigana varchar(20) not null,
birthdate varchar(20) not null,
bloodtype varchar(8) not null,
constellation varchar(8) not null,
height varchar(8) not null,
status varchar(50) not null,
portrait varchar(200) not null,
link varchar(200) not null, 
primary key(id)
);


create table blog(
id int(6) zerofill not null,
mid int(4) zerofill not null,
title varchar(500) not null,
snippet varchar(200) not null,
link varchar(200) not null,
primary key(id),
foreign key(mid) references member(id)
);