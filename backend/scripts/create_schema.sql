-- Drop existing tables if they exist
PRAGMA foreign_keys = OFF;

-- Drop tables in reverse order of dependencies
DROP TABLE IF EXISTS build_professions;
DROP TABLE IF EXISTS builds;
DROP TABLE IF EXISTS user_roles;
DROP TABLE IF EXISTS roles;
DROP TABLE IF EXISTS professions;
DROP TABLE IF EXISTS users;

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT 1,
    is_superuser BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Roles table
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    permission_level INTEGER NOT NULL DEFAULT 0,
    is_default BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- User-Roles association table
CREATE TABLE user_roles (
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE
);

-- Professions table
CREATE TABLE professions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    icon_url VARCHAR(255),
    description TEXT,
    game_modes JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Builds table
CREATE TABLE builds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    game_mode VARCHAR(20) NOT NULL DEFAULT 'wvw',
    team_size INTEGER NOT NULL DEFAULT 5,
    is_public BOOLEAN NOT NULL DEFAULT 0,
    created_by_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    config JSON NOT NULL,
    constraints JSON,
    FOREIGN KEY (created_by_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Build-Professions association table
CREATE TABLE build_professions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    build_id INTEGER NOT NULL,
    profession_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (build_id) REFERENCES builds (id) ON DELETE CASCADE,
    FOREIGN KEY (profession_id) REFERENCES professions (id) ON DELETE CASCADE,
    UNIQUE (build_id, profession_id)
);

-- Create indexes
CREATE INDEX idx_builds_created_by ON builds (created_by_id);
CREATE INDEX idx_build_professions_build ON build_professions (build_id);
CREATE INDEX idx_build_professions_profession ON build_professions (profession_id);

-- Insert initial data
INSERT INTO roles (name, description, permission_level, is_default) VALUES 
('admin', 'Administrator with full access', 100, 0),
('user', 'Regular user', 10, 1);

-- Insert some professions
INSERT INTO professions (name, description) VALUES 
('Warrior', 'A strong melee fighter'),
('Guardian', 'A protective fighter'),
('Revenant', 'Channeler of the Mists'),
('Ranger', 'Beastmaster and archer'),
('Thief', 'Stealthy damage dealer'),
('Engineer', 'Tech-savvy inventor'),
('Necromancer', 'Master of the dark arts'),
('Elementalist', 'Wielder of elemental magic'),
('Mesmer', 'Illusionist and trickster');
