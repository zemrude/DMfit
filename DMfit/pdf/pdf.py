import abc
from typing import Dict, List, Optional, Iterable, Mapping, Any, Tuple, Union
import numpy as np
import collections
import itertools 
   

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
        
        

    
    
    
    def __str__(self):
        lines = []
        lines.append(" Name: {}".format(str(self.name)))
        lines.append(" Value: {}".format(str(self._value)))
        lines.append(" Limits: ({}, {})".format(str(self.limits[0]), str(self.limits[1])))
        lines.append(" Is fixed? {}".format(self.fixed))
        return "\n".join(lines)

    
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
            expression = "{} + self._pdfs['{}'][index]".format(other, self.name)
            name = "{}+{}".format(other, self.name)
            m = Model(pdfs = [self], name=name, expression=expression)
            return m

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