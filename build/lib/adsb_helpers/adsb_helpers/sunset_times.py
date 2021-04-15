# -*- coding: utf-8 -*-
# sunset_times.py

from math import pi, sin, cos, asin, atan2

from .dcf_ast import sidereal_time

deg = pi / 180


# Return the [RA, Dec] of the Sun at a given Unix time. See Jean Meeus, Astronomical Algorithms, pp 163-4
def sun_pos(utc):
    """
    Calculate an estimate of the J2000.0 RA and Decl of the Sun at a particular Unix time
    :param utc:
        Unix time
    :type utc:
        float
    :return:
        [RA, Dec] in [hours, degrees]
    """

    jd = utc / 86400.0 + 2440587.5

    t = (jd - 2451545.0) / 36525.
    l0 = 280.46646 + 36000.76983 * t + 0.0003032 * t * t
    m = 357.52911 + 35999.05029 * t + 0.0001537 * t * t
    # e = 0.016708634 - 0.000042037 * t - 0.0000001267 * t * t

    c = ((1.914602 - 0.004817 * t - 0.000014 * t * t) * sin(m * deg) +
         (0.019993 - 0.000101 * t) * sin(2 * m * deg) +
         0.000289 * sin(3 * m * deg))

    tl = l0 + c  # true longitude
    # v = m + c  # true anomaly

    epsilon = 23 + 26. / 60 + 21.448 / 3600 + 46.8150 / 3600 * t + 0.00059 / 3600 * t * t + 0.001813 / 3600 * t * t * t

    ra = 12 / pi * atan2(cos(epsilon * deg) * sin(tl * deg), cos(tl * deg))  # hours
    dec = 180 / pi * asin(sin(epsilon * deg) * sin(tl * deg))  # degrees

    # Ensure right ascension is in the range 0-24 hours
    if ra < 0:
        ra += 24

    return ra, dec


def alt_az(ra, dec, utc, latitude, longitude):
    """
    Converts [RA, Dec] into local [altitude, azimuth]

    :param ra:
        The right ascension of the object, hours, epoch of observation.
    :param dec:
        The declination of the object, degrees, epoch of observation.
    :param longitude:
        The longitude of the observer, degrees
    :param latitude:
        The latitude of the observer, degrees
    :param utc:
        The unix time of the observation
    :return:
        The [altitude, azimuth] of the object in degrees
    """
    ra *= pi / 12
    dec *= pi / 180
    st = sidereal_time(utc=utc) * pi / 12 + longitude * pi / 180
    xyz = [sin(ra) * cos(dec),
           -sin(dec),  # y-axis = towards south pole
           cos(ra) * cos(dec)]  # z-axis = vernal equinox; RA=0

    # Rotate by hour angle around y-axis
    xyz2 = [0, 0, 0]
    xyz2[0] = xyz[0] * cos(st) - xyz[2] * sin(st)
    xyz2[1] = xyz[1]
    xyz2[2] = xyz[0] * sin(st) + xyz[2] * cos(st)

    # Rotate by latitude around x-axis
    xyz3 = [0, 0, 0]
    t = pi / 2 - latitude * pi / 180
    xyz3[0] = xyz2[0]
    xyz3[1] = xyz2[1] * cos(t) - xyz2[2] * sin(t)
    xyz3[2] = xyz2[1] * sin(t) + xyz2[2] * cos(t)

    alt = -asin(xyz3[1])
    az = atan2(xyz3[0], -xyz3[2])

    # [altitude, azimuth] of object in degrees
    return [alt * 180 / pi, az * 180 / pi]


def ra_dec(alt, az, utc, latitude, longitude):
    """
    Converts local [altitude, azimuth] into [RA, Dec] at epoch

    :param alt:
        The altitude of the object, degrees
    :param az:
        The azimuth of the object, degrees
    :param utc:
        The unix time of the observation
    :param longitude:
        The longitude of the observer, degrees
    :param latitude:
        The latitude of the observer, degrees
    :return:
        The [RA, Dec] of the object, in hours and degrees, at epoch
    """
    alt *= pi / 180
    az *= pi / 180
    st = sidereal_time(utc=utc) * pi / 12 + longitude * pi / 180
    xyz3 = [sin(az) * cos(alt), sin(-alt), -cos(az) * cos(alt)]

    # Rotate by latitude around x-axis
    xyz2 = [0, 0, 0]
    t = pi / 2 - latitude * pi / 180
    xyz2[0] = xyz3[0]
    xyz2[1] = xyz3[1] * cos(t) + xyz3[2] * sin(t)
    xyz2[2] = -xyz3[1] * sin(t) + xyz3[2] * cos(t)

    # Rotate by hour angle around y-axis
    xyz = [0, 0, 0]
    xyz[0] = xyz2[0] * cos(st) + xyz2[2] * sin(st)
    xyz[1] = xyz2[1]
    xyz[2] = -xyz2[0] * sin(st) + xyz2[2] * cos(st)

    dec = -asin(xyz[1])
    ra = atan2(xyz[0], xyz[2])

    while ra < 0:
        ra += 2 * pi
    return [ra * 12 / pi, dec * 180 / pi]
