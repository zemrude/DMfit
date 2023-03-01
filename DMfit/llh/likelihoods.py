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

            
class LikelihoodRatioTest:
    def __init__(self, model = None, null_model = None, llh_type = "Poisson", data = None, **kwargs):

        self.data = data
        #Ratio test is H0, H1
        self._models = collections.OrderedDict()

        if model is not None and null_model is not None:
            if isinstance(null_model, Model):
                self._models["H0"]  = null_model.copy()
            if isinstance(model, Model):
                self._models["H1"] = model.copy()
             

                     
        self._llhs = {"H0" : self.llhH0, 
                      "H1" : self.llhH1}
        
        self._minimizers = {"H0" : None,
                            "H1" : None}
        
        
        
        
        
        self.llh_type = llh_type
        self._meta_data = kwargs.copy()
       
        

    @property
    def llhs(self) -> dict:
        return self._llhs

        
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

        
    def fit(self, hypothesis, **kwargs):
        
        kwds = dict()
        kwds['errordef'] = Minuit.LIKELIHOOD 
        #kwds['print_level'] = 2.
        z = {**kwds, **kwargs}
         
            
        
        #Minimizer work in factor space, not in value space
        
        
        names, init_values, limits, fixed = np.transpose([(par.name, par.factor, par.factor_limits, par.fixed) for par in list(self._models[hypothesis].parameters.values())])

               
        self._minimizers[hypothesis] = Minuit.from_array_func(self._llhs[hypothesis], init_values, fix = fixed, limit = limits, name = names, **z)
        
        
        return self._minimizers[hypothesis].migrad(**kwargs) 
  

    @property
    def minLlhH1(self):
        try:
            return self.minimizers["H1"].fmin.fval
        except:
            raise AttributeError("You need to run .fit('H1') fist")

    @property
    def minLlhH0(self):
        try:
            return self.minimizers["H0"].fmin.fval
        except:
            raise AttributeError("You need to run .fit_H0 fist")

    @property
    def TS(self):
        return 2 * (self.minLlhH0 - self.minLlhH1)

    def TS_llhinterval(self, param_val, parname_fit, parname_fix):
        self.models['H0'].parameters[parname_fix].value = param_val
        self.fit("H0")
        self.fit("H1")
        if self.models['H1'].parameters[parname_fit].value > param_val:
            T = 0
        else:    
            T = self.TS
        return T    
            
    def llhH0(self, pars):
        """
        Wrapper function to _llh for Minuit
        
        """
        return self._llh(pars, model = self._models["H0"])
    
    def llhH1(self, pars):
        """
        Wrapper function to _llh for Minuit
        """
        
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
        if np.any(np.isnan(pars)):
            raise ValueError("One of the pass parameters is a nan")
            
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
    
    def upperlimit_llhinterval(self, parname_fit, parname_fix, conf_level):        
        #Default C.L.
        deltaTS = 1.64
        if conf_level==90:
            deltaTS = 1.64
        elif conf_level==95:
            deltaTS = 2.71

        # First, we try to find a range [param_low, param_up]
        # that contains the upper limit value

        self.fit('H1')
        param_up = self.models['H1'].parameters[parname_fit].value
        dTS = 0
        nIterations = 0

        while(dTS<deltaTS) and (nIterations<1000):                
            nIterations += 1            
            if param_up < 1e-14:
                param_up = 1e-14
            param_up=param_up+3.*np.abs(param_up)                        
            dTS = self.TS_llhinterval(param_up, parname_fit, parname_fix)

        if (dTS<deltaTS):
            raise RuntimeError('Can not find upper value to perform bisection search due to maximum number of iteration reached')    
        param_low = param_up/4.

        # enter the bisection search for upperlimit within a tolerance:
        # note: code below only for increasing function which should be the case for the test statistics as the function of signal fraction.

        # param_tol = 5e-8
        ts_tol = 0.001
        nIterations = 0
        param_mean = (param_up+param_low)/2. 
        while ( abs(dTS - deltaTS) > ts_tol ) and (nIterations<500):
            nIterations += 1
            param_mean = (param_up+param_low)/2.            
            dTS = self.TS_llhinterval(param_mean, parname_fit, parname_fix)
            if dTS == deltaTS:
                return dTS
            elif dTS < deltaTS:
                param_low = param_mean
            else:
                param_up = param_mean

        if nIterations==500:
            print('Warning: maximum number of iteration reached in bisection seacch')
        
        # print('upper limit: {}'.format(param_mean))
        # print('TS value at the output upper limit: {}'.format(dTS))

        return param_mean

        
    def __str__(self):
        lines = []
        lines.append(self._model.__str__())
        lines.append("--------------------")
        lines.append(self._data.__str__())
        lines.append("Minimizer ")
        return "\n".join(lines)
        
    
    
    
    
    
    
