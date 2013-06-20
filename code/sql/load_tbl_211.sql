-- This runs a set of scripts to load a database table
--
--
-- Version March2008    Created by Tony Teculescu    on 04/03/2008    
--

alter table tls211_pat_publn disable keys;
load data local infile '/mnt/db_master/patstat_raw/dvd1/tls211_part01.txt' into table tls211_pat_publn fields terminated by ',' optionally enclosed by '"' lines terminated by '\r\n' ignore 1 lines;
SHOW WARNINGS;
load data local infile '/mnt/db_master/patstat_raw/dvd1/tls211_part02.txt' into table tls211_pat_publn fields terminated by ',' optionally enclosed by '"' lines terminated by '\r\n' ignore 1 lines;
SHOW WARNINGS;
load data local infile '/mnt/db_master/patstat_raw/dvd1/tls211_part03.txt' into table tls211_pat_publn fields terminated by ',' optionally enclosed by '"' lines terminated by '\r\n' ignore 1 lines;
SHOW WARNINGS;
alter table tls211_pat_publn enable keys;
