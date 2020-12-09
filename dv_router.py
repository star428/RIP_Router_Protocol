# coding=utf-8
from sim.api import *
from sim.basics import *
from sim.topo import *

'''
Create your distance vector router in this file.
'''

MAX_LATENCY = 1024

all_router_list = []  # 打印用


class DVRouter(Entity):
    def __init__(self):
        # Add your code here!
        self.neibor_table = {}
        # 记录与该路由器相连的实体名字（包含路由器和主机）
        # 格式为 实体名 ：[出口端口，延迟]
        self.router_table = {}  # 路由表判断路由
        #  比转发表多几项用来判断转发的端口
        # 格式为 实体名 ： [出口端口，延迟]

        self.forwarding_table = {}  # 转发表转发当前值
        # 格式为 实体名 ： 延迟

        self.send_RoutingUpdate_packet()
        self.count = 1

    def handle_rx(self, packet, port):
        # Add your code here!
        # raise NotImplementedError
        if len(packet.trace) > 16:  # 当包的转发条数大于16条时，直接忽视这个包
            pass
        else:
            neibor_len = len(self.neibor_table)
            port_len = len(topoOf(self).get_ports())

            # 下代码为求第一个泛洪的discoverpacket所能增加的表中的项
            # 这个泛洪是每一个实体都会发，所以很好能建立相关表项，虽然他们其中的值都是最大值
            if type(packet) is DiscoveryPacket:
                source_entity = packet.src  # 发送这个包的源实体
                ports = topoOf(self).get_ports()  # 这个路由器所有的端口列表
                source_port = port  # 从哪个端口发来的这个包
                for p in ports:  # p就是每一个邻居的表示
                    # [('s1', 0, 'h1', 0), ('s1', 1, 's2', 1)]
                    # 就表示s1有两个邻居， 0端口连h1, 1端口连s2
                    if p[1] == source_port and p[2] == source_entity.name and \
                            neibor_len < port_len:
                        # 用来增加邻居表中的值
                        self.neibor_table[p[2]] = [p[1], packet.latency]
                # 由于每个实体都会发包，包的source指向自己，所以接受所有包的source name
                # 就是接受所有的实体
                if not (packet.src.name in self.router_table.keys()):
                    if packet.src.name == self.name:
                        self.router_table[packet.src.name] = [0, 0]
                    else:
                        self.router_table[packet.src.name] = [0, MAX_LATENCY]
                    # 此时设置默认端口为0,最大延迟为1024

                # 同理设置发送表，使之拥有所有的实体
                if not (packet.src.name in self.forwarding_table.keys()):
                    if packet.src.name == self.name:
                        self.forwarding_table[packet.src.name] = 0
                    else:
                        self.forwarding_table[packet.src.name] = MAX_LATENCY
                    # 增加初始的路由表，全部为最大延迟

                if neibor_len == port_len:  # 若找到所有邻居后对相应的路由表和转发表做相关更改
                    # 使之具有初值
                    neibors = list(self.neibor_table.keys())
                    for neibor in neibors:
                        if neibor in self.router_table.keys():
                            self.router_table[neibor] = \
                                self.neibor_table[neibor]

                        if neibor in self.forwarding_table.keys():
                            self.forwarding_table[neibor] = \
                                self.neibor_table[neibor][1]
                self.send(packet, port, flood=True)
                # self.discovery_packet_analyse(packet, port)

                # 用来确定从邻居收到的转发表同时更新自己的路由表和转发表
            if type(packet) is RoutingUpdate:
                # print "this packet is RoutingUpdate!!!"
                # print "the routingupdate source is : " + str(packet.src)
                the_neibor = packet.src
                the_neibor_port = self.neibor_table[the_neibor.name][0]
                the_neibor_latency = self.neibor_table[the_neibor.name][1]
                the_RoutingUpdate_table = packet.paths  # 就是邻居给的forwarding——table

                for k in list(self.router_table.keys()):
                    if k in list(the_RoutingUpdate_table.keys()):
                        new_latency = the_RoutingUpdate_table[k] + \
                                      the_neibor_latency
                        if new_latency < self.router_table[k][1]:
                            self.router_table[k] = [the_neibor_port,
                                                    new_latency]
                            self.forwarding_table[k] = new_latency

                # self.routing_update_packet_analyse()
                isOk = True
                for k in list(self.router_table.keys()):
                    if self.router_table[k][1] == MAX_LATENCY:
                        isOk = False

                if isOk:
                    if self.count == 1:
                        print str(self.name) + " is ok!"
                        # print self.router_table
                        self.count -= 1
                        # 为了输出而已，count只是为了输出一次而设置的变量

            # 解决来的包是ping或者pong包
            if type(packet) is Ping or type(packet) is Pong:
                if not (self.count == 0):
                    pass
                else:
                    packet_dst_name = packet.dst.name
                    out_port = \
                        self.router_table[packet_dst_name][0]
                    self.send(packet, out_port)

    # 设定1秒1发
    def send_RoutingUpdate_packet(self):
        self.timer_function = \
            create_timer(1, self.RoutingUpdate_packet)

    # 给自己所有的邻居发
    def RoutingUpdate_packet(self):
        packet = RoutingUpdate()
        packet.paths = self.forwarding_table

        self.send(packet, flood=True)

    # 输出测试可以试试，将上面我打过注销的#注销即可
    def routing_update_packet_analyse(self):
        print "-------------------------------"
        print str(self.name) + " changed router table is : " + \
              str(self.router_table)
        print "-------------------------------"

    # 输出测试，将上面的注销大小即可
    def discovery_packet_analyse(self, packet, port):
        print "the DVrouter source port is : " + str(port)
        print "now the router is : " + str(self.name)
        print "package source is : " + str(packet.src.name)
        print "package det is : " + str(packet.dst.name)
        show_ports(self)  # 展示当前的端口链接
        print "the type of packet is : " + str(type(packet))
        print "the latency is : " + str(packet.latency)
        print "the neibor_table is : " + str(self.neibor_table)
        print "the router_table is : " + str(self.router_table)
        print "the forwarding_table is : " + str(self.forwarding_table)

        ports = topoOf(self).get_ports()
        # [('s1', 0, 'h1', 0), ('s1', 1, 's2', 1)]
        # 返回该路由和其他实体的链接，显示的是名字
        # 而ping是src是实体而不是实体名
        # create_timer(10,print_hello) # 能保证每10秒调用该代码 **
        print "-------------------------------"
        # 启示状态时建立就会发discover包，然后我们可以通过
        # discover包来测延迟，该路由有几个邻居可以通过函数
        # 调用获得


# 没啥用的函数，或许有大用处？？？-----》可以完美输出hello的用处
def print_hello():
    print "hello!!!!!!!!"
