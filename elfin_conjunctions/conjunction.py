import numpy as np
import asilib

import IRBEM

class Conjunction:
    def __init__(self, time, pos_gei):
        """"
        Calculate conjunctions between a satellite with its position in the GEI coordinates.

        Parameters
        ----------
        time: np.array
            An (nTime) shaped array of datetime objects
        pos_gei: np.array
            The satellite positions in GEI coordinates with shape (nTime, 3)
        """
        self.time = np.array(time)
        # all stands for (altitude, latitude, longitude), the variable order for IRBEM.
        transform = IRBEM.Coords()
        _all = transform.coords_transform(time, pos_gei, 'GEI', 'GDZ')
        self.lla = np.array([_all[:, 1], _all[:, 2], _all[:, 0]]).T

        assert self.time
        return

    def map_footprint(self, alt=110, hemi_flag=0):
        """
        Map self.lla along the magnetic field line to alt using IRBEM.MagFields.find_foot_print.

        Parameters
        ----------
        alt: float
            The mapping altitude in units of kilometers
        hemi_flag: int
            What direction to trace the field line: 
            0 = same magnetic hemisphere as starting point
            +1   = northern magnetic hemisphere
            -1   = southern magnetic hemisphere
            +2   = opposite magnetic hemisphere as starting point
        """
        m = IRBEM.MagFields(kext='OPQ77')

        for time_i, lla_i in zip(self.time, self.lla):
            X = {'Time':time_i, 'x1':lla_i[2], 'x2':lla_i[0], 'x3':lla_i[1]}
            _footprint = 
        return