import abc
from typing import Dict, List, Optional, Iterable, Mapping, Any, Tuple, Union
import numpy as np
import collections
import itertools 

class Model():
    
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
    
    #@expression.setter
    #def expression(self, value: str):
    #    self._meta_data["expression"] = str(value)
        
    def __len__(self):
        #To do check if the _pdfs is initiated
        return len(self._pdfs[0])
    
    def __getitem__(self, index: int):
        expression = self.expression
        variables = {"index" : index, "self": self}
        return eval(expression, {}, variables)
    def __mul__(self, other):
        """If we multiply by a float or a int, the method returns simply the frequencies multiplied """
       
        if isinstance(other, Model):
            expression = "({}) * ({})".format(self.expression, other.expression)
            name = "({})*({})".format(self.name, other.name)
            pdfs_self = list(self._pdfs.values())
            pdfs_other = list(other._pdfs.values())
            pdfs = list(itertools.chain(pdfs_self, pdfs_other))
            param_self = list(self._parameters.values())
            param_other = list(other._parameters.values())
            param = list(itertools.chain(param_self, param_other))
            m = Model(pdfs = pdfs, parameters= param, name=name, expression=expression)
            return m
        
        if isinstance(other, PdfBase):
            expression = "({}) * self._pdfs['{}'][index]".format(self.expression, other.name)
            name = "({}) * {}".format(self.name, other.name)
            
            pdfs_self = list(self._pdfs.values())
            pdfs = list(itertools.chain(pdfs_self, [other]))
            
            m = Model(pdfs=pdfs, parameters=list(self._parameters.values()), name=name, expression=expression)
            return m
           
        if isinstance(other, Parameter):
            expression = "self._parameters['{}'].value * ({})".format(other.name, self.expression)
            name = "{}*({})".format(other.name, self.name)
            pdfs = list(self._pdfs.values())
            param_self = list(self._parameters.values())
            param = list(itertools.chain(param_self, [other]))
            m = Model(pdfs = pdfs, parameters= param, name=name, expression=expression)
            return m
    
    def __rmul__(self, other):
        return self.__mul__(other)

    
    
    def __add__(self, other):
        
        if isinstance(other, PdfBase):
            expression = "{} + self._pdfs['{}'][index]".format(self.expression, other.name)
            name = "{} + {}".format(self.name, other.name)
            pdfs_self = list(self._pdfs.values())
            pdfs = list(itertools.chain(pdfs_self, other))
            
            m = Model(pdfs=pdfs, parameters=list(self._parameters.values()), name=name, expression=expression)
            return m
        
        elif isinstance(other, Model):
            expression = "{} + {}".format(self.expression, other.expression)
            name = "{} + {}".format(self.name, other.name)
            pdfs_self = list(self._pdfs.values())
            pdfs_other = list(other._pdfs.values())
            pdfs = list(itertools.chain(pdfs_self, pdfs_other))
            param_self = list(self._parameters.values())
            param_other = list(other._parameters.values())
            param = list(itertools.chain(param_self, param_other))
            
            
            m = Model(pdfs=pdfs, parameters=param, name=name, expression=expression)
            return m
        
        
        
    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, PdfBase):
            expression = "{} - self._pdfs['{}'][index]".format(self.expression, other.name)
            name = "{} - {}".format(self.name, other.name)
            m = Model(pdfs=[list(self._pdfs.values()) + other], parameters=list(self._parameters.values()), name=name, expression=expression)
            return m
        
        elif isinstance(other, Model):
            expression = "{} - {}".format(self.expression, other.expression)
            name = "{} - {}".format(self.name, other.name)
            pdfs_self = list(self._pdfs.values())
            pdfs_other = list(other._pdfs.values())
            pdfs = list(itertools.chain(pdfs_self, pdfs_other))
            param_self = list(self._parameters.values())
            param_other = list(other._parameters.values())
            param = list(itertools.chain(param_self, param_other))
            
            
            m = Model(pdfs=pdfs, parameters=param, name=name, expression=expression)
            return m
        
    def __rsub__(self, other):
        return self.__sub__(other)
    
    def __str__(self):
        lines = []
        lines.append(" Model: {}".format(self.name))
        lines.append(" Number of pdf: {}".format(len(self._pdfs.keys())))
        for key in self._pdfs.keys():
            lines.append(" - {}".format(key))
        lines.append(" Number of parameters: {}".format(len(self._parameters.keys())))
        for key, param in self._parameters.items():
            lines.append(" - {}, limits = ({},{}),  Is it Fixed? {}".format(key, param.limits[0], param.limits[1], param.fixed))
        return "\n".join(lines)
    
    
from .pdf import PdfBase
from .parameter import Parameter
