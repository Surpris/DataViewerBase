#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from numpy import array, arange, zeros, meshgrid, outer
from cytoolz import identity, curry
from scipy.interpolate import RectBivariateSpline
try:
    from numba import jit
except ImportError:
    print("Module 'numba' is not imported!")
    jit = identity


@jit
def get_centers(edges):
    return (edges[1:]+edges[:-1])/2.0


@jit
def get_diffs(edges):
    return edges[1:]-edges[:-1]


class Hist:
    def __init__(self, hist=None, x_edges=None, y_edges=None):
        if hist is None:
            nx = len(x_edges) - 1
            ny = len(y_edges) - 1
            hist = zeros((nx, ny))
        self.__hist = array(hist, dtype='float64')
        nx, ny = self.hist.shape
        if x_edges is None:
            x_edges = arange(nx + 1)
        if y_edges is None:
            y_edges = arange(ny + 1)
        self.__x_edges = array(x_edges, dtype='float64')
        self.__y_edges = array(y_edges, dtype='float64')

        def fst(*arr):
            ret, *_ = arr
            return ret
        if (nx != fst(*self.x_edges.shape)-1) or (ny != fst(*self.y_edges.shape)-1):
            raise ValueError('The shapes of hist and edges do not match each others!')

    @property
    def copy(self):
        return Hist(self.hist, self.x_edges, self.y_edges)

    @property
    def hist(self):
        return self.__hist

    @hist.setter
    def hist(self, h):
        self.hist[:, :] = h

    @property
    def img(self):
        x, y = meshgrid(self.x_edges, self.y_edges, indexing='ij')
        return self.intensity(x, y)

    @img.setter
    def img(self, i):
        x, y = self.x_edges, self.y_edges
        spline = RectBivariateSpline(x, y, i)
        self.intensity = curry(spline, grid=False)

    @property
    def x_edges(self):
        return self.__x_edges

    @property
    def x_centers(self):
        return get_centers(self.x_edges)

    @property
    def x_diffs(self):
        return get_diffs(self.x_edges)

    @property
    def y_edges(self):
        return self.__y_edges

    @property
    def y_centers(self):
        return get_centers(self.y_edges)

    @property
    def y_diffs(self):
        return get_diffs(self.y_edges)

    @property
    def intensity(self):
        x, y = self.x_centers, self.y_centers
        dx, dy = self.x_diffs, self.y_diffs
        spline = RectBivariateSpline(x, y, self.hist/outer(dx, dy))
        return curry(spline, grid=False)

    @intensity.setter
    def intensity(self, i):
        x, y = meshgrid(self.x_centers, self.y_centers, indexing='ij')
        dx, dy = self.x_diffs, self.y_diffs
        self.hist = i(x, y) * outer(dx, dy)

    @property
    def meshed_xyz(self):
        return self.x_edges, self.y_edges, self.hist.T

    @property
    def meshed_yxz(self):
        return self.y_edges, self.x_edges, self.hist
