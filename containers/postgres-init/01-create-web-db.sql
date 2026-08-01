-- Create the aegiscore_web database used by the Web dashboard.
--
-- Postgres auto-runs files in /docker-entrypoint-initdb.d/ on first startup
-- (only when data volume is empty). This ensures aegiscore_web exists
-- alongside the litellm database created by POSTGRES_DB.
--
-- To apply to an existing deployment without data loss, create the DB
-- manually: `docker exec aegiscore-postgres psql -U aegiscore -c "CREATE DATABASE aegiscore_web;"`

CREATE DATABASE aegiscore_web;
GRANT ALL PRIVILEGES ON DATABASE aegiscore_web TO aegiscore;
