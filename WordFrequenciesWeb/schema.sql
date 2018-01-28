drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  'date' text not null,
  'text' text not null
);