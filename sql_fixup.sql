-- This file holds needed corrections to the database until they have been applied to
-- the live database.  This file is applied after importing a new dump of the live DB.

-- To add primary key into id_submission_env table
alter table id_submission_env add id int(1) primary key auto_increment first;
