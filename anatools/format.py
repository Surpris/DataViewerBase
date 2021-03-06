#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from textwrap import dedent
from glob import iglob
from cytoolz import reduce, concat, map, curry, compose, memoize, identity
from numpy import fromiter
from h5py import File


class FermiReader:
    def __init__(self, *filenames, map=None):
        if map is None:
            map = {}
        globbed = concat(iglob(f) for f in filenames)
        self.__files = tuple(File(f, 'r') for f in globbed)
        self.__map = map
        self.__cache = {}
        print('Files below are loaded:')
        for f in self.files:
            print('    {}'.format(f))
        print('    Total {} files'.format(len(self.files)))

    def close(self):
        for f in self.files:
            f.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    @property
    def files(self):
        return self.__files

    def map(self, k):
        if k in self.__map:
            return self.__map[k]
        else:
            return k

    @property
    def cache(self):
        return self.__cache

    def __getitem__(self, key):
        i = key.find('.')
        if i == -1:
            return self[key+'.each_event']
        k, w = key[:i], key[i+1:]
        if w == 'each_file':
            return (f[self.map(k)].value for f in self.files)
        elif w == 'each_event':
            return concat(f[self.map(k)] for f in self.files)
        else:
            raise ValueError("Key '{}' is invalid!".format(key))


try:
    from dbpy import (read_hightagnumber as __read_hightagnumber,
                      read_taglist_byrun as __read_taglist_byrun,
                      read_syncdatalist_float)
    from stpy import StorageReader, StorageBuffer
    read_hightagnumber = curry(memoize(__read_hightagnumber))
    read_taglist_byrun = curry(memoize(__read_taglist_byrun))

    class _ReadonlyBuffer:
        def __init__(self, buffer):
            self.__buffer = buffer

        @property
        def data(self):
            return self.__buffer.read_det_data(0)

        @property
        def info(self):
            return self.__buffer.read_det_info(0)


    class StorageWrapper:
        def __init__(self, *runs, beamline, id):
            self.__reader = StorageReader(id, beamline, runs)
            self.__buffer = StorageBuffer(self.reader)
            self.__readonly = _ReadonlyBuffer(self.buffer)

        @property
        def reader(self):
            return self.__reader

        @property
        def buffer(self):
            return self.__buffer

        @property
        def readonly(self):
            return self.__readonly

        def __getitem__(self, tag):
            self.reader.collect(self.buffer, tag)
            return self.readonly


    def tags(beamline, runs):
        hi_tags = fromiter(map(read_hightagnumber(beamline), runs), 'int')
        if not hi_tags.all():
            raise ValueError('Not all the runs have a single high tag!')
        hi_tag = hi_tags[0]
        low_tags = concat(map(read_taglist_byrun(beamline), runs))
        return hi_tag, low_tags


    class SaclaReader:
        def __init__(self, *runs: int, beamline: int, **map):
            hi_tag, low_tags = tags(beamline, runs)
            self.__beamline = beamline
            self.__runs = fromiter(sorted(runs), 'int')
            self.__hi_tag = hi_tag
            self.__low_tags = fromiter(sorted(low_tags), 'int')
            self.__map = map
            self.__cache = {}

        @property
        def beamline(self):
            return self.__beamline

        @property
        def runs(self):
            return self.__runs

        @property
        def hi_tag(self):
            return self.__hi_tag

        @property
        def low_tags(self):
            return self.__low_tags

        @property
        def tags(self):
            return self.hi_tag, self.low_tags

        @property
        def ntags(self):
            return len(self.low_tags)

        @property
        def map(self):
            return self.__map

        @property
        def cache(self):
            return self.__cache

        def __getitem__(self, key: str) -> iter:
            if key not in self.map:
                raise ValueError(dedent(
                        """\
                        Key '{}' is invalid!
                        Valid keys: {}
                        """.format(key, reduce(lambda k1, k2: '{}, {}'.format(k1, k2),
                                               map(lambda k: "'{}'".format(k), self.map)))))
            ref = self.map[key]
            if 'api' not in ref:
                ref['api'] = 'dbpy'  # default api
            api = ref['api']

            # load reader
            if key not in self.cache:
                print("Loading '{}' reader...".format(key))
                if api not in ('dbpy', 'stpy'):
                    raise ValueError("Invalid api type '{}'!".format(api))
                if 'id' not in ref:
                    ref['id'] = key  # default id
                id = ref['id']
                if api == 'dbpy':
                    self.cache[key] = fromiter(
                            read_syncdatalist_float(id,
                                                    self.hi_tag,
                                                    tuple(map(int, self.low_tags))),
                            'float')
                if api == 'stpy':
                    self.cache[key] = StorageWrapper(*map(int, self.runs),
                                                     beamline=self.beamline,
                                                     id=id)
                if 'deco' not in ref:
                    ref['deco'] = identity  # default deco
                print('Loaded!')

            data = self.cache[key]
            deco = ref['deco'] if hasattr(ref['deco'], '__call__') else eval(ref['deco'])
            if api == 'dbpy':
                return map(deco, data)
            if api == 'stpy':
                return map(compose(deco, data.__getitem__), self.low_tags)
except ImportError:
    print("Modules 'dbpy', 'stpy' are not imported!")
    SaclaReader = None
