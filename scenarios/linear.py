# coding=utf-8
import sim
from sim.core import CreateEntity, topoOf
from sim.basics import BasicHost
from hub import Hub
import sim.topo as topo

def create (switch_type = Hub, host_type = BasicHost, n = 2):
    """
    Creates a really simple topology like:
    s1 -- s2 -- .. -- sn
     |     |           |
    h1    h2          hn
    n defaults to 2.
    """

    switches = []
    for i in range(1, n+1):
      s = switch_type.create('s' + str(i))
      switches.append(s)
      h = host_type.create('h' + str(i))
      topo.link(s, h, 2)
      # s.linkTo(h)

    # Connect the switches
    prev = switches[0]
    for s in switches[1:]:
      # prev.linkTo(s)
      # link is the same as linkto
      topo.link(prev, s, 1) # 这里设置每根线缆的latery为2
      prev = s
