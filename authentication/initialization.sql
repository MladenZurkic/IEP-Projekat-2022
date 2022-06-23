
INSERT INTO roles (id, name) VALUES
(1,	'kupac'),
(2,	'magacioner'),
(3,	'admin');

INSERT INTO users (id, email, password, forename, surname) VALUES
(1,	'admin@admin.com',	'1',	'admin',	'admin');


INSERT INTO userrole (id, userId, roleId) VALUES (1,	1,	3);