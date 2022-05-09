import numpy as np
import IRBEM

from elfin_conjunctions.load import elfin


R_e = 6378.137  # km

class Elfin_footprint:
    def __init__(self, sc_id, day):
        """"
        Load ELFIN's ephemeris and calculate its footprint.

        Parameters
        ----------
        time: np.array
            An (nTime) shaped array of datetime objects
        pos_gei: np.array
            The satellite positions in GEI coordinates with shape (nTime, 3)
        """
        self.time, self.state = elfin.load_state(sc_id, day)
        self.pos_gei = self.state.varget(f'el{sc_id.lower()}_pos_gei')/R_e

        # all stands for (altitude, latitude, longitude), the variable order for IRBEM.
        transform = IRBEM.Coords()
        _all = transform.coords_transform(self.time, self.pos_gei, 'GEI', 'GDZ')
        self.lla = self._swap_all2lla(_all)

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
        _all = np.zeros_like(self.lla)

        for i, (time_i, lla_i) in enumerate(zip(self.time, self.lla)):
            X = {'Time':time_i, 'x1':lla_i[2], 'x2':lla_i[0], 'x3':lla_i[1]}
            _all[i, :] = m.find_foot_point(X, {}, alt, hemi_flag)['XFOOT']
        _all[_all == -1E31] = np.nan
        self.lla = self._swap_all2lla(_all)
        return

    def _swap_all2lla(self, _all):
        """
        Swap from IRBEM's (alt, lat, lon) to (lat, lon, alt) coordinates.
        """
        return np.array([_all[:, 1], _all[:, 2], _all[:, 0]]).T