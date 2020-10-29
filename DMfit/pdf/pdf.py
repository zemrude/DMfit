import abc
from typing import Dict, List, Optional, Iterable, Mapping, Any, Tuple, Union
import numpy as np
import collections

   
from .parameter import Parameter    
    
class PdfBase(abc.ABC):
    """PDF base class"""

    def __init__(self, frequencies = None, errors2 = None, **kwargs):
        
        if frequencies is not None:
            frequencies = np.asarray(frequencies)
            self.frequencies = frequencies
           
        if errors2 is not None:
            errors2 = np.asarray(errors2)
            self.errors2 = errors2
        
       
        self._meta_data = kwargs.copy()
     
            
    def __getitem__(self, index: int):
        return self.frequencies[index]
        
    @property
    def meta_data(self) -> dict:
        """A dictionary of non-numerical information about the pdf.
        """
        return self._meta_data
        
    
    @property
    def name(self) -> Optional[str]:
        """Name of the Pdf (stored in meta-data)."""
        return self._meta_data.get("name", None)
    
    @name.setter
    def name(self, value: str):
        """Name of the Pdf
        """
        self._meta_data["name"] = str(value)
        
    @property
    def frequencies(self):
        try:
            return self._frequencies
        except AttributeError as e:
            raise AttributeError(str(e), "Frequencies not set yet!")
        
    @frequencies.setter
    def frequencies(self, frequencies: np.ndarray) -> None:
        if np.any(frequencies < 0):
            raise ValueError("Cannot have negative values in the pdf.")
        elif not np.isclose(np.sum(frequencies),1.):
            raise ValueError("PDF is not normalized!")
            
        self._frequencies = frequencies
        
        
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
        
        self._errors2 = errors2
        
    @property   
    def nbins(self) -> int:
        """Number of bins of the pdf"""
        return len(self._frequencies)
    
    def __mul__(self, other):
        """If we multiply by a float or a int, the method returns simply the frequencies multiplied """
        if isinstance(other, int) or isinstance(other, float):
            frequencies = other * self._frequencies
            return frequencies
        
        elif isinstance(other, Parameter):
            expression = "self._parameters['{}'].value*self._pdfs['{}'][index]".format(other.name, self.name)
            name = "{}*{}".format(other.name, self.name)
            m = Model(pdfs = [self], parameters=[other], name=name, expression=expression)
            return m
    def __rmul__(self, other):
        return self.__mul__(other)

    def __add__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            frequencies = other + self._frequencies
            return frequencies

        elif isinstance(other, Parameter):
            expression = "self._parameters['{}'].value + self._pdfs['{}'][index]".format(other.name, self.name)
            name = "{}+{}".format(other.name, self.name)
            m = Model(pdfs = [self], parameters=[other], name=name, expression=expression)
            return m
        elif isinstance(other, PdfBase):
            expression = "self._pdfs['{}'][index] + self._pdfs['{}'][index]".format(other.name, self.name)
            name = "{}+{}".format(other.name, self.name)
            m = Model(pdfs = [self], parameters=[other], name=name, expression=expression)
            return m
            
    def __rmul__(self, other):
        return self.__mul__(other)
    def __radd__(self, other):
        return self.__add__(other)
    
    
    
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
