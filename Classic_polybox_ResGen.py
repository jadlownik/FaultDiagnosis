import numpy as np
from numpy import * # For access to all fundamental functions, constants etc.
def Classic_polybox_ResGen(z,state,params,Ts):
    """ CLASSIC_POLYBOX_RESGEN Sequential residual generator for model ''
    Causality: algebraic

    Structurally sensitive to faults: f_M1, f_M2, f_M3, f_A1, f_A2

    Example of basic usage:
    Let z be the observations matrix, each column corresponding to a known signal and Ts the sampling time,
    then the residual generator can be simulated by:

    r = np.zeros(N) # N number of data points
    state = {    for k,zk in enumerate(z):
        r[k], state = Classic_polybox_ResGen( zk, state, params, Ts )

    State is a dictionary with the keys: 
    File generated Wed Jun 19 22:19:12 2024
    """
    def Classic_polybox_ResGen_core(z, state, params, Ts):
        # Known signals
        u_a = z[0]
        u_b = z[1]
        u_d = z[3]
        u_e = z[4]
        u_f = z[5]
        u_g = z[6]

        # Residual generator body
        g = u_g # e12
        e = u_e # e10
        d = u_d # e9
        b = u_b # e7
        y = b*d # e2
        z = g - y # e5
        c = z/e # e3
        a = u_a # e6
        x = a*c # e1
        f = x + y # e4
         
        r = -f + u_f # e11

        return (r, state)

    return Classic_polybox_ResGen_core(z, state, params, Ts)
