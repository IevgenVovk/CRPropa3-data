import numpy as np
import interactionRate
import os
import gitHelp as gh
from crpropa import eV
from calc_all import fields_cmbebl, fields_urb

cdir = os.path.split(__file__)[0]

lgamma = np.linspace(6, 16, 251)  # tabulated Lorentz factors
gamma = 10**lgamma

# ----------------------------------------------------
# Load proton / neutron cross sections [1/m^2] for tabulated energies [J]
# truncate to largest length 2^i + 1 for Romberg integration
# ----------------------------------------------------
ddir1 = os.path.join(cdir, 'tables/PPP/xs_proton.txt')
d = np.genfromtxt(ddir1, unpack=True)
eps1 = d[0, :2049] * 1e9 * eV  # [J]
xs1 = d[1, :2049] * 1e-34  # [m^2]

ddir2 = os.path.join(cdir, 'tables/PPP/xs_neutron.txt')
d = np.genfromtxt(ddir2, unpack=True)
eps2 = d[0, :2049] * 1e9 * eV  # [J]
xs2 = d[1, :2049] * 1e-34  # [m^2]


def process(field):
    """ 
        calculate the interction rate on the given photonfield
        
        field : photon field as defined in photonField.py
    """

    # output folder
    folder = 'data/PhotoPionProduction'
    if not os.path.exists(folder):
        os.makedirs(folder)

    # ----------------------------------------------------
    # calculate interaction rates at z=0, default option
    # ----------------------------------------------------
    r1 = interactionRate.calc_rate_eps(eps1, xs1, gamma, field)
    r2 = interactionRate.calc_rate_eps(eps2, xs2, gamma, field)

    fname = folder + '/rate_%s.txt' % field.name
    data = np.c_[lgamma, r1, r2]
    fmt = '%.2f\t%.6e\t%.6e'
    try:
        git_hash = gh.get_git_revision_hash()
        header = ("Photo-pion interaction rate with the %s\n"% field.info
                  +"Produced with crpropa-data version: "+git_hash+"\n"
                  +"log10(gamma)\t1/lambda_proton [1/Mpc]\t1/lambda_neutron [1/Mpc]" )
    except:
        header = ("Photo-pion interaction rate with the %s\nlog10(gamma)"
                  "\t1/lambda_proton [1/Mpc]\t1/lambda_neutron [1/Mpc]" % field.info)
    np.savetxt(fname, data, fmt=fmt, header=header)

    # ----------------------------------------------------
    # calculate redshift dependent interaction rates
    # ----------------------------------------------------
    redshifts = field.redshift
    if redshifts is None:
        return  # skip CMB
    if len(redshifts) > 100:
        redshifts = redshifts[::10]  # thin out long redshift lists (Finke10)

    data = []
    for z in redshifts:
        r1 = interactionRate.calc_rate_eps(eps1, xs1, gamma, field, z)
        r2 = interactionRate.calc_rate_eps(eps2, xs2, gamma, field, z)
        data.append(np.c_[[z] * len(lgamma), lgamma, r1, r2])

    data = np.concatenate([d for d in data], axis=0)
    np.nan_to_num(data)
    fname = folder + '/rate_%s.txt' % field.name.replace('IRB', 'IRBz')
    fmt = '%.2f\t%.2f\t%.6e\t%.6e'
    try:
        git_hash = gh.get_git_revision_hash()
        header = ("Photo-pion interaction rate with the %s (redshift dependent) \n"% field.info
                  +"Produced with crpropa-data version: "+git_hash+"\n"
                  + "z\tlog10(gamma)\t1/lambda_proton [1/Mpc]\t1/lambda_neutron [1/Mpc]")
    except:
        header = ("Photo-pion interaction rate for the %s\n (redshift dependent)"
                  "z\tlog10(gamma)\t1/lambda_proton [1/Mpc]\t1/lambda_neutron [1/Mpc]" % field.info)
    np.savetxt(fname, data, fmt=fmt, header=header)

if __name__ == "__main__":

    for field in fields_cmbebl+fields_urb:
        print(field.name)
        process(field)
