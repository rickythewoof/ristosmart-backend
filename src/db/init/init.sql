-- Initial DB setup run by Postgres container on first start
-- NOTE: when using POSTGRES_USER and POSTGRES_DB env vars the DB and user
-- will already be created. This script is safe but may fail if objects exist.

DO
$$
BEGIN
   -- create role if not exists
   IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'risto_user') THEN
       CREATE ROLE risto_user WITH LOGIN PASSWORD 'risto_pass';
   END IF;
EXCEPTION WHEN others THEN
   -- ignore
END
$$;

-- create database if not exists
SELECT 'CREATE DATABASE ristosmart'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ristosmart')
\gexec

GRANT ALL PRIVILEGES ON DATABASE ristosmart TO risto_user;
