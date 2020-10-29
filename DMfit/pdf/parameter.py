import abc
from typing import Dict, List, Optional, Iterable, Mapping, Any, Tuple, Union
import numpy as np
   
    

class Parameter():
    """ Parameter class """
    def __init__(self, name, value, limits, fixed, **kwargs):
        
        limits = np.asarray(limits)
        self.limits = limits
        self.fixed = fixed
        self._meta_data = kwargs.copy()
        self.value = value
        self.name = name
    @property    
    def meta_data(self) -> dict:
        return self._meta_data
    
    @property
    def name(self) -> Optional[str]:
        
        return self._meta_data.get("name", None)
    
    @name.setter
    def name(self, value: str):
        self._meta_data["name"] = str(value)
    
    @property
    def value(self) -> float:
        """Name of the histogram (stored in meta-data)."""
        return self._value
    
    @value.setter
    def value(self, value: float):
        """Name of the histogram (stored in meta-data)."""
        
        if self.limits[0] <= value <= self.limits[1]:
            self._value = value
        else:
            raise ValueError(" Value {} is not between limits ({}, {})".format(value, self.limits[0], self.limits[1]))
   
    @property
    def limits(self) -> np.ndarray:
        return self._limits
    
    @limits.setter
    def limits(self, limits: np.ndarray):
        if ( len(limits) != 2 ):
            raise ValueError( "Limits need a dim = 2")
        elif limits[0] >= limits[1]:
            raise ValueError( "Lower limit is equal or greater than upper limit")
        else:
            self._limits = limits
    @property
    def upper_limit(self) -> float:
        return self._limits[1]
    @property
    def lower_limit(self) -> float:
        return self._limits[0]
    @upper_limit.setter
    def upper_limit(self, value : float):
        if value < self._limits[0]:
            raise ValueError( " Upper limit {} is smaller than lower limit {}".format(value, self._limits[0]))
        else:
            self._limits[1] = value
    @lower_limit.setter
    def lower_limit(self, value : float):
        if value > self._limits[1]:
            raise ValueError( " Lower limit {} is greater than upper limit {}".format(value, self._limits[1]))
        else:
            self._limits[0] = value
    
        
    def __str__(self):
        lines = []
        lines.append(" Name: {}".format(str(self.name)))
        lines.append(" Value: {}".format(str(self._value)))
        lines.append(" Limits: ({}, {})".format(str(self.limits[0]), str(self.limits[1])))
        lines.append(" Is fixed? {}".format(self.fixed))
        return "\n".join(lines)