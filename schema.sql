drop table if exists humidity;
create table humidity (
	-- id integer primary key autoincrement,
	'time' integer not null,
	humidity integer not null
);

drop table if exists temperature;
create table temperature (
	-- id integer primary key autoincrement,
	'time' integer not null,
	temperature integer not null
);
