# Image display formats
CREATE TABLE adsb_img_formats
(
    uid    INTEGER PRIMARY KEY AUTO_INCREMENT,
    name   TEXT     NOT NULL,
    width  SMALLINT NOT NULL,
    height SMALLINT NOT NULL
);

# Create table of constants
CREATE TABLE adsb_constants
(
    uid   INTEGER PRIMARY KEY AUTO_INCREMENT,
    name  VARCHAR(32) UNIQUE NOT NULL,
    value TEXT
);

# Aircraft squitters
CREATE TABLE adsb_squitters
(
    message_type        VARCHAR(3),
    transmission_type   TINYINT,
    session_id          MEDIUMINT,
    aircraft_id         MEDIUMINT,
    hex_ident           VARCHAR(6),
    flight_id           MEDIUMINT,
    generated_timestamp REAL,
    logged_timestamp    REAL,
    call_sign           VARCHAR(8),
    altitude            INT,
    ground_speed        INT,
    track               INT,
    lat                 REAL,
    lon                 REAL,
    vertical_rate       REAL,
    squawk              MEDIUMINT,
    alert               TINYINT,
    emergency           TINYINT,
    spi                 TINYINT,
    is_on_ground        TINYINT,
    parsed_timestamp    REAL,

    INDEX (generated_timestamp),
    INDEX (logged_timestamp),
    INDEX (parsed_timestamp),
    INDEX (hex_ident, call_sign, generated_timestamp),
    INDEX (hex_ident, call_sign, logged_timestamp),
    INDEX (hex_ident, call_sign, parsed_timestamp)
);
