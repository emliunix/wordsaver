-- coding: UTF-8

CREATE TABLE metadata (key VARCHAR(50) PRIMARY KEY, value VARCHAR(50));
INSERT INTO metadata (key, value) VALUES
    ('version', '0.1'),
    ('author', 'Liu Yuhui'),
    ('description', 'An app to keep a personal dictionary. OoQ');

CREATE TABLE word (
    wid SERIAL PRIMARY KEY, 
    word VARCHAR(80) UNIQUE NOT NULL, 
    pronounce_eng VARCHAR(300), 
    pronounce_us VARCHAR(300)
);
CREATE TABLE word_definition (
    wid INTEGER REFERENCES word (wid) ON DELETE CASCADE,
    type VARCHAR(20), 
    definition VARCHAR(200)
);
CREATE TABLE word_variants(
    wid INTEGER REFERENCES word (wid) ON DELETE CASCADE,
    kind VARCHAR(50) NOT NULL, 
    word VARCHAR(80) NOT NULL
);
