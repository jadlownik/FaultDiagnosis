import numpy as np
from numpy import * # For access to all fundamental functions, constants etc.
def Classic_polybox_ResGen(z,state,params,Ts):
    """ CLASSIC_POLYBOX_RESGEN Sequential residual generator for model ''
    Causality: algebraic

    Structurally sensitive to faults: f_M2, f_M3, f_A2

    Example of basic usage:
    Let z be the observations matrix, each column corresponding to a known signal and Ts the sampling time,
    then the residual generator can be simulated by:

    r = np.zeros(N) # N number of data points
    state = {    for k,zk in enumerate(z):
        r[k], state = Classic_polybox_ResGen( zk, state, params, Ts )

    State is a dictionary with the keys: 
    File generated Tue Jun 18 23:53:45 2024
    """
    def Classic_polybox_ResGen_core(z, state, params, Ts):
        # Known signals
        u_b = z[1]
        u_c = z[2]
        u_d = z[3]
        u_e = z[4]
        u_g = z[6]

        # Residual generator body
        g = u_g # e7
        e = u_e # e12
        d = u_d # e11
        b = u_b # e8
        y = b*d # e2
        z = g - y # e5
        c = z/e # e3
         
        r = -c + u_c # e9

        return (r, state)

    return Classic_polybox_ResGen_core(z, state, params, Ts)
