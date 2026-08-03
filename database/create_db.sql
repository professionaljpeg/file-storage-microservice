DROP TABLE IF EXISTS api_keys;
CREATE TABLE api_keys (
    keyID varchar(255) UNIQUE NOT NULL,
    username varchar(255) UNIQUE NOT NULL,
    secretHash varchar(255) UNIQUE NOT NULL,
    PRIMARY KEY (keyID)
);