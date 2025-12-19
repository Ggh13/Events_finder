create schema if not exists events_finder;

create type user_role as enum('P', 'A', 'O', 'D');
--P - participant
--A - admin
--O - organiser
--D - distributor

create table if not exists events_finder.photo(
	id serial primary key,
	url text not null default ''
);

create table if not exists events_finder.telegram_info (
	id serial primary key,
	telegram_id bigint unique not null,
	username text unique not null,
	chat_id bigint unique not null
);


create table if not exists events_finder.user (
  id serial primary key,
  telegram_id int references events_finder.telegram_info(id),
  first_name text not null,
  last_name text not null,
  photo_id int not null,
  balance int not null,
  role user_role not null default 'P',
  longitude decimal(8, 6) not null,
  latitude decimal(9, 6) not null
);

create table if not exists events_finder.team (
  id serial primary key,
  name text not null
);


create table if not exists events_finder.user_team (
  user_id int, 
  team_id int,
  primary key(user_id, team_id),
  constraint fk_team foreign key(team_id) references events_finder.team(id),
  constraint fk_user foreign key(user_id) references events_finder.user(id)
);

create table if not exists events_finder.category (
  id serial primary key,
  name text not null
);

create table if not exists events_finder.event (
  id serial primary key,
  name text not null,
  description text not null,
  date timestamp not null,
  address text not null,
  longitude decimal(8, 6) not null,
  latitude decimal(9, 6) not null,
  age_restriction int not null,
  chat_link text not null,
  organiser_id int references events_finder.user,
  max_participants int not null,
  cost int not null,
  balance int not null,
  is_freezed boolean not null default false
);


create table if not exists events_finder.event_photo (
	event_id int,
	photo_id int,
	primary key(event_id, photo_id),
	constraint fk_event foreign key(event_id) references events_finder.event(id),
  constraint fk_photo foreign key(photo_id) references events_finder.photo(id)
)


create table if not exists events_finder.event_category (
  event_id int,
  category_id int,
  primary key(event_id, category_id),
  constraint fk_event foreign key(event_id) references events_finder.event(id),
  constraint fk_category foreign key(category_id) references events_finder.category(id)
);


create table if not exists events_finder.user_category(
  user_id int, 
  category_id int,
  primary key(user_id, category_id),
  constraint fk_category foreign key(category_id) references events_finder.category(id),
  constraint fk_user foreign key(user_id) references events_finder.user(id)
);

create type ticket_status as enum('P', 'A', 'D');

-- P - pending (юзер подал заявку на участие у мероприятии)
-- A - accepted (юзер пришел на мероприятие и отметил своё присутсвие)
-- D - deleted (юзер отказался от участия в мероприятии)

create table if not exists events_finder.ticket(
  id uuid primary key,
  user_id int references events_finder.user(id),
  event_id int references events_finder.event(id),
  unique (user_id, event_id),
  status ticket_status not null default 'P',
  created_at timestamp not null default CURRENT_TIMESTAMP,
  updated_at timestamp not null default CURRENT_TIMESTAMP
);


create table if not exists events_finder.user_ban(
  user_id int, 
  user_ban_id int,
  primary key(user_id, user_ban_id),
  constraint fk_user_ban foreign key(user_ban_id) references events_finder.user(id),
  constraint fk_user foreign key(user_id) references events_finder.user(id)
);


create table if not exists events_finder.user_report(
  id uuid primary key,
  sender_id int references events_finder.user(id),
  message text not null,
  reported_user_id int references events_finder.user(id)
);


create table if not exists events_finder.event_report(
  id uuid primary key,
  sender_id int references events_finder.user(id),
  message text not null,
  reported_event_id int references events_finder.event(id)
);

ALTER TABLE events_finder."user"
  DROP CONSTRAINT IF EXISTS user_photo_id_fkey;

-- если фото не обязательно
ALTER TABLE events_finder."user"
  ALTER COLUMN photo_id DROP NOT NULL;