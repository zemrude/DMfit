import abc
from typing import Dict, List, Optional, Iterable, Mapping, Any, Tuple, Union
import numpy as np
import collections
import itertools 
from data import DataSet
from modeling import Model


LIKELIHOODS = ["Poisson", "Effective"]

class LikelihoodRatioTest:
    """"""
    
    
    def __init__(self, model, null_model = None, llh_type = "Poisson", data = None, **kwargs):
        self._model = model
        self.llh_type = llh_type
        self._meta_data = kwargs.copy()
        self._data = data
        
        if null_model is not None:
            self._null_model = null_model
            
        
    @property    
    def meta_data(self) -> dict:
        return self._meta_data

    @property
    def data(self) -> DataSet:
        if self._data is not None:
            return self._data
        else:
            raise ValueError("Data has not been loaded yet!")
            
    @data.setter
    def data(self, value: DataSet):
        self._data = value
    

    @property
    def llh_type(self) -> str:
        return self._llh_type
    
    @llh_type.setter
    def llh_type(self, value: str):
        if value in LIKELIHOODS:
            self._llh_type = value
        else:
            print("Likelihood type {} is not implented, available likelihoods are {}".format(value, LIKELIHOODS))
    
    
    
    def LLH(self, *pars):
        "TODO: make this faster?"
        if(len(pars) != self._model.nparameters):
            raise ValueError("The number of parameters passed is larger than the number of parameters in the Model")
        
        for z, p in zip(iter(model._parameters.values()), params):
            z.value = p
        
        #Avoid NaN when calculating log
        mask = np.where(self._model[:] > 0)
        
        logs = map(np.log, self._data.ntotal * np.asarray(self._model[mask]))        
      
        return -np.sum(self._data.values[mask] * logs - self._data.ntotal*self._dat.values[mask])
    
    
    def __str__(self):
        lines = []
        lines.append(self._model.__str__())
        lines.append(self._data.__str__())
        lines.append("Minimizer ")
        return "\n".join(lines)
        
    
    
    
    
    
    
