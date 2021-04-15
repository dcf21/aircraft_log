# -*- coding: utf-8 -*-
# location_filter.py

import time
import logging
from math import atan2, pi

from adsb_helpers import dcf_ast, sunset_times


class LocationFilter:
    """
    A class for filtering squitters from a particular geographic area.
    """

    def __init__(self):
        # Database of aircraft IDs which we have identified as falling within filtered area
        self.allowed_ids = {}

        # Grace period within which to follow aircraft which have passed through the filtered area
        self.grace_period = 300

    def is_in_range(self, id: str, lat: float, lon: float):
        """
        Test whether a supplied geographic position lies within the filtered region.

        :param id:
            An identification string for this aircraft
        :param lat:
            Latitude, degrees
        :param lon:
            Longitude, degrees
        :return:
            bool
        """
        time_now = time.time()

        if lat is not None and lon is not None:
            if self.test_point(id=id, lat=lat, lon=lon):
                self.allowed_ids[id] = time_now

        if id not in self.allowed_ids:
            return False

        if self.allowed_ids[id] < time_now - self.grace_period:
            del self.allowed_ids[id]
            return False

        return True

    def test_point(self, id: str, lat: float, lon: float):
        """
        Test whether a supplied geographic position lies within the filtered region.

        :param id:
            An identification string for this aircraft
        :param lat:
            Latitude, degrees
        :param lon:
            Longitude, degrees
        :return:
            bool
        """

        raise NotImplementedError("The test_point method must be implemented separately in a child class")


class LocationFilter_Cambridge(LocationFilter):
    """
    A location filter which picks out aircraft within a circular area around Cambridge
    """

    def __init__(self, radius=50, lat=52.222, lon=0.078):
        """
        A location filter which picks out aircraft within a circular area around Cambridge

        :param radius:
            Search radius, km
        :param lat:
            Latitude of centre of search region, degrees
        :param lon:
            Longitude of centre of search region, degrees
        """
        self.search_radius_km = radius
        self.search_central_lat = lat
        self.search_central_lon = lon

        self.radius_earth = 6371e3  # metres
        self.search_radius = radius * 1e3  # metres
        self.search_angle = atan2(self.search_radius, self.radius_earth)  # radians

        self.sun_position_grace_time = 30
        self.sun_alt_az = [999, 999]
        self.sun_alt_az_time = 0

        # Call parent constructor
        super(LocationFilter_Cambridge, self).__init__()

    def test_point(self, id: str, lat: float, lon: float):
        """
        Test whether a supplied geographic position lies within the filtered region.

        :param id:
            An identification string for this aircraft
        :param lat:
            Latitude, degrees
        :param lon:
            Longitude, degrees
        :return:
            bool
        """

        deg = pi / 180

        # Look up angular distance of plane across Earth's surface from observer
        angular_distance = dcf_ast.ang_dist(ra0=self.search_central_lon * deg,
                                            dec0=self.search_central_lat * deg,
                                            ra1=lon * deg,
                                            dec1=lat * deg)
        physical_distance = angular_distance * self.radius_earth / 1e3 # km

        # Is this within range?
        is_within_range = angular_distance < self.search_angle

        # Look up position of the Sun
        time_now = time.time()
        if self.sun_alt_az_time < time_now-self.sun_position_grace_time:
            sun_pos = sunset_times.sun_pos(utc=time_now)
            self.sun_alt_az = sunset_times.alt_az(ra=sun_pos[0], dec=sun_pos[1], utc=time_now,
                                                  latitude=self.search_central_lat, longitude=self.search_central_lon)
            self.sun_alt_az_time = time_now

        # Check whether Sun is below the horizon
        if self.sun_alt_az[0] > -2:
            logging.info("Rejecting squitter as Sun is {:5.1f} deg above horizon.".format(self.sun_alt_az[0]))
            return False

        if not is_within_range:
            logging.info("Rejecting <{}>; plane is {:5.1f} km away.".format(id, physical_distance))
            return False

        return True
