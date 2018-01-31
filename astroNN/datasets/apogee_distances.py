# ---------------------------------------------------------#
#   astroNN.datasets.apogee_distances: APOGEE Distances
# ---------------------------------------------------------#

import numpy as np
from astropy.io import fits
from astropy import units as u

from astroNN.apogee.downloader import apogee_distances
from astroNN.apogee import allstar
from astroNN.gaia import mag_to_absmag, mag_to_fakemag


def load_apogee_distances(dr=None, metric='absmag'):
    """
    NAME:
        load_apogee_distances
    PURPOSE:
        load apogee distances (absolute magnitude from stellar model)
    INPUT:
        metric (string): which metric you want ot get back
                "absmag" for absolute magnitude
                "fakemag" for fake magnitude
                "distance" for distance
    OUTPUT:
    HISTORY:
        2018-Jan-25 - Written - Henry Leung (University of Toronto)
    """
    fullfilename = apogee_distances(dr=dr, verbose=1)

    with fits.open(fullfilename) as F:
        hdulist = F[1].data
        # Convert kpc to pc
        distance = hdulist['BPG_dist50'] * 1000
        dist_err = (hdulist['BPG_dist84'] - hdulist['BPG_dist16']) * 1000

    # Bad index refers to nan index
    bad_index = np.argwhere(np.isnan(distance))

    if metric == 'distance':
        output = distance * u.parsec
        output_err = dist_err * u.parsec

    elif metric == 'absmag':
        allstarfullpath = allstar(dr=dr)
        with fits.open(allstarfullpath) as F:
            K_mag = F[1].data['K']

        absmag = mag_to_absmag(K_mag, 1/distance * u.arcsec)
        output = absmag
        output_err = dist_err
        print('Error array is wrong, dont use it, I am sorry')

    elif metric == 'fakemag':
        allstarfullpath = allstar(dr=dr)
        with fits.open(allstarfullpath) as F:
            K_mag = F[1].data['K']

        # fakemag requires parallax (mas)
        fakemag = mag_to_fakemag(K_mag, 1000/distance * u.mas)
        output = fakemag
        output_err = dist_err
        print('Error array is wrong, dont use it, I am sorry')

    else:
        raise ValueError('Unknown metric')

    # Set the nan index to -9999. as they are bad and unknown. Not magic_number as this is an APOGEE dataset
    output[bad_index], output_err[bad_index] = -9999., -9999.

    return output, output_err
