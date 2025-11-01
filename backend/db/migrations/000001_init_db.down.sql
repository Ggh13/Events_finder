UPDATE schema_migrations SET dirty = false;
DROP TABLE IF EXISTS schema_migrations;
-- +goose Down
DROP SCHEMA IF EXISTS mig CASCADE;