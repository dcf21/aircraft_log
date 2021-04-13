#!../../auto/virtualenv/bin/python3
# encoding: utf-8

import socket
import logging
import argparse
import sys
import time

from adsb_helpers.connect_db import connect_db
from adsb_helpers import dcf_ast

# Defaults
HOST = "localhost"
PORT = 30003
BUFFER_SIZE = 100
CONNECT_ATTEMPT_LIMIT = 10
CONNECT_ATTEMPT_DELAY = 5.0


def connect_to_socket(loc, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((loc, port))
    return s


# open a socket connection
def open_socket(host, port, connect_attempt_limit, connect_attempt_delay):
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

    jd = dcf_ast.julian_day(year=year, month=month, day=day, hour=hour, minute=minute, sec=seconds)
    utc = dcf_ast.unix_from_jd(jd=jd)
    return utc

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

    # parse command line options
    args = parser.parse_args()

    # print args.accumulate(args.in)
    count_total = 0

    # connect to database
    [db, c] = connect_db()

    s = open_socket(host=args.host, port=args.port,
                    connect_attempt_limit=args.connect_attempt_limit,
                    connect_attempt_delay=args.connect_attempt_delay)

    data_str = ""

    try:

        # loop until an exception
        while True:
            # get current time
            parse_time = time.time()

            # receive a stream message
            message = ""
            try:
                message = s.recv(args.buffer_size).decode("utf-8")
                logging.info(message)
                data_str += message.strip("\n")
            except socket.error:
                # this happens if there is no connection and is delt with below
                pass

            if len(message) == 0:
                logging.info("No broadcast received. Attempting to reconnect")
                time.sleep(args.connect_attempt_delay)
                s.close()
                s = open_socket(host=args.host, port=args.port,
                                connect_attempt_limit=args.connect_attempt_limit,
                                connect_attempt_delay=args.connect_attempt_delay)
                continue

            # it is possible that more than one line has been received
            # so split it then loop through the parts and validate

            data = data_str.split("\n")
            for d in data:
                line = d.split(",")

                # if the line has 22 items, it's valid
                if len(line) == 22:
                    # extract components
                    message_type, transmission_type, session_id, aircraft_id, hex_ident, flight_id, \
  generated_date, generated_time, logged_date, logged_time, callsign, altitude, \
  ground_speed, track, lat, lon, vertical_rate, \
                    squawk, alert, emergency, spi, is_on_ground = line

                    # check if aircraft is within search region
                    is_ok = location_filter.is_in_range(lat, lon)

                    # extract timestamps
                    if is_ok:
                        generated_timestamp = parse_date_time(generated_date, generated_time)
                        logged_timestamp = parse_date_time(logged_date, logged_time)

                        # check entry is ok
                        is_ok = generated_timestamp is not None and logged_timestamp is not None

                    # add the row to the db
                    if is_ok:
                        c.execute("""
INSERT INTO adsb_squitters
 (message_type, transmission_type, session_id, aircraft_id, hex_ident, flight_id,
  generated_timestamp, logged_timestamp, callsign, altitude,
  ground_speed, track, lat, lon, vertical_rate, squawk, alert, emergency, spi, is_on_ground, parsed_timestamp
 ) VALUES (%s, %s, %s, %s, %s, %s,
           %s, %s, %s, %s,
           %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                              (message_type, transmission_type, session_id, aircraft_id, hex_ident, flight_id)
                              )

                        # increment counts
                        count_total += 1

                        # commit the new rows to the database in batches
                        c.commit()

                    # since everything was valid we reset the stream message
                    data_str = ""
                else:
                    # the stream message is too short, prepend to the next stream message
                    data_str = d
                    continue

    except KeyboardInterrupt:
        logging.info("Closing connection")
        s.close()
        c.commit()
        c.close()
        logging.info("{:d} squitters added to your database".format(count_total))

        if __name__ == "__main__":
            main()
