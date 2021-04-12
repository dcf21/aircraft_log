CREATE TABLE squitters
(
    message_type        VARCHAR(3),
    transmission_type   TINYINT,
    session_id          MEDIUMINT,
    aircraft_id         MEDIUMINT,
    hex_ident           VARCHAR(6),
    flight_id           MEDIUMINT,
    generated_timestamp REAL,
    logged_timestamp    REAL,
    callsign            VARCHAR(8),
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

    INDEX(generated_timestamp),
    INDEX(logged_timestamp),
    INDEX(parsed_timestamp),
    INDEX(hex_ident, callsign, generated_timestamp),
    INDEX(hex_ident, callsign, logged_timestamp),
    INDEX(hex_ident, callsign, parsed_timestamp)

);
