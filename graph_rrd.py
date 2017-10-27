#!/usr/bin/env python
# encoding: utf-8

import binascii
import md5
import sys

class HashRing(object):
    def __init__(self, nodes=None, replicas=20):
        """Manages a hash ring.
        `nodes` is a list of objects that have a proper __str__ representation.
        `replicas` indicates how many virtual points should be used pr. node,
        replicas are required to improve the distribution.
        """
        self.replicas = replicas
        self.ring = dict()
        self._sorted_keys = []
        if nodes:
            for node in nodes:
                self.add_node(node)

    def add_node(self, node):
        """Adds a `node` to the hash ring (including a number of replicas).
        """
        for i in xrange(0, self.replicas):
            #key = self.gen_key('%s:%s' % (node, i))
            key = self.gen_key('%s%s' % (i,node))
            self.ring[key] = node
            self._sorted_keys.append(key)
        self._sorted_keys.sort()

    def remove_node(self, node):
        """Removes `node` from the hash ring and its replicas.
        """
        for i in xrange(0, self.replicas):
            #key = self.gen_key('%s:%s' % (node, i))
            key = self.gen_key('%s%s' % (i,node))
            del self.ring[key]
            self._sorted_keys.remove(key)

    def get_node(self, string_key):
        """Given a string key a corresponding node in the hash ring is returned.
        If the hash ring is empty, `None` is returned.
        """
        return self.get_node_pos(string_key)[0]

    def get_node_pos(self, string_key):
        """Given a string key a corresponding node in the hash ring is returned
        along with it's position in the ring.
        If the hash ring is empty, (`None`, `None`) is returned.
        """
        if not self.ring:
            return None, None
        key = self.gen_key(string_key)
        nodes = self._sorted_keys
        for i in xrange(0, len(nodes)):
            node = nodes[i]
            if key <= node:
                return self.ring[node], i
        return self.ring[nodes[0]], 0

    def get_nodes(self, string_key):
        """Given a string key it returns the nodes as a generator that can hold the key.
        The generator is never ending and iterates through the ring
        starting at the correct position.
        """
        if not self.ring:
            yield None, None
        node, pos = self.get_node_pos(string_key)
        for key in self._sorted_keys[pos:]:
            yield self.ring[key]
        while True:
            for key in self._sorted_keys:
                yield self.ring[key]

    def gen_key(self, key):
        """Given a string key it returns a long value,
        this long value represents a place on the hash ring.
        md5 is currently used because it mixes well.
        """
        return long(self._crc32(key),16)


    def _crc32(self, v):
        """
        Generates the crc32 hash of the v.
        @return: str, the str value for the crc32 of the v
        """
        return '%d' % (binascii.crc32(v) & 0xffffffff)

    def _md5(self, key):
        """
        Generates the md5 hash of the v.
        @return: str, the str value for the md5 of the v
        """
        m = md5.new()
        m.update(key)
        return m.hexdigest()

def usage():
    print "\nUsage: %s endpoint0/counter0 endpoint1/counter1 ...\n"%(sys.argv[0])

def main():
    if len(sys.argv) < 2 :
        usage()
        exit(1)
    
    #rrd 存放路径
    rrd_path = '/data/6070'
    
    #graph cluster 列表
    graph_dic = {'graph-00':'10.0.19.104',
                 'graph-01':'10.0.19.105',
                 'graph-02':'10.0.19.106',
                 'graph-03':'10.0.19.107'}
    graph_list = graph_dic.keys()
    ring = HashRing(graph_list,500)
    for i in range(1, len(sys.argv)):
        key = sys.argv[i]
        node = ring.get_node(key)
        md5_value = ring._md5(key)

        print "\nkey:\t%s \nnode:\t%s"%(key,node)
        print "IP:\t%s"%(graph_dic[node])
        print "rrd:\t%s/%s/%s\n" %(rrd_path,md5_value[:2],md5_value)


if __name__ == '__main__':
    main()
