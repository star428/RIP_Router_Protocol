# Code Analysis

---

## api.py

- `create_timer`

```python
def create_timer (seconds, target, recurring = True, pass_self = False,args=(), kw={}):
```

> 作用为创建一个定时器，此时可以通过设置 seconds 来控制调用函数的时间，通过 target 来填入需要调用的函数的名字，使用该函数将返回一个实体，如果需要停止定时器对返回的实体使用<font color='df7861'>.cancel()</font>方法即可

- `Packet`

```python
class Packet (object):
  """
  作为所有包的父类，此后所有包都需要继承，
  包里面包含了源entity，目标entity，总长度和走过的实体名（下面解释）的 list，
  一般 src 为 NULL 时就自动填上当前发送的实体，dst 为空时如果路由器没有设置相关解决方案，
  可能会引起路由器错误

  """
  def __init__ (self, dst=NullAddress, src=NullAddress):

    self.src = src # 源实体（就是实体，不是实体名）注意（有name）
    self.dst = dst # 目标实体
    self.ttl = 20 # 总长度
    self.trace = [] # 走过的路径
    self.outer_color = hsv_to_rgb(rand(), rand()*.25+.1, rand()*.95+.5,.75)
    self.inner_color = [0,0,0,0]

  def __repr__ (self):
```

- `Entity`

```python
class Entity (object):
  """
  所有实体元件的基类（父类）比如交换机router，路由器switch，主机host等
  """

  @classmethod # 不使用self而是cls完成在调用函数后同时实例化，可以把cls当作类名使用
  def create (cls, name, *args, **kw):
    """
    创建一个实体，加入名字即可
    """
    return core.CreateEntity(name, cls, *args, **kw)

  def get_port_count (self):
    """
    返回该实体的端口数（此时是实际物理端口）
    """
    pass

  def handle_rx (self, packet, port):
    """
    当Entity实体收到一个packet时就会自动调用这个函数(core.py中有方法
    可以识别包来的端口)，所以将自动调用该函数，此时packet就是表示收到的包，
    port表示包来自的端口（物理）
    """
    pass

  def set_debug (self, *args):
    """
    将所有参数转换为此实体的调试消息。
    此次实验用不到该函数
    """
    pass

  def log (self, msg, *args, **kwargs):
    """
    格式化输出所用，实体调用该函数实际为输出某些信息(和printf作用差不多相同）
    实际使用见basics中
    """
    pass

  def send (self, packet, port=None, flood=False):
    """
    发送一个包给相对应的端口，port可以是端口号，也可以是端口号列表，如果使用了
    flood选项，那么就会发送到除port端口以外的所有端口
    """
    pass

  def remove (self):
    """
    将该实体移除，本实验用不到（如果使用图形化的话可能会在取消实体的时候调用这个
    函数
    """
    pass

  def __repr__ (self):
    return "<" + self.__class__.__name__ + " " + str(self.name) + ">"
```

- `HostRntity`

```python
class HostEntity (Entity):
"""
与Entity实体完全相同，只是简单的继承关系
"""
```

---

## basics.py

- `BasicHost`

```python
class BasicHost (HostEntity):
  """增添了ping功能的host实体类"""

  def ping (self, dst, data=None):
    """ 发送一个ping包(后面实体化)给目标 """
    self.send(Ping(dst, data=data), flood=True)

  def handle_rx (self, packet, port):
    """
    Returns Pings with a Pong.
    host接收到不同的包输出不同的反映（一般默认只有一个端口0），
    当收到包的目标entity为NULL时，简单丢弃这个包，
    当这个包的目的entity不是自己时，发出warn，
    当这个包的目的entity是自己同时是一个ping包时，输出相关信息，同时发送一个pong包给src
    当这个包的目的entity是自己同时是一个pong包时，输出相关信息
    """
    if packet.dst is NullAddress:
      # Silently drop messages not to anyone in particular
      return

    trace = ','.join((s.name for s in packet.trace))

    if packet.dst is not self:
      self.log("NOT FOR ME: %s %s" % (packet, trace), level="WARNING")
    else:
      self.log("rx: %s %s" % (packet, trace))
      if type(packet) is Ping:
        # Trace this path
        import core
        core.events.highlight_path([packet.src] + packet.trace)
        # Send a pong response
        self.send(Pong(packet), port)
```

- `Ping`

```python
class Ping (Packet):
  """继承自包类的ping包"""
  def __init__ (self, dst, data=None):
    Packet.__init__(self, dst=dst) # packet中src为NULL时自动填入当前发送的实体的地址
    self.data = data # 新增包中的data
    self.outer_color[3] = 1 # 调整颜色所用
    self.inner_color = [1,1,1,1] # 调整颜色所用

  def __repr__ (self):
    """
    控制直接可以print ping类
    """
    d = self.data
    if d is not None:
      d = ': ' + str(d)
    else:
      d = ''
    return "<Ping %s->%s ttl:%i%s>" % (self.src.name, self.dst.name, self.ttl, d)

```

- `Pong`

```python
class Pong (Packet):
  """
  继承自包类的pong包，是对ping包的回应，origianl为ping包，解析ping包中的相关信息，
  然后再将ping包的src加入到pong包的dst中
  """
  def __init__ (self, original):
    Packet.__init__(self, dst=original.src)
    self.original = original

    # 颜色设置
    self.outer_color = original.inner_color
    self.inner_color = original.outer_color

  def __repr__ (self):
    """
    控制直接可以print pong类
    """
    return "<Pong " + str(self.original) + ">"
```

- `DiscoveryPacket`

```python
class DiscoveryPacket (Packet):
    """
    继承自packet的discoverypacket包
    实体建立时发送该包的机制如下：
    当拓扑图连好后，实体会将包的dst设置为NULL，同时所有已经建立的实体会向自己所有已连接entity的端口发送discovery包，
    实体会自动检测端口所连接线的latency同时加入发送往该端口的discovery包的latency中
    """
    def __init__(self, src, latency):
        Packet.__init__(self, src=src)
        self.latency = latency
        self.is_link_up = (latency != None and latency != float("inf"))

    def __repr__ (self):
        return "<%s from %s->%s, %s, %s>" % (self.__class__.__name__,
                                 self.src.name if self.src else None,
                                 self.dst.name if self.dst else None,
                                 self.latency,
                                 self.is_link_up)
```

- `RoutingUpdate`

```python
class RoutingUpdate (Packet):
    """
    继承自packet的路由用包，用在路由器构建路由表的包
    """

    def __init__(self):
        Packet.__init__(self)# 没有dst，src打上发送的entity的地址
        self.paths = {} # path可以当作要向邻居发送的路由矢量值，也就是记录该路由器到router/host的估计值

    def add_destination(self, dest, distance):
        """
        加入新节点和估计的延迟
        """
        self.paths[dest] = distance

    def get_distance(self, dest):
        """
        获取到某个节点的估计延迟（某个router接收到该来自邻居的包是使用）
        """
        return self.paths[dest]

    def all_dests(self):
        """
        获取包中的所有节点
        """
        return self.paths.keys()

    def str_routing_table(self):
        """
        获取包中的路由矢量值
        """
        return str(self.paths)
```
