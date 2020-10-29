import abc
from typing import Dict, List, Optional, Iterable, Mapping, Any, Tuple, Union
import numpy as np
   
    
    
    
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
