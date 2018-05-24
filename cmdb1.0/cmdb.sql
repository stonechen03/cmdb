create table if not exists user (
    id int primary key auto_increment,
    name varchar(32) not null default '',
    age int,
    telephone varchar(32),
    password varchar(32),
    sex int,
    department varchar(64),
    title varchar(64),
    role varchar(64),
    birthday date,
    job_join timestamp
)engine=innodb default charset=utf8;

insert into user (id, name, password) values(1, 'admin', md5('admin'));

create table if not exists `machine_room` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `addr` varchar(128) DEFAULT NULL,
  `ip_ranges` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

create table if not exists asset (
    id int primary key auto_increment,
    sn varchar(125) not null unique key comment '资产标号',
    hostname varchar(64) comment '主机名',
    os varchar(64) comment '操作系统',
    ip varchar(256) comment 'ip地址',
    machine_room_id int comment '机房ID',

    vendor varchar(256) comment '生产厂商',
    model varchar(64) comment '型号',
    
    ram int comment '内存, 单位G',
    cpu int comment 'cpu核数',
    disk int comment '硬盘，单位G',

    time_on_shelves date comment '上架时间',
    over_guaranteed_date date comment '过保时间',
    buiness varchar(256) comment '业务',
    admin varchar(256) comment '使用者',
    status int comment '0正在使用, 1 维护, 2 删除'
) engine=innodb default charset=utf8;


create table if not exists monitor_host(
    id int primary key auto_increment,
    ip varchar(128),
    cpu float,
    mem float,
    disk float,
    m_time datetime,
    r_time datetime
)engine=innodb default charset=utf8;

create table if not exists alert(
    id int primary key auto_increment,
    ip varchar(128),
    message text,
    admin varchar(256),
    status int,
    type int,
    c_time datetime
) engine=innodb default charset=utf8;


create table accesslog(
    id int primary key auto_increment,
    a_time datetime,
    ip varchar(128),
    url text,
    code int,
    city_name varchar(64)
) engine=innodb default charset=utf8;

create table geoip (
    id int primary key auto_increment,
    city_name varchar(64),
    city_lat float,
    city_lgt float
) engine=innodb default charset=utf8;