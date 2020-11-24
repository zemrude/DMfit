import abc
from typing import Dict, List, Optional, Iterable, Mapping, Any, Tuple, Union
import numpy as np
import collections
import itertools 

__all__ = ["Parameter"]

class Parameter():
    """ Parameter class 
    To do: Add priors
    To do: Add scale
    
    This idea is taking from Gammapy and is implented as such
    
    value = factor x scale

    scale only takes values of 0.01, 0.1, 1, 10, etc..
    

    """
    
    def __init__(self, name, value, limits, scale = 1, fixed = False, is_nuisance = False, **kwargs):
        
        self.fixed = fixed
        self._meta_data = kwargs.copy()
        #First we fixed the scale
        
        if not np.log10(scale).is_integer():
            print ("Scale can only take as value power of 10.")
        else:
            self._scale = scale
        
        #Value will only set the factor, once the scale is fixed
        self.value = value
      
    
        limits = np.asarray(limits)
        self.limits = limits
      
    
        self.name = name
        self.is_nuisance = is_nuisance
        
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
        return self._factor * self._scale
    
    @value.setter
    def value(self, value: float):
        self.factor = float(value) / self._scale
 
    @property
    def scale(self) -> float:
        return self._scale
    
    @scale.setter
    def scale(self, val: float):
        value = self.value
        limits = self.limits
        
        if not np.log10(val).is_integer():
            print ("Scale can only take as value power of 10.")
        else:
            self._scale = val 
            #we change the scale, but not factor, so that could lead to a change of value!
            self._factor = float(value) / self._scale
            #Same for the limits
            self._factor_limits = limits / self._scale
            
    @property
    def factor(self) -> float:
        return self._factor
    
    @factor.setter
    def factor(self, value: float):
        self._factor = value

        
    @property
    def fixed(self) -> bool:
        return self._fixed

    @fixed.setter
    def fixed(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(f"Invalid type: {value}, {type(value)}")
        self._fixed = value

    @property
    def is_nuisance(self) -> bool:
        return self._is_nuisance

    @is_nuisance.setter
    def is_nuisance(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(f"Invalid type: {value}, {type(value)}")
        self._is_nuisance = value

    @property
    def limits(self) -> np.ndarray:
        return self._factor_limits * self._scale
    
    @limits.setter
    def limits(self, limits: np.ndarray):
        if ( len(limits) != 2 ):
            raise ValueError( "Limits need a dim = 2")
        elif limits[0] >= limits[1]:
            raise ValueError( "Lower limit is equal or greater than upper limit")
        else:
            self.factor_limits = limits / self._scale
    
    @property
    def upper_limit(self) -> float:
        return self.limits[1]
    
    @property
    def lower_limit(self) -> float:
        return self.limits[0]
    
    @upper_limit.setter
    def upper_limit(self, value : float):
        if value < self._limits[0]:
            raise ValueError( " Upper limit {} is smaller than lower limit {}".format(value, self._limits[0]))
        else:
            self._factor_limits[1] = value / self._scale
    
    @lower_limit.setter
    def lower_limit(self, value : float):
        if value > self._limits[1]:
            raise ValueError( " Lower limit {} is greater than upper limit {}".format(value, self._limits[1]))
        else:
            self._factor_limits[0] = value / self._scale
    
            
    @property
    def factor_limits(self) -> np.ndarray:
        return self._factor_limits
    
    @factor_limits.setter
    def factor_limits(self, limits: np.ndarray):
        if ( len(limits) != 2 ):
            raise ValueError( "Limits need a dim = 2")
        elif limits[0] >= limits[1]:
            raise ValueError( "Lower limit is equal or greater than upper limit")
        else:
            self._factor_limits = limits
    
    
    
    def __add__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            expression = "self._parameters['{}'].value + {}".format(self.name, other)
            name = "{}+{}".format(other, self.name)
            m = Model(parameters = [self], name=name, expression=expression)
            return m

        elif isinstance(other, Parameter):
            expression = "self._parameters['{}'].value + self._parameters['{}'].value".format(other.name, self.name)
            name = "{}+{}".format(other.name, self.name)
            m = Model(parameters=[self, other], name=name, expression=expression)
            return m
        
    def __radd__(self, other):
        return __add__(other)
    
    
    def __sub__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            expression = "self._parameters['{}'].value - {}".format(self.name, other)
            name = "{}-{}".format(self.name, other)
            m = Model(parameters = [self], name=name, expression=expression)
            return m

        elif isinstance(other, Parameter):
            expression = "self._parameters['{}'].value - self._parameters['{}'].value".format(self.name, other.name)
            name = "{}-{}".format(self.name, other.name)
            m = Model(parameters=[self, other], name=name, expression=expression)
            return m
        
    def __rsub__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            expression = "{} - self._parameters['{}'].value".format(other, self.name)
            name = "{}-{}".format(other, self.name)
            m = Model(parameters = [self], name=name, expression=expression)
            return m

        elif isinstance(other, Parameter):
            expression = "self._parameters['{}'].value - self._parameters['{}'].value".format(other.name, self.name)
            name = "{}-{}".format(other.name,self.name)
            m = Model(parameters=[self, other], name=name, expression=expression)
            return m
        
    
    def autoscale(self):
        #We set the scale based on the value
        value = self.value
        if value != 0:
            exponent = np.floor(np.log10(np.abs(value)))
            scale = np.power(10.0, exponent)
            self.scale = scale
            self.value = value
          
    
    def __str__(self):
        lines = []
        lines.append(" Name: {}".format(str(self.name)))
        lines.append(" Value: {:.2f}".format(self.value))
        lines.append(" Scale: {:.1e}".format(self.scale))
        lines.append(" Limits: ({:.1f}, {:.1f})".format(self.limits[0], self.limits[1]))
        lines.append(" Fixed: {}".format(self.fixed))
        lines.append(" Is nuisance? {}".format(self.is_nuisance))
        return ",".join(lines)

    
from .model import Model