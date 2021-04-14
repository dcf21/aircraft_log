#!../../auto/virtualenv/bin/python3
# encoding: utf-8
# receiver.py

import socket
import logging
import argparse
import sys
import time

from adsb_helpers.connect_db import connect_db
from adsb_helpers import dcf_ast
from location_filter import LocationFilter_Cambridge

# Defaults
HOST = "localhost"  # Hostname of dump1090 server
PORT = 30003  # Port that dump1090 is running on
BUFFER_SIZE = 100  # Size of buffer to store squitter stream data in
CONNECT_ATTEMPT_LIMIT = 10  # Number of times to attempt to reconnect
CONNECT_ATTEMPT_DELAY = 5.0  # Delay between reconnection attempts


def connect_to_socket(host: str = "localhost", port: int = 30003):
    """
    Connect to socket serving dump1090 stream of squitters.

    :param host:
        Hostname of dump1090 server
    :param port:
        Port that dump1090 is running on
    :return:
        Stream connection
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return s


def open_socket(host: str = "localhost", port: int = 30003,
                connect_attempt_limit: int = 10, connect_attempt_delay: float = 5.0):
    """
    Try to open a socket connection, with retries in the event of failure.

    :param host:
        Hostname of dump1090 server
    :param port:
        Port that dump1090 is running on
    :param connect_attempt_limit:
        Number of times to attempt to reconnect
    :param connect_attempt_delay:
        Delay between reconnection attempts
    :return:
        Stream connection
    """
    s = None
    count_failed_connection_attempts = 0
    while count_failed_connection_attempts < connect_attempt_limit:
        try:
            s = connect_to_socket(host, port)
            count_failed_connection_attempts = 0
            print("Connected to dump1090 broadcast")
            break
        except socket.error:
            count_failed_connection_attempts += 1
            print(
                "Cannot connect to dump1090 broadcast. Making attempt"
                + str(count_failed_connection_attempts)
                + "."
            )
            time.sleep(connect_attempt_delay)
    else:
        quit()

    return s


def parse_date_time(date_str, time_str):
    """
    Parse date/time strings in the format "yyyy/mm/dd" and "HH:mm:ss.sss" into a unix timestamp
    :param date_str:
        Date string in the format "yyyy/mm/dd"
    :param time_str:
        Time string in the format "HH:mm:ss.sss"
    :return:
        Unix timestamp
    """
    try:
        year = int(date_str[0:4])
        month = int(date_str[5:7])
        day = int(date_str[8:10])
        hour = int(time_str[0:2])
        minute = int(time_str[3:5])
        seconds = float(time_str[6:])
    except ValueError:
        logging.warning("Could not parse date/time <{}> <{}>".format(date_str, time_str))
        return None

    # Convert date components into a Julian day number
    jd = dcf_ast.julian_day(year=year, month=month, day=day, hour=hour, minute=minute, sec=seconds)

    # Convert to unix timestamp
    utc = dcf_ast.unix_from_jd(jd=jd)
    return utc


def listen_for_squitters(host: str = "localhost", port: int = 30003,
                         buffer_size: int = 100,
                         connect_attempt_limit: int = 10, connect_attempt_delay: float = 5.0):
    """
    Listen for squitters, and store them in the database.

    :param host:
        Hostname of dump1090 server
    :param port:
        Port that dump1090 is running on
    :param buffer_size:
        Size of buffer to store squitter stream data in
    :param connect_attempt_limit:
        Number of times to attempt to reconnect
    :param connect_attempt_delay:
        Delay between reconnection attempts
    :return:
        Stream connection
    """
    # Count how many squitter we have processed
    count_total = 0

    # Connect to database
    [db, c] = connect_db()

    # Connect to dump1090 output stream
    input_socket = open_socket(host=host, port=port,
                               connect_attempt_limit=connect_attempt_limit,
                               connect_attempt_delay=connect_attempt_delay)

    # Instantiate location filter
    location_filter = LocationFilter_Cambridge()

    # Buffer for storing squitter data
    text_buffer = ""

    try:

        # Loop until an exception
        while True:
            # Receive a stream message
            message = ""
            try:
                message = input_socket.recv(buffer_size).decode("utf-8")
                logging.info(message)
                text_buffer += message.strip("\n")
            except socket.error:
                # This happens if there is no connection and is dealt with below
                pass

            # If we didn't get a stream message, reconnect
            if len(message) == 0:
                logging.info("No broadcast received. Attempting to reconnect")
                time.sleep(connect_attempt_delay)
                input_socket.close()
                input_socket = open_socket(host=host, port=port,
                                           connect_attempt_limit=connect_attempt_limit,
                                           connect_attempt_delay=connect_attempt_delay)
                continue

            # It is possible that more than one line has been received,
            # so split it then loop through the parts and validate
            squitters = text_buffer.split("\n")
            text_buffer = ""
            for squitter in squitters:
                columns = squitter.split(",")

                # If the line has 22 items, it's valid
                if len(columns) == 22:
                    # Extract components of the line
                    try:
                        message_type = columns[0]
                        transmission_type = columns[1]
                        session_id = int(columns[2]) if columns[2] else None
                        aircraft_id = int(columns[3]) if columns[3] else None
                        hex_ident = columns[4]
                        flight_id = int(columns[5]) if columns[5] else None
                        generated_date = columns[6]
                        generated_time = columns[7]
                        logged_date = columns[8]
                        logged_time = columns[9]
                        call_sign = columns[10]
                        altitude = int(columns[11]) if columns[11] else None
                        ground_speed = int(columns[12]) if columns[12] else None
                        track = int(columns[13]) if columns[13] else None
                        lat = float(columns[14]) if columns[14] else None
                        lon = float(columns[15]) if columns[15] else None
                        vertical_rate = float(columns[16]) if columns[16] else None
                        squawk = int(columns[17]) if columns[17] else None
                        alert = int(columns[18]) if columns[18] else None
                        emergency = int(columns[19]) if columns[19] else None
                        spi = int(columns[20]) if columns[20] else None
                        is_on_ground = int(columns[21]) if columns[21] else None
                    except ValueError:
                        logging.warning("Error parsing line <{}>".format(squitter))
                        continue

                    # Get current time
                    parse_time = time.time()

                    # check if aircraft is within search region
                    aircraft_id_str = "{}/{}".format(call_sign, hex_ident)
                    if not location_filter.is_in_range(id=aircraft_id_str, lat=lat, lon=lon):
                        continue

                    # Extract timestamps from strings
                    generated_timestamp = parse_date_time(generated_date, generated_time)
                    logged_timestamp = parse_date_time(logged_date, logged_time)

                    # Check entry is ok
                    is_ok = generated_timestamp is not None and logged_timestamp is not None
                    if not is_ok:
                        logging.warning("Error parsing dates in line <{}>".format(squitter))
                        continue

                    # Add the row to the db
                    c.execute("""
INSERT INTO adsb_squitters
 (message_type, transmission_type, session_id, aircraft_id, hex_ident, flight_id,
  generated_timestamp, logged_timestamp, call_sign, altitude,
  ground_speed, track, lat, lon, vertical_rate, squawk, alert, emergency, spi, is_on_ground, parsed_timestamp
 ) VALUES (%s, %s, %s, %s, %s, %s,
           %s, %s, %s, %s,
           %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                              (message_type, transmission_type, session_id, aircraft_id, hex_ident, flight_id,
                               generated_timestamp, logged_timestamp, call_sign, altitude,
                               ground_speed, track, lat, lon, vertical_rate, squawk, alert, emergency, spi,
                               is_on_ground, parse_time)
                              )

                    # Increment squitter count
                    count_total += 1

                    # Commit the new row to the database
                    c.commit()
                else:
                    # The stream message is too short, so prepend it to the next stream message
                    text_buffer = squitter
                    continue

    except KeyboardInterrupt:
        # Clean up neatly on keyboard interrupt
        logging.info("Closing connection")
        input_socket.close()
        c.commit()
        c.close()
        logging.info("{:d} squitters added to your database".format(count_total))


def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO,
                        stream=sys.stdout,
                        format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S')
    logger = logging.getLogger(__name__)
    logger.info(__doc__.strip())

    # Set up command line options
    parser = argparse.ArgumentParser(description="Process dump1090 messages then insert them into a database")
    parser.add_argument(
        "-h", "--host", type=str, default=HOST,
        help="This is the network location of your dump1090 broadcast. Defaults to {}".format(HOST))
    parser.add_argument(
        "-p", "--port", type=int, default=PORT,
        help="The port broadcasting in SBS-1 BaseStation format. Defaults to {}".format(PORT))
    parser.add_argument(
        "--buffer-size", type=int, default=BUFFER_SIZE,
        help="An integer of the number of bytes to read at a time from the stream. Defaults to {}".format(BUFFER_SIZE))
    parser.add_argument(
        "--connect-attempt-limit", type=int, default=CONNECT_ATTEMPT_LIMIT,
        help="An integer limit to the number of times to try to connect to dump1090 before qutting. "
             "Defaults to {}".format(CONNECT_ATTEMPT_LIMIT))
    parser.add_argument(
        "--connect-attempt-delay", type=float, default=CONNECT_ATTEMPT_DELAY,
        help="The number of seconds to wait after a failed connection attempt. "
             "Defaults to {}".format(CONNECT_ATTEMPT_DELAY))

    # Parse command line options
    args = parser.parse_args()

    # Listen for dump1090 output
    listen_for_squitters(host=args.host, port=args.port,
                         connect_attempt_delay=args.connect_attempt_delay,
                         connect_attempt_limit=args.connect_attempt_limit)


# If invoked from the command line, start listening now
if __name__ == "__main__":
    main()
