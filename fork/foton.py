# $Id: foton.py 7372 2015-05-13 20:57:23Z james.batch@LIGO.ORG $
# Python module for foton scripting, allows generation of filter coefficients
# from foton design strings, and parsing of foton filter files. 
# Author: Christopher Wipf, LIGO - Massachusetts Institute of Technology
# May 6, 2014

import sys, os
from numpy import poly1d
from scipy.signal import lfilter, lfiltic

import ROOT

from array import array

ROOT.gInterpreter.AddIncludePath("/usr/include/gds") 
ROOT.gSystem.AddDynamicPath("/usr/lib") 
ROOT.gSystem.Load("libRdmtsigp")
ROOT.gSystem.Load("libRgdsplot")


__docformat__ = 'restructuredtext'
__all__ = ['FilterFile', 'FilterDesign', 'iir2zpk', 'iir2z', 'iir2poly', 'iir2direct', 'Filter', 'serialize_filters']

class FilterFile(object):
    """
    Read and edit CDS filter files.

    Example:
      >>> from ligocds.foton import FilterFile
      >>> filterfile = FilterFile('/cvs/cds/mit/chans/M1PDE.txt')
      >>> filterfile['LSC_CARM'][0].rate
      65536.0
      >>> filterfile['LSC_CARM']['PHlead'].name
      'PHlead'

      """
    def __init__(self, filename=None):
        self.ff = ROOT.filterwiz.FilterFile()
        self.filename = filename
        if filename:
            self.read(filename)

    def __getitem__(self, key):
        lookup = lambda: self.ff.find(key)
        # The subtlety here is that find() returns a C pointer that
        # can be invalidated when modules are added or removed -- so a
        # 'Module' needs to carry around this lookup function to
        # retrieve a valid pointer.
        try:
            item = lookup()
        except:
            raise KeyError, key
        if item == None:
            raise KeyError, key
        return Module(lookup)

    def __setitem__(self, key, val):
        if not isinstance(val, Module):
            raise ValueError, val
        self.ff.add(key, val.rate)
        for sec in val:
            self[key][sec.index] = sec

    def __delitem__(self, key):
        self.ff.remove(key)

    def __contains__(self, key):
        try:
            item = self.ff.find(key)
        except:
            return False
        if item == None:
            return False
        else:
            return True

    def __iter__(self):
        for key in self.keys():
            yield key

    def keys(self):
        return [fm.getName() for fm in self.ff.modules()]

    def items(self):
        return [(key, self[key]) for key in self.keys()]

    def refresh(self):
        return self.ff.update()

    def valid(self):
        val = True
        for name, fm in self.items():
            for sec in fm:
                if not sec.valid():
                    val = False
                    print >>sys.stderr, name + '[' + str(sec.index) + ']',
                    print >>sys.stderr, 'invalid'
        return val

    def read(self, filename):
        "Load filter file"
        self.filename = os.path.abspath(filename)
        self.ff.read(self.filename)

    def write(self, *args):
        "Save filter file."
        if not self.filename:
            raise Exception("undefined filename")
        if not (self.valid() and self.refresh() and self.valid()):
            raise Exception("problem with the filters")
        if len(args) == 0:
            self.ff.write(self.filename)
        else:
            self.ff.write(*args)

class Module(object):
    def __init__(self, lookup):
        self._lookup = lookup

    fm = property(lambda self: self._lookup(), None)
    name = property(lambda self: self.fm.getName(),
                    lambda self, val: self.fm.setName(val))
    rate = property(lambda self: self.fm.getFSample(),
                    lambda self, val: self.fm.setFSample(val))
        
    def __len__(self):
        return ROOT.filterwiz.kMaxFilterSections

    def __getitem__(self, key):
        if isinstance(key, basestring):
            for n in range(len(self)):
                item = self.fm[n]
                if item.getName() == key:
                    return Section(self._lookup, n)
            raise KeyError, key
        elif key in range(len(self)):
            return Section(self._lookup, key)
        else:
            raise KeyError, key

    def __setitem__(self, key, val):
        self[key].copyfrom(val)
        if isinstance(key, basestring):
            self[key].name = key

    def __contains__(self, key):
        try:
            item = self[key]
            return True
        except:
            return False

    def __iter__(self):
        for n in range(len(self)):
            yield self[n]

class Section(object):
    def __init__(self, lookup_fm, key):
        self._lookup_fm = lookup_fm
        self._key = key

    sec = property(lambda self: self._lookup_fm()[self._key], None)
    index = property(lambda self: self.sec.getIndex(),
                     lambda self, val: self.sec.setIndex(val))
    name = property(lambda self: self.sec.getName(),
                    lambda self, val: self.sec.setName(val))
    design = property(lambda self: self.sec.getDesign(),
                      lambda self, val: self._set_design(val))
    filt = property(lambda self: self.sec.filter(), None)
    order = property(lambda self: ROOT.iirorder(self.filt.get()), None)
    input_switch = property(lambda self: self.sec.getInputSwitch(),
                            lambda self, val: self.sec.setInputSwitch(val))
    output_switch = property(lambda self: self.sec.getOutputSwitch(),
                             lambda self, val: self.sec.setOutputSwitch(val))
    ramp = property(lambda self: self.sec.getRamp(),
                    lambda self, val: self.sec.setRamp(val))
    tolerance = property(lambda self: self.sec.getTolerance(),
                         lambda self, val: self.sec.setTolerance(val))
    timeout = property(lambda self: self.sec.getTimeout(),
                         lambda self, val: self.sec.setTimeout(val))
    header = property(lambda self: self.sec.getHeader(),
                      lambda self, val: self.sec.setHeader(val))

    def _set_design(self, newdesign):
        self.sec.setDesign(newdesign)
        self.refresh()

    def empty(self):
        return self.sec.empty()

    def check(self):
        return self.sec.check()

    def valid(self):
        return self.sec.valid()

    def refresh(self):
        return self.sec.update()

    def add(self, cmd):
        return self.sec.add(cmd)

    def copyfrom(self, src):
        self.name = src.name
        self.design = src.design
        self.input_switch = src.input_switch
        self.output_switch = src.output_switch
        self.ramp = src.ramp
        self.tolerance = src.tolerance
        self.timeout = src.timeout

class FilterDesign(object):
    def __init__(self, filt, rate=None):
        self.filt = filt
        if isinstance(filt, basestring):
            if rate is None:
                raise ValueError
            self.filt = ROOT.FilterDesign(filt, rate)

    string = property(lambda self: self.filt.getFilterSpec(), None)
    design = property(lambda self: self.filt.getFilterSpec(), None)
    rate = property(lambda self: self.filt.getFSample(), None)

def iir2zpk(filt, plane='s', prewarp=True):
    """Returns the zeros and poles of an IIR filter. 
    The returned string has the format "zpk(...)", if the plane is
    "s", "n" or "f". It is of the form "rpoly(...)", if the plane is
    "p".
    """
    try:
        arg = filt.filt.get()
    except AttributeError:
        arg = filt.get()
    zpk = ROOT.string()
    ROOT.iir2zpk(arg, zpk, plane, prewarp)
    return zpk

def iir2z(filt, format='s'):
    """Returns the a's and b's of an IIR filter.
    The returned a's and b's are grouped in zecond order sections.
    The first returned coeffcient is the overall gain. The following
    coeffcients come in groups of 4. If the format is 's' (standard),
    the order is b1, b2, a1, b2. If the format is 'o' (online), the
    order is a1, a2, b1, b2. The returned length is always of the
    for nba = 1 + 4 * (number of second order sections). A second order
    section is defined as:
    $$H(z)=\\frac{b0+b1 z^{-1}+b2 z^{-2}}{1+a1 z^{-1}+a2 z^{-2}}$$
    """
    try:
        arg = filt.filt.get()
    except AttributeError:
        arg = filt.get()
    nsos = ROOT.iirsoscount(arg)
    nba = ROOT.Long(0)
    ba = array('d', range(1 + 4*nsos))
    ROOT.iir2z(arg, nba, ba)
    return [ba[n] for n in range(nba)]

def iir2poly(filt, unwarp=True):
    """Returns the rational polynomial of an IIR filter. (numer, denom, gain)

       A rational polynomial in s is specified by the polynomial 
       coefficients in the numerator and the denominator in descending 
       order of s. 

       The formula is
       $$zpk(s) = k \\frac{a_n s^{n_z} + a_{n-1} s^{n_z - 1} \\cdots}
                         {b_n s^{n_p} + b_{n-1} s^{n_p - 1} \\cdots}$$
       where $a_n$, $a_{n-1}$,..., $a_0$ are the coeffciients of the 
       polynomial in the numerator and $b_n$, $b_{n-1}$,..., $b_0$ are
       the coefficients of the polynomial in the denominator.
       The polynomial coefficients have to be real.

       N.B. coefficients seem to be returned in descending order
    """
    try:
        arg = filt.filt.get()
    except AttributeError:
        arg = filt.get()
    n_array = array('d', range(ROOT.iirzerocount(arg) + 1))
    nnumer = ROOT.Long(0)
    d_array = array('d', range(ROOT.iirpolecount(arg) + 1))
    ndenom = ROOT.Long(0)
    gain = ROOT.Double(0)
    ROOT.iir2poly(arg, nnumer, n_array, ndenom, d_array, gain, unwarp)
    numer = [n_array[n] for n in range(nnumer)]
    denom = [d_array[n] for n in range(ndenom)]
    return numer, denom, gain+0
    
def iir2direct(filt):
    """Returns the direct form of an IIR filter.

       The direct form can be written as
       $$H(z)=\Sum_{k=0}^{nb}b_k z^{-k} / (1-\Sum_{k=1}^{na}a_k z^{-k})$$

       Cascaded second order sections are formed by finding the roots
       of the direct form. The returned coefficients are $b_0$, $b_1$,...,
       $b_{nb}$ for the numerator and $a_1$, $a_2$,..., $a_{na}$ for the
       denominator. $nb$ is the number of b coefficients minus 1, whereas
       $na$ is exactly the number of a coefficients since $a_0$ is always 1
       and omitted from the list.

       Avoid the direct form since even fairly simple filters will run into
       precision problems.

       N.B. coefficients seem to be returned in ascending order
    """
    try:
        arg = filt.filt.get()
    except AttributeError:
        arg = filt.get()
    soscount = ROOT.iirsoscount(arg)
    b_array = array('d', range(2*soscount + 1))
    nb = ROOT.Long(0)
    a_array = array('d', range(2*soscount))
    na = ROOT.Long(0)
    ROOT.iir2direct(arg, nb, b_array, na, a_array)
    b = [b_array[n] for n in range(nb+1)]
    a = [a_array[n] for n in range(na)]
    return b, a
    
def serialize_filters(filter_list):
    # convert filters to direct form
    filter_list = [iir2direct(filt) for filt in filter_list]
    # convert direct form coeffs to poly1d polynomials
    # ascending order -> descending order (::-1 reverses coeffs)
    # denom coeffs from iir2direct: constant term is equal to 1 and is omitted
    # denom coeffs from iir2direct: sign is flipped
    direct_b = [poly1d(arg[0][::-1]) for arg in filter_list]
    direct_a = [-1 * poly1d(arg[1][::-1] + [-1.0]) for arg in filter_list]
    # form sum of direct form expressions:
    # b1/a1 + b2/a2 = (b1*a2 + b2*a1)/(a1*a2)
    serial_b = poly1d([0])
    serial_a = poly1d([1])
    for n in range(len(filter_list)):
        # numerator term is multiplied by product of all a's except a_n
        a_prod = poly1d([1])
        for m in range(len(filter_list)):
            if m != n:
                a_prod *= direct_a[m]
        serial_b += direct_b[n] * a_prod
        serial_a *= direct_a[n]
    # output new filter design
    # descending order -> ascending order
    # denom coeffs: omit constant term and flip sign again
    serial_b = serial_b.c[::-1]
    serial_b = [str(c) for c in serial_b]
    serial_b = '[' + ';'.join(serial_b) + ']'
    serial_a = serial_a.c[:-1][::-1]
    serial_a = [str(-c) for c in serial_a]
    serial_a = '[' + ';'.join(serial_a) + ']'
    return 'direct(' + ','.join([serial_b, serial_a]) + ')'

class Filter(object):
    def __init__(self, design, ic=None):
        self.design = design
        self.ic = ic
        self.sections = []

        coeffs = iir2z(design)
        gain = coeffs[0]
        coeffs_by_sos = [coeffs[n:n+4] for n in xrange(1, len(coeffs)-1, 4)]
        if coeffs_by_sos:
            (b1, b2, a1, a2) = coeffs_by_sos[0]
            self.sections.append(((gain, gain*b1, gain*b2), (1.0, a1, a2)))
        for (b1, b2, a1, a2) in coeffs_by_sos[1:]:
            self.sections.append(((1.0, b1, b2), (1.0, a1, a2)))

        if ic is None:
            self.clear_history()

    def clear_history(self):
        self.ic = [lfiltic(b, a, (0.0,)) for (b, a) in self.sections]

    def apply(self, data):
        newic = []
        out = data
        for (b, a), ic in zip(self.sections, self.ic):
            out, ic = lfilter(b, a, out, zi=ic)
            newic.append(ic)
        self.ic = newic
        return out
