#!../../auto/virtualenv/bin/python3
# encoding: utf-8
# receiver.py

"""
Receive squitter messages, and store them in a MySQL database.
"""

import socket
import logging
import argparse
import traceback
import MySQLdb
import time

from adsb_helpers.connect_db import connect_db
from adsb_helpers import dcf_ast
from location_filter import LocationFilter_Cambridge

# Defaults
HOST = "localhost"  # Hostname of dump1090 server
PORT = 30003  # Port that dump1090 is running on
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
            logging.info("Connected to dump1090 broadcast")
            break
        except socket.error:
            count_failed_connection_attempts += 1
            logging.info(
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
                         connect_attempt_limit: int = 10, connect_attempt_delay: float = 5.0):
    """
    Listen for squitters, and store them in the database.

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
    # Count how many squitter we have processed
    count_total = 0
    count_committed = 0
    last_report_time = time.time()
    total_at_last_report = 0
    committed_at_last_report = 0
    report_interval = 30

    # Connect to database
    [db, c] = connect_db()

    # Connect to dump1090 output stream
    input_socket = open_socket(host=host, port=port,
                               connect_attempt_limit=connect_attempt_limit,
                               connect_attempt_delay=connect_attempt_delay)

    # Instantiate location filter
    location_filter = LocationFilter_Cambridge()

    # Cached values by hex_ident
    value_cache = {}
    value_cache_grace_period = 600

    try:
        # Loop until an exception
        while True:
            # Consider producing a report message
            if last_report_time < time.time() - report_interval:
                message_rate_total = (count_total - total_at_last_report) / (time.time() - last_report_time)
                message_rate_committed = (count_committed - committed_at_last_report) / (time.time() - last_report_time)
                logging.info(
                    "Message rate per second: {:5.2f} {:5.2f}".format(message_rate_total, message_rate_committed))
                last_report_time = time.time()
                total_at_last_report = count_total
                committed_at_last_report = count_committed

                # Touch database connection to prevent timeout
                c.execute("SELECT 1 FROM adsb_squitters LIMIT 1;");
                results = c.fetchall()

            # Receive a single line from the input stream
            message_bytes = bytearray()
            try:
                while not message_bytes.decode('utf-8').endswith('\n'):
                    message_bytes += input_socket.recv(1)
            except socket.error:
                # This happens if there is no connection and is dealt with below
                pass

            # If we didn't get a stream message, reconnect
            squitter = message_bytes.decode('utf-8').strip()
            if len(squitter) == 0:
                logging.info("No broadcast received. Attempting to reconnect")
                time.sleep(connect_attempt_delay)
                input_socket.close()
                input_socket = open_socket(host=host, port=port,
                                           connect_attempt_limit=connect_attempt_limit,
                                           connect_attempt_delay=connect_attempt_delay)
                continue

            # Break squitter up into comma-separated components
            columns = squitter.strip().split(",")

            # If the line has 22 items, it's valid
            if len(columns) != 22:
                logging.warning("Received illegal squitter with only {:d} columns.".format(len(columns)))
                logging.warning("Input line was: <{}>".format(squitter))

            # Extract components of the line
            current_values = {}
            try:
                current_values['message_type'] = columns[0].strip()
                current_values['transmission_type'] = columns[1].strip()
                current_values['hex_ident'] = columns[4].strip()
                current_values['generated_date'] = columns[6].strip()
                current_values['generated_time'] = columns[7].strip()
                current_values['logged_date'] = columns[8].strip()
                current_values['logged_time'] = columns[9].strip()

                # See if we have cached values for this hex_ident
                old_values = {}
                cache_timeout = time.time() - value_cache_grace_period
                if current_values['hex_ident'] in value_cache:
                    if value_cache[current_values['hex_ident']]['time'] > cache_timeout:
                        old_values = value_cache[current_values['hex_ident']]['cached']

                if columns[2].strip():
                    current_values['session_id'] = int(columns[2])
                else:
                    current_values['session_id'] = old_values.get('session_id', None)

                if columns[3].strip():
                    current_values['aircraft_id'] = int(columns[3])
                else:
                    current_values['aircraft_id'] = old_values.get('aircraft_id', None)

                if columns[5].strip():
                    current_values['flight_id'] = int(columns[5])
                else:
                    current_values['flight_id'] = old_values.get('flight_id', None)

                if columns[10].strip():
                    current_values['call_sign'] = columns[10].strip()
                else:
                    current_values['call_sign'] = old_values.get('call_sign', None)

                if columns[11].strip():
                    current_values['altitude'] = int(columns[11])
                else:
                    current_values['altitude'] = old_values.get('altitude', None)

                if columns[12].strip():
                    current_values['ground_speed'] = int(columns[12])
                else:
                    current_values['ground_speed'] = old_values.get('ground_speed', None)

                if columns[13].strip():
                    current_values['track'] = int(columns[13])
                else:
                    current_values['track'] = old_values.get('track', None)

                if columns[14].strip():
                    current_values['lat'] = float(columns[14])
                else:
                    current_values['lat'] = old_values.get('lat', None)

                if columns[15].strip():
                    current_values['lon'] = float(columns[15])
                else:
                    current_values['lon'] = old_values.get('lon', None)

                if columns[16].strip():
                    current_values['vertical_rate'] = float(columns[16])
                else:
                    current_values['vertical_rate'] = old_values.get('vertical_rate', None)

                if columns[17].strip():
                    current_values['squawk'] = int(columns[17])
                else:
                    current_values['squawk'] = old_values.get('squawk', None)

                if columns[18].strip():
                    current_values['alert'] = int(columns[18])
                else:
                    current_values['alert'] = old_values.get('alert', None)

                if columns[19].strip():
                    current_values['emergency'] = int(columns[19])
                else:
                    current_values['emergency'] = old_values.get('emergency', None)

                if columns[20].strip():
                    current_values['spi'] = int(columns[20])
                else:
                    current_values['spi'] = old_values.get('spi', None)

                if columns[21].strip():
                    current_values['is_on_ground'] = int(columns[21])
                else:
                    current_values['is_on_ground'] = old_values.get('is_on_ground', None)
            except ValueError:
                logging.warning("Error parsing line <{}>".format(squitter.strip()))
                continue

            # Update database of cache values
            value_cache[current_values['hex_ident']] = {
                'cached': current_values,
                'time': time.time()
            }

            # Reject illegal message type
            if current_values['message_type'] != "MSG":
                logging.warning("Received illegal message type <{}>".format(current_values['message_type']))
                logging.warning("Input line was: {}".format(squitter))
                continue

            # Count messages parsed
            count_total += 1

            # Only proceed with messages if latitude and longitude were updated
            if len(columns[14].strip()) == 0:
                continue

            # Only proceed if call sign is known
            if current_values['call_sign'] is None:
                continue

            # Get current time
            parsed_timestamp = time.time()

            # check if aircraft is within search region
            aircraft_id_str = "{}/{}".format(current_values['call_sign'], current_values['hex_ident'])
            if not location_filter.is_in_range(id=aircraft_id_str,
                                               lat=current_values['lat'],
                                               lon=current_values['lon']):
                continue

            # Extract timestamps from strings
            generated_timestamp = parse_date_time(date_str=current_values['generated_date'],
                                                  time_str=current_values['generated_time'])
            logged_timestamp = parse_date_time(date_str=current_values['logged_date'],
                                               time_str=current_values['logged_time'])

            # Check entry is ok
            is_ok = generated_timestamp is not None and logged_timestamp is not None
            if not is_ok:
                logging.warning("Error parsing dates in line <{}>".format(squitter))
                continue

            # Add the row to the db
            mysql_fields = (current_values['message_type'], current_values['transmission_type'],
                            current_values['session_id'], current_values['aircraft_id'],
                            current_values['hex_ident'], current_values['flight_id'],
                            generated_timestamp, logged_timestamp,
                            current_values['call_sign'], current_values['altitude'],
                            current_values['ground_speed'], current_values['track'],
                            current_values['lat'], current_values['lon'], current_values['vertical_rate'],
                            current_values['squawk'], current_values['alert'], current_values['emergency'],
                            current_values['spi'],
                            current_values['is_on_ground'], parsed_timestamp)

            try:
                c.execute("""
INSERT INTO adsb_squitters
(message_type, transmission_type, session_id, aircraft_id, hex_ident, flight_id,
generated_timestamp, logged_timestamp, call_sign, altitude,
ground_speed, track, lat, lon, vertical_rate, squawk, alert, emergency, spi, is_on_ground, parsed_timestamp
) VALUES (%s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""", mysql_fields)

                # Commit the new row to the database
                db.commit()
            except MySQLdb.DataError:
                logging.warning("Error inserting row: {}".format(str(mysql_fields)))
                logging.warning("Input line was: {}".format(squitter))
                logging.warning("Error message was: {}".format(str(traceback.format_exc())))

            # Increment squitter count
            count_committed += 1

    except KeyboardInterrupt:
        # Clean up neatly on keyboard interrupt
        logging.info("Closing connection")
        input_socket.close()
        db.commit()
        db.close()
        logging.info("{:d} squitters parsed".format(count_total))
        logging.info("{:d} squitters added to your database".format(count_committed))


def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S',
                        handlers=[
                            logging.FileHandler("receiver.log"),
                            logging.StreamHandler()
                        ])
    logger = logging.getLogger(__name__)
    logger.info(__doc__.strip())

    # Set up command line options
    parser = argparse.ArgumentParser(description="Process dump1090 messages then insert them into a database")
    parser.add_argument(
        "--host", type=str, default=HOST,
        help="This is the network location of your dump1090 broadcast. Defaults to {}".format(HOST))
    parser.add_argument(
        "--port", type=int, default=PORT,
        help="The port broadcasting in SBS-1 BaseStation format. Defaults to {}".format(PORT))
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
