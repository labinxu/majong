

class NetCmd(object):
    def __init__(self):
        self.cmd = None
    def _pack(self,**kwags):
        pass

    def pack(self):
        return self._pack()


class Ready(NetCmd):
    def __init__(self):
        self.cmd = 'ready'
