-- Replace 'radius_user_password' with a secure password.

-- 1. Create the database
CREATE DATABASE radius
  WITH OWNER = postgres
       ENCODING = 'UTF8'
       CONNECTION LIMIT = -1;

-- 2. Connect to the radius database
\c radius;

-- 3. Create a dedicated database user for FreeRADIUS
CREATE USER radius WITH PASSWORD 'radius_user_password';

-- 4. Grant basic privileges to the radius user
GRANT CONNECT ON DATABASE radius TO radius;

-- 5. Create the schema and tables
--    Grant the necessary privileges to the radius user

-- Create the radcheck table
CREATE TABLE radcheck (
  id SERIAL PRIMARY KEY,
  username VARCHAR(64) NOT NULL,
  attribute VARCHAR(64) NOT NULL,
  op CHAR(2) DEFAULT '==',
  value VARCHAR(253) NOT NULL
);
GRANT SELECT, INSERT, UPDATE, DELETE ON radcheck TO radius;

-- Create the radreply table
CREATE TABLE radreply (
  id SERIAL PRIMARY KEY,
  username VARCHAR(64) NOT NULL,
  attribute VARCHAR(64) NOT NULL,
  op CHAR(2) DEFAULT '=',
  value VARCHAR(253) NOT NULL
);
GRANT SELECT, INSERT, UPDATE, DELETE ON radreply TO radius;

-- Create the radgroupcheck table
CREATE TABLE radgroupcheck (
  id SERIAL PRIMARY KEY,
  groupname VARCHAR(64) NOT NULL,
  attribute VARCHAR(64) NOT NULL,
  op CHAR(2) DEFAULT '==',
  value VARCHAR(253) NOT NULL
);
GRANT SELECT, INSERT, UPDATE, DELETE ON radgroupcheck TO radius;

-- Create the radgroupreply table
CREATE TABLE radgroupreply (
  id SERIAL PRIMARY KEY,
  groupname VARCHAR(64) NOT NULL,
  attribute VARCHAR(64) NOT NULL,
  op CHAR(2) DEFAULT '=',
  value VARCHAR(253) NOT NULL
);
GRANT SELECT, INSERT, UPDATE, DELETE ON radgroupreply TO radius;

-- Create the usergroup table
CREATE TABLE usergroup (
  username VARCHAR(64) NOT NULL,
  groupname VARCHAR(64) NOT NULL,
  priority INT DEFAULT 1,
  PRIMARY KEY (username, groupname)
);
GRANT SELECT, INSERT, UPDATE, DELETE ON usergroup TO radius;

-- Create the radacct table
CREATE TABLE radacct (
  radacctid BIGSERIAL PRIMARY KEY,
  acctsessionid VARCHAR(64) NOT NULL,
  acctuniqueid VARCHAR(32) NOT NULL UNIQUE,
  username VARCHAR(64),
  groupname VARCHAR(64),
  realm VARCHAR(64),
  nasipaddress INET NOT NULL,
  nasportid VARCHAR(15),
  nasporttype VARCHAR(32),
  acctstarttime TIMESTAMP WITHOUT TIME ZONE,
  acctstoptime TIMESTAMP WITHOUT TIME ZONE,
  acctsessiontime BIGINT,
  acctauthentic VARCHAR(32),
  connectinfo_start VARCHAR(50),
  connectinfo_stop VARCHAR(50),
  acctinputoctets BIGINT,
  acctoutputoctets BIGINT,
  calledstationid VARCHAR(50),
  callingstationid VARCHAR(50),
  acctterminatecause VARCHAR(32),
  servicetype VARCHAR(32),
  framedprotocol VARCHAR(32),
  framedipaddress INET,
  acctstartdelay BIGINT,
  acctstopdelay BIGINT,
  xascendsessionsvrkey VARCHAR(10)
);
GRANT SELECT, INSERT, UPDATE, DELETE ON radacct TO radius;

-- Create the radpostauth table
CREATE TABLE radpostauth (
  id BIGSERIAL PRIMARY KEY,
  username VARCHAR(64),
  pass VARCHAR(64),
  reply VARCHAR(32),
  authdate TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);
GRANT SELECT, INSERT, UPDATE, DELETE ON radpostauth TO radius;

-- Create the nas table
CREATE TABLE nas (
  id SERIAL PRIMARY KEY,
  nasname VARCHAR(128) NOT NULL,
  shortname VARCHAR(32),
  type VARCHAR(30) DEFAULT 'other',
  ports INT,
  secret VARCHAR(60) NOT NULL,
  server VARCHAR(64),
  community VARCHAR(50),
  description VARCHAR(200)
);
GRANT SELECT, INSERT, UPDATE, DELETE ON nas TO radius;

-- 6. Grant schema-wide privileges
GRANT USAGE ON SCHEMA public TO radius;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO radius;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO radius;

-- 7. Set default privileges for the radius user (future-proofing)
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO radius;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT USAGE, SELECT ON SEQUENCES TO radius;