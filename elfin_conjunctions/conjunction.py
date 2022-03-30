import numpy as np
import asilib

import IRBEM

from elfin_conjunctions.load import elfin
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

        assert self.time.shape[0] == self.lla.shape[0], 'The time and pos_gei shapes do not match.'
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
        self.footprint = np.zeros_like(self.lla)

        for i, (time_i, lla_i) in enumerate(zip(self.time, self.lla)):
            X = {'Time':time_i, 'x1':lla_i[2], 'x2':lla_i[0], 'x3':lla_i[1]}
            self.footprint[i, :] = m.find_foot_point(X, {}, alt, hemi_flag)['XFOOT']
            pass
        self.footprint[self.footprint == -1E31] = np.nan
        return

if __name__ == '__main__':
    R_e = 6378.137  # km
    sc_id = 'A'
    day = '2020-01-01'
    times, state = elfin.load_state(sc_id, day)
    pos_gei_re = state.varget(f'el{sc_id.lower()}_pos_gei')/R_e
    c = Conjunction(times, pos_gei_re)
    c.map_footprint()