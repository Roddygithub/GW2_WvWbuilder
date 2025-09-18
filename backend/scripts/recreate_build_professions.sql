-- Supprimer la table existante
DROP TABLE IF EXISTS build_professions;

-- Recréer la table avec une configuration plus simple
CREATE TABLE build_professions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    build_id INTEGER NOT NULL,
    profession_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (build_id) REFERENCES builds (id) ON DELETE CASCADE,
    FOREIGN KEY (profession_id) REFERENCES professions (id) ON DELETE CASCADE,
    UNIQUE (build_id, profession_id)
);

-- Recréer les index
CREATE INDEX idx_build_professions_build ON build_professions (build_id);
CREATE INDEX idx_build_professions_profession ON build_professions (profession_id);
