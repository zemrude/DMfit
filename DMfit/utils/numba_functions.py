import numpy as np
from numba import jit, njit

kwd = {"fastmath": True}



@njit(**kwd)
def nb_log(val):
    return np.log(val)

@njit(**kwd)
def  nb_sum(val):
    return np.sum(val)

@njit(**kwd)
def nb_where(val):
    return np.where(val)

@njit(**kwd)
def nb_random_poisson(val):
    return np.random.poisson(val)