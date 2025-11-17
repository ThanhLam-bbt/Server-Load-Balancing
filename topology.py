#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSKernelSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel

def sdn_load_balancer_topology():

    net = Mininet( controller=RemoteController, link=TCLink, switch=OVSKernelSwitch )

    # Creating nodes
    client1 = net.addHost( 'client1', mac='00:00:00:00:00:01', ip='10.0.0.1/8' )
    client2 = net.addHost( 'client2', mac='00:00:00:00:00:02', ip='10.0.0.2/8' )
    client3 = net.addHost( 'client3', mac='00:00:00:00:00:03', ip='10.0.0.3/8' )
    client4 = net.addHost( 'client4', mac='00:00:00:00:00:04', ip='10.0.0.4/8' )
    client5 = net.addHost( 'client5', mac='00:00:00:00:00:05', ip='10.0.0.5/8' )
    client6 = net.addHost( 'client6', mac='00:00:00:00:00:06', ip='10.0.0.6/8' )
    server7 = net.addHost( 'server7', mac='00:00:00:00:00:07', ip='10.0.0.7/8' )
    server8 = net.addHost( 'server8', mac='00:00:00:00:00:08', ip='10.0.0.8/8' )
    server9 = net.addHost( 'server9', mac='00:00:00:00:00:09', ip='10.0.0.9/8' )
    server10 = net.addHost( 'server10', mac='00:00:00:00:00:10', ip='10.0.0.10/8' )
    server11 = net.addHost( 'server11', mac='00:00:00:00:00:11', ip='10.0.0.11/8' )    
    server12 = net.addHost( 'server12', mac='00:00:00:00:00:12', ip='10.0.0.12/8' )
    s1 = net.addSwitch( 's1', listenPort=6633, mac='00:00:00:00:00:13')
    c1 = net.addController( 'c1', controller=RemoteController )

    # Creating links 
    net.addLink(client1, s1)
    net.addLink(client2, s1)
    net.addLink(client3, s1)
    net.addLink(client4, s1)
    net.addLink(client5, s1)	
    net.addLink(client6, s1)
    net.addLink(server7, s1)
    net.addLink(server8, s1)
    net.addLink(server9, s1)
    net.addLink(server10, s1)
    net.addLink(server11, s1)
    net.addLink(server12, s1)

    # Starting network
    net.build()
    c1.start()
    s1.start( [c1] )

    # Running CLI
    CLI( net )

    # Stopping network
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    sdn_load_balancer_topology()
