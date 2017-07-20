#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from textwrap import dedent
from cytoolz import identity
from numpy import sin, cos, matrix, array, zeros, tensordot
from scipy.optimize import fmin
from .coordinate import convert_xy2rth
try:
    from numba import jit
except ImportError:
    print("Module 'numba' is not imported!")
    jit = identity


@jit
def get_rotation_mat(th):
    return matrix(((cos(th), -sin(th)), (sin(th), cos(th))))


@jit
def __get_squeeze_mat(k):
    return matrix(((k, 0.0), (0.0, 1.0/k)))


@jit
def get_squeeze_mat(k, th=0.0):
    rot = get_rotation_mat(th)
    squ = __get_squeeze_mat(k)
    return rot.I.dot(squ).dot(rot)


class LinearTransformer:
    def __init__(self, mat, o=None):
        self.__mat = matrix(mat, dtype='float64')
        n, n1 = self.mat.shape
        if n != n1:
            raise ValueError('The matrix must be square!')
        if o is None:
            o = zeros(n)
        self.__o = array(o, dtype='float64')
        n2, *_ = self.o.shape
        if n != n2:
            raise ValueError(dedent(
                    """\
                    The shapes of hist and edges do not match each others!"""))

    @property
    def mat(self):
        return array(self.__mat)

    @property
    def inv(self):
        return array(self.__mat.I)

    @property
    def o(self):
        return self.__o

    def transform(self, *x):
        return tensordot(self.mat, tuple(x1-x0 for x0, x1 in zip(self.o, x)), axes=((1,), (0,)))

    def invert(self, *x):
        return (x1+x0 for x0, x1 in zip(self.o, tensordot(self.inv, x, axes=((1,), (0,)))))

    def __call__(self, *args):
        return self.transform(*args)

    @property
    def transformer(self):
        return self.transform

    @property
    def inverter(self):
        return self.invert

    @property
    def operators(self):
        return self.transformer, self.inverter


# high level objects
class SqueezeTransformer(LinearTransformer):
    def __init__(self, k=1.0, th=0.0, x0=0.0, y0=0.0):
        mat = get_squeeze_mat(k, th)
        super().__init__(mat, o=(x0, y0))


def opt_squ_pars(*smp, **init):
    """
    Find parameters to make the sample dots symmetric
    Below parameters will be searched:
        k: k parameter to squeeze the dots
        th: theta to rotate the dots
        x0, y0: center of the dots
    """
    def wrap(*arr):
        k, th, x0, y0 = arr
        return dict(k=k, th=th, x0=x0, y0=y0)

    def unwrap(**d):
        return d['k'], d['th'], d['x0'], d['y0']

    def norm(pars):
        transformer = SqueezeTransformer(**wrap(*pars))
        r, _ = convert_xy2rth(*transformer(*smp))
        return r.std()
    print('Optimizing parameters of squeeze transformation...')
    ret = fmin(norm, unwrap(**init))
    print(dedent("""\
                 Optimized parameters are...
                 k: {k}
                 theta: {th}
                 center of x: {x0}
                 center of y: {y0}""".format(**wrap(*ret))))
    return wrap(*ret)
