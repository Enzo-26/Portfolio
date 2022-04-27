-- SQLite
CREATE table if not exists movies (
id int NOT NULL,
Title varchar(255) NOT NULL,
Description TEXT,
PRIMARY KEY (id)
);


CREATE table if not exists auditorium (
id smallint not null,
capacity int not null,
PRIMARY KEY (id)
);

CREATE table if not exists customers (
email varchar(255) NOT NULL,
first_name varchar(255) NOT NULL,
last_name varchar(255) NOT NULL,
phone varchar(30),
PRIMARY KEY (email)
);


create table if not exists orders (
email varchar(255) NOT NULL,
viewing_id int unsigned NOT NULL,
tickets int not null,
PRIMARY KEY (email),
FOREIGN KEY (viewing_id) REFERENCES viewing(id),
FOREIGN KEY (email) REFERENCES customers (email)
);

create table if not exists viewing (
id int NOT NULL,
movie_id int NOT NULL,
audit_id int NOT NULL,
date_time DATETIME NOT NULL,
PRIMARY KEY (id),
FOREIGN KEY (movie_id) REFERENCES movies(id),
FOREIGN KEY (audit_id) REFERENCES auditorium (id)
);

create table if not exists tickets (
viewing_id int not null,
price decimal(10, 2) NOT NULL,
PRIMARY KEY (viewing_id),
FOREIGN KEY (viewing_id) REFERENCES viewing (id)
);


INSERT INTO auditorium values (1, 100), (2,120);

insert into movies values (1, 'Tenet', 
'This is a science fiction-action-thriller film starring John David Washington, Robert Pattinson, Elizabeth Debicki, and Kenneth Branagh, among others. Its the story of a secret agent who learns to manipulate the flow of time to prevent an attack from the future that threatens to annihilate the present');

insert into movies values (2, 'The Great Gatsby',
'The Great Gatsby, third novel by F. Scott Fitzgerald, published in 1925 by Charles Scribners Sons. Set in Jazz Age New York, the novel tells the tragic story of Jay Gatsby, a self-made millionaire, and his pursuit of Daisy Buchanan, a wealthy young woman whom he loved in his youth.');

insert into movies values (3, 'Sherlock',
'Detective Sherlock Holmes and his stalwart partner Watson engage in a battle of wits and brawn with a nemesis whose plot is a threat to all of England. Detective Sherlock Holmes and his stalwart partner Watson engage in a battle of wits and brawn with a nemesis whose plot is a threat to all of England.');

insert into customers values ('user1@gmail.com', 'John', 'Smiith', '+4700000000');
insert into customers values ('user2@gmail.com', 'Adam', 'Clark', '+4712345678');
insert into customers values ('user3@gmail.com', 'Julia', 'Red', '+4711223344');

insert into viewing values (1, 1, 1, '2022-04-20 12:30:00 PM');
insert into viewing values (2, 2, 2, '2022-04-20 02:30:00 PM');
insert into viewing values (3, 3, 1, '2022-04-20 05:30:00 PM');
insert into viewing values (4, 2, 2, '2022-04-20 07:30:00 PM');
insert into viewing values (5, 2, 1, '2022-04-20 10:30:00 PM');

insert into tickets values (1, 15), (2, 20), (3,15), (4,20), (5,15);
