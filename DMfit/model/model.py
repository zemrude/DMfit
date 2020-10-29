import abc
from typing import Dict, List, Optional, Iterable, Mapping, Any, Tuple, Union
import numpy as np
import collections



class Model(abc.ABC):
    def __init__(self, pdfs = None, parameters = None, **kwargs):
        self._pdfs = collections.OrderedDict()
        self._parameters = collections.OrderedDict()
       
        if pdfs is not None:
            for pdf in pdfs:
                self._add_pdf(pdf)
        if parameters is not None:    
            for param in parameters:
                self._add_parameter(param)
        
        self._meta_data = kwargs.copy()
                
    def _add_parameter(self, param):
    
        if isinstance(param, Parameter):
            name = param.name
            
            if name  in self._parameters.keys():
                print (r"Parameter {} already exists in the model!".format(name))

            else:
                self._parameters[name] = param
            
    def _add_pdf(self, pdf):
        
        
        
        
        if isinstance(pdf, PdfBase):
            name = pdf.name
            if name  in self._pdfs.keys():
                print (r"PDF {} already exists in the model!".format(name))
            else:
                self._pdfs[name] = pdf
            
    @property
    def meta_data(self) -> dict:
        """A dictionary of non-numerical information 
        """
        return self._meta_data
    
    @property
    def name(self) -> Optional[str]:
        return self._meta_data.get("name", None)
   
    @name.setter
    def name(self, value: str):
        self._meta_data["name"] = str(value)
    
    
    @property
    def expression(self) -> Optional[str]:
        """Name of the histogram (stored in meta-data)."""
        return self._meta_data.get("expression", None)
    
    @expression.setter
    def expression(self, value: str):
        self._meta_data["expression"] = str(value)
    
    def __getitem__(self, index: int):
        expression = self.expression
        variables = {"index" : index, "self": self}
        return eval(expression, {}, variables)
            
    def __add__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            frequencies = other + self._frequencies
            return frequencies

        elif isinstance(other, PdfBase):
            expression = "{} + self._pdfs['{}'][index]".format(self.expression, other.name)
            name = "{} + {}".format(self.name, other.name)
            m = Model(pdfs=[self._pdfs + other], parameters=self._parameters, name=name, expression=expression)
            return m
        
    def __radd__(self, other):
        return self.__add__(other)