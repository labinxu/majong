import multiprocessing
import time


class TestMultiAccess():
    def __init__(self):
        mgr =  multiprocessing.Manager()
        self.players = []#mgr.list()
        lock = multiprocessing.Lock()
        multiprocessing.Process(target=self.worker, args=(self.players,lock)).start()
        multiprocessing.Process(target=self.consumer, args=(self.players, lock)).start()
        while True:
            time.sleep(1)

    def consumer(self, players, lock):
        while True:
            time.sleep(1)
            for i in range(100):
                lock.acquire()
                players.append(i)
                lock.release()

    def worker(self, players, lock):
        while True:
            time.sleep(1)
            lock.acquire()
            print(len(players))
            print(players)
            lock.release()

t = TestMultiAccess()



def producter(ns, e):
    ns['1']='a'
    e.set()

def consumer(ns, e):
    e.wait()
    print(ns)

if __name__ == '__main___':

    e = multiprocessing.Event()
    p = multiprocessing.Process(target=producter, args=(nms,e))

    p1 = multiprocessing.Process(target=consumer, args=(nms,e))
    p.start()
    p1.start()
    p.join()
    p1.join()
    

