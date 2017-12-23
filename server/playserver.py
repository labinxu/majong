import json
class PlayerServ:
    def __init__(self, request,server):
        self.request = request
        self.server = server
        self.status = 'Unknown'
        self.name = 'Unknow'

    def do(self, jsondata):
        try:
            action = json.loads(jsondata)
            if  'data' in action.keys():
                getattr(self.server.action, action['a'])(self, action['data'])
            else:
                getattr(self.server.action, action['a'])(self)
        except Exception:
            print('[%s Received] %s' %(self.name, jsondata))

    def run(self):
        conn = self.request
        while True:
            # get action
            accept_data = str(conn.recv(1024), encoding='utf8')
            self.do(accept_data)
        conn.close()
