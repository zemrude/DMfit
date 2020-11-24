import abc
from typing import Dict, List, Optional, Iterable, Mapping, Any, Tuple, Union
import numpy as np
import collections
import itertools 
from utils.numba_functions import nb_log, nb_sum, nb_where, nb_random_poisson

__all__ = ["DataSet"]

DATATYPES = ["unblinding", "simulation", "scrambling"]

class DataSet():
    
    def __init__(self, values = None, errors2 = None, data_type = "simulation",  **kwargs):
        
        self.ntotal = 0
        
        if values is not None:
            values = np.asarray(values)
            self.values = values
           
        if errors2 is not None:
            errors2 = np.asarray(errors2)
            self.errors2 = errors2
        
        self.data_type = data_type
        

    
    @property
    def values(self):
        try:
            return self._values
        except AttributeError as e:
            raise AttributeError(str(e), "values not set yet!")
        
    @values.setter
    def values(self, values: np.ndarray) -> None:
        values = np.asarray(values)
        if np.any(values < 0):
            raise ValueError("Cannot have negative values in the pdf.")
        self._values = values
        self.ntotal = np.sum(self._values)
        
        
    @property
    def errors2(self):
        try:
            return self._errors2
        except AttributeError as e:
            raise AttributeError(str(e), "Errors2 not set yet!")
   
    @errors2.setter
    def errors2(self, errors2: np.ndarray) -> None:
        if np.any(errors2 < 0):
            raise ValueError("Cannot have negative errors2")
        
        self._errors2 = np.asarray(errors2)
   
    def fill_errors2(self):
        """ Fill errors as sqrt(n) """
        self._errors2 = self._values
        
    @property
    def data_type(self) -> str:
        return self._data_type
    
    @data_type.setter
    def data_type(self, value: str):
        if value not in DATATYPES:
            raise ErrorValue("Data type {} not implemented".format(str(value)))
        else:
            self._data_type = str(value)
            
            
    def residuals(self, model):
        return self._values - model[:]
    
    
    def sample(self, ntotal, model):
        "Makes a pseudo sample"
       
        self.values = list(map(nb_random_poisson, ntotal * np.asarray(model)))


    def __str__(self):
        lines = []
        lines.append("DataSet type {}".format(self._data_type))
        lines.append("Total number of events: {}".format(self.ntotal))
        return "\n".join(lines)
