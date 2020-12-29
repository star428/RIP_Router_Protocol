#!/usr/bin/env python
# encoding: utf-8
"""
@author: star428
@contact: yewang863@gmail.com
@software: garner
@file: dv_router_new.py
@time: 2020/12/29 下午10:57
@desc:
"""

# coding=utf-8
from sim.api import *
from sim.basics import *

MAX_LATENCY = 1024


class DVRouter_New(Entity):

    def __init__(self):
        self.neibor_table = {}
        # 记录与该路由器相连的实体名字（包含路由器和主机）
        # 格式为 实体 ：[出口端口，延迟]
        self.router_table = {self: [NullAddress, 0]}  # 路由表判断路由
        #  比转发表多几项用来判断转发的端口
        # 格式为 实体 ： [出口端口，延迟]

        self.count = 4 # 最多根新8次即可
        self.send_RoutingUpdate_packet()

    def handle_rx(self, packet, port):
        if len(packet.trace) > 16:
            pass
        else:
            if type(packet) is DiscoveryPacket:
                source_port = port
                source_entity = packet.src

                self.neibor_table[source_entity] = [source_port, packet.latency]
                self.router_table[source_entity] = [source_port, packet.latency]

                # self.package_analyse(packet)

            if type(packet) is RoutingUpdate:

                the_neibor = packet.src
                the_neibor_port = self.neibor_table[the_neibor][0]
                the_neibor_latency = self.neibor_table[the_neibor][1]

                the_RoutingUpdate_table = packet.paths

                # 加入新的节点
                for new_point in the_RoutingUpdate_table.keys():
                    if not (new_point in self.router_table.keys()):
                        self.router_table[new_point] = [0, MAX_LATENCY]

                for k in list(self.router_table.keys()):
                    if k in list(the_RoutingUpdate_table.keys()):
                        new_latency = the_RoutingUpdate_table[k] + \
                                      the_neibor_latency
                        if new_latency < self.router_table[k][1]:
                            self.router_table[k] = [the_neibor_port,
                                                    new_latency]

                if self.count == 0:
                    print self.name + " is ok!"
                    self.count -= 1
                else:
                    if self.count == -1:
                        pass
                    else:
                        self.count -= 1

                # self.package_analyse(packet)

            if type(packet) is Ping or type(packet) is Pong:
                out_port = \
                    self.router_table[packet.dst][0]
                self.send(packet, out_port)

    def send_RoutingUpdate_packet(self):
        self.timer_function = \
            create_timer(1, self.RoutingUpdate_packet)

    def RoutingUpdate_packet(self):
        packet = RoutingUpdate()
        for entity, latency in self.router_table.items():
            packet.add_destination(entity, latency[1])

        self.send(packet, flood=True)

    def package_analyse(self, packet):
        print "now the router is : " + str(self.name)
        print "the type of packet is : " + str(type(packet))
        print "the neibor_table is : " + str(self.neibor_table)
        print "the router_table is : " + str(self.router_table)
        # print NullAddress
        print "-----------------------------------------"
