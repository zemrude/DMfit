import abc
from typing import Dict, List, Optional, Iterable, Mapping, Any, Tuple, Union
import numpy as np
import collections
import itertools 
from data import DataSet
from modeling import Model
from iminuit import Minuit

from utils.numba_functions import nb_log, nb_sum, nb_where

LIKELIHOODS = ["Poisson", "Effective"]

HYPOTHESIS = {'H0': 0, 'H1': 1}
            
class LikelihoodRatioTest:
    def __init__(self, model = None, null_model = None, llh_type = "Poisson", data = None, **kwargs):

        #Ratio test is H0, H1
        self._models = {"H0" : null_model, 
                        "H1" : model}
             

        llhs = {"H0" : self.llhH0, 
                "H1" : self.llhH1}
        
        self._minimizers = {"H0" : None,
                            "H1" : None}
        
        kwds = dict()
        kwds['errordef'] = Minuit.LIKELIHOOD 
        kwds['print_level'] = 2.
        z = {**kwds, **kwargs}
         
            
        #Minimizer work in factor space, not in value space
        
        for i, m in enumerate(self._models.values()):
            names = ([par.name for par in list(m.parameters.values())])
            limits = ([par.factor_limits for par in list(m.parameters.values())])
            init_values = ([par.factor for par in list(m.parameters.values())])
            self._minimizers[list(self._minimizers.keys())[i]] = Minuit.from_array_func(llhs[list(self._minimizers.keys())[i]], init_values, limit = limits, name = names, **z)
        
        self.llh_type = llh_type
        self._meta_data = kwargs.copy()
        self.data = data
        
 
        
    @property    
    def meta_data(self) -> dict:
        return self._meta_data
    
    @property
    def models(self) -> dict:
        return self._models
    
    @property
    def minimizers(self) -> dict:
        return self._minimizers
    
    @property
    def minimizerH0(self, tag) -> Minuit:
        return self._minimizers["H0"]

    @property
    def minimizerH1(self, tag) -> Minuit:
        return self._minimizers["H1"]

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
            raise ValueError("Likelihood type {} is not implented, available likelihoods are {}".format(value, LIKELIHOODS))
    
    
        
    def fitH0(self, **kwargs):
        return self.minimizers["H0"].migrad(**kwargs) 
  
            
    def fitH1(self, **kwargs):
        return self.minimizers["H1"].migrad(**kwargs) 

    @property
    def minLlhH1(self):
        try:
            return self.minimizers["H1"].fmin.fval
        except:
            raise AttributeError("You need to run .fit_H1 fist")

    @property
    def minLlhH0(self):
        try:
            return self.minimizers["H0"].fmin.fval
        except:
            raise AttributeError("You need to run .fit_H0 fist")

    @property
    def TS(self):
        return 2 * (self.minLlhH0 - self.minLlhH1)
        
            
    def llhH0(self, pars):
        """
        Wrapper function to _llh for Minuit
        
        """
        return self._llh(pars, model = self._models["H0"])
    
    def llhH1(self, pars):
        return self._llh(pars, model = self._models["H1"])
    
    
        
    def _llh(self, pars, model = None):
        """ Likelihood evaluation using the numba module 
            Numba wrappers (see numba_functions.py):
            
            nb_log -> np.log 
            nb_where -> np.where
            nb_sum -> np.sum
            
            --------------------
            Note: as numba needs to compile in time first call will be slower than usual.
        """
        if model is None:
            raise ValueError("Model {H0, H1} not specified!")
            
        if(len(pars) != model.npars):
            raise ValueError("The number of parameters {} passed is not the same as the number of parameters in the Model {}".format(len(pars), self._model.npars))
        
        
        #We change the parameters of the parameters
        #Minimizer work in factor space not in value space!
        #factor = value if scale is set to 1
        
        for z, p in zip(iter(model.parameters.values()), pars):
            z.factor = p
        
        mask = np.where(model[:] > 0)
    
        logs = np.asarray(list(map(nb_log, self._data.ntotal * np.asarray(model[mask]))))
      
        return -nb_sum(self._data.values[mask] * logs - self._data.ntotal * model[mask])
    
    
    def upperlimit(self):
        return 0
    
        
    def __str__(self):
        lines = []
        lines.append(self._model.__str__())
        lines.append("--------------------")
        lines.append(self._data.__str__())
        lines.append("Minimizer ")
        return "\n".join(lines)
        
    
    
    
    
    
    
