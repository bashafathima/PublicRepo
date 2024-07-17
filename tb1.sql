DROP TABLE IF EXISTS bus_routes;
create table bus_routes(
	id integer not null generated always as identity(increment by 1),
	constraint pk_bus_route primary key(id),
	route_name text,
	route_link text,
	busname text,
	bustype text,
	departing_time timestamp default NULL,
	duration text,
	reaching_time timestamp default NULL,
	star_rating float,
	price decimal,
	seats_available int
);
create table dept_time(
	id integer not null generated always as identity(increment by 1),
	TimeName varchar(50),
	Timeformat varchar(30)
);
create table Arrival_time(
	id integer not null generated always as identity(increment by 1),
	TimeName varchar(50),
	Timeformat varchar(30)
);
create table bus_type(
	id integer not null generated always as identity(increment by 1),
	bus_type varchar(100)
);
create table Routes(
	id integer not null generated always as identity(increment by 1),
	state_name varchar(50)
	Route_Name varchar(100),
	Route_Link text
);