#!/usr/bin/env python
# encoding: utf-8
"""
@author: star428
@contact: yewang863@gmail.com
@software: garner
@file: my_topo.py
@time: 2020/12/9 下午3:12
@desc:
"""
import sim
from sim.core import CreateEntity, topoOf
from sim.basics import BasicHost
from hub import Hub
import sim.topo as topo


def create(switch_type=Hub, host_type=BasicHost):
    """
    Creates a topology with loops that looks like:
             h2
             |
             B
          /  |  \
    h1 - A   |   D - h4
          \  |  /
             C
             |
             h3
    """

    a = switch_type.create('a')
    b = switch_type.create('b')
    c = switch_type.create('c')
    d = switch_type.create('d')

    h1 = host_type.create('h1')
    h2 = host_type.create('h2')
    h3 = host_type.create('h3')
    h4 = host_type.create('h4')

    topo.link(h1, a, 1)
    topo.link(h2, b, 1)
    topo.link(h3, c, 1)
    topo.link(h4, d, 1)

    topo.link(a, b, 2)
    topo.link(a, c, 7)
    topo.link(b, c, 1)
    topo.link(b, d, 3)
    topo.link(c, d, 1)
