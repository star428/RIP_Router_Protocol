# coding=utf-8
from sim.api import *
from sim.basics import *
import time

class Hub (Entity):
  """ A simple hub -- floods all packets """

  def handle_rx (self, packet, port):
    """
    Just sends the packet back out of every port except the one it came
    in on.
    port为传入端口
    """
    all_port = list(range(self.get_port_count()))

    all_port.remove(port)
    self.send(packet, all_port)
    # 此时传入端口数的列表同样能使得send函数照常运行

    # self.send(packet, port, flood=True)

    #print "now the in port is :" + str(port)
    #print "now the hub is" + str(self)
    #print "now the all port num is : " + str(self.get_port_count())
    #print "now the all port is : " + str(all_port)
    #print "package source is : " + str(packet.src)
    #print "package det is : " + str(packet.dst)
    #print "-------------------------------"