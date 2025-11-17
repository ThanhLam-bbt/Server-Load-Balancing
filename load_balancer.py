# -*- coding: utf-8 -*-
from pox.core import core
import pox.lib.packet as libpacket
from pox.lib.packet.ethernet import ethernet
from pox.lib.packet.arp import arp
from pox.lib.addresses import IPAddr, EthAddr
import pox.openflow.libopenflow_01 as of
from pox.openflow.of_json import *
import random
import threading
import os
import time
import json

logger = core.getLogger()

FLOW_TIMEOUT = 10
SCHED_RANDOM = 0
SCHED_ROUNDROBIN = 1
SCHED_ALGORITHM = SCHED_ROUNDROBIN
STATS_INTERVAL = 3

LOG_DIR = os.path.expanduser("~/sdn_lb")
SERVER_USAGE_FILE = os.path.join(LOG_DIR, "server_usage.json")

class Machine(object):
    def __init__(self, mac, ip, port):
        self.mac_addr = mac
        self.ip_addr = ip
        self.port_num = port
        self.request_count = 0

    def __str__(self):
        return "MAC: " + str(self.mac_addr) + " | IP: " + str(self.ip_addr) + " | Port: " + str(self.port_num)

class UsageLogger(threading.Thread):
    def __init__(self, stop_event):
        threading.Thread.__init__(self)
        self.stop_event = stop_event
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        
        with open(SERVER_USAGE_FILE, "w") as f:
            f.write("[]") 

    def run(self):
        logger.info("Server Usage Logger started")
        while not self.stop_event.wait(STATS_INTERVAL):
            data_point = {
                "timestamp": time.time(),
                "server_usage": {}
            }
            
            for index, server in SERVER_MACHINES.items():
                data_point["server_usage"]["server%d" % (index + SERVER_START)] = server.request_count
            
            try:
                with open(SERVER_USAGE_FILE, "r+") as f:
                    f.seek(0)
                    content = f.read()
                    if content:
                        log_data = json.loads(content)
                    else:
                        log_data = []

                    log_data.append(data_point)
                    
                    f.seek(0)
                    f.truncate()
                    json.dump(log_data, f, indent=2)
                logger.debug("Logged server usage data point")
            except Exception as e:
                logger.error("Usage log file write error: %s" % str(e))

MAC_BASE = "00:00:00:00:00"
NET_BASE = "10.0.0"
SWITCH_IP_END = "13"
SWITCH_MAC_END = "13"

SWITCH_MACHINE = Machine(
    EthAddr(MAC_BASE + ":" + SWITCH_MAC_END),
    IPAddr(NET_BASE + "." + SWITCH_IP_END),
    None
)

def create_machines(start_num, end_num):
    machines = {}
    index = 0
    for num in range(start_num, end_num + 1):
        mac_end = "0" + str(num) if num < 10 else str(num)
        machines[index] = Machine(
            EthAddr(MAC_BASE + ":" + mac_end),
            IPAddr(NET_BASE + "." + str(num)),
            num
        )
        index += 1
    return machines

CLIENT_START = 1
CLIENT_END = 6
SERVER_START = 7
SERVER_END = 12

CLIENT_MACHINES = create_machines(CLIENT_START, CLIENT_END)
SERVER_MACHINES = create_machines(SERVER_START, SERVER_END)

def find_machine_by_mac(machines, mac):
    for m in machines.values():
        if str(m.mac_addr) == str(mac):
            return m
    return None

def find_machine_by_ip(machines, ip):
    for m in machines.values():
        if str(m.ip_addr) == str(ip):
            return m
    return None

class StatsCollector(threading.Thread):
    def __init__(self, conn, stop_event):
        threading.Thread.__init__(self)
        self.connection = conn
        self.stop_event = stop_event

    def run(self):
        while not self.stop_event.wait(STATS_INTERVAL):
            stats_msg = of.ofp_stats_request()
            stats_msg.type = of.OFPST_PORT
            stats_msg.body = of.ofp_port_stats_request()
            self.connection.send(stats_msg)

class LoadBalancerProxy(object):
    def __init__(self, conn):
        self.conn = conn
        global stop_event
        stop_event = threading.Event()
        StatsCollector(self.conn, stop_event).start()
        UsageLogger(stop_event).start()

        if SCHED_ALGORITHM == SCHED_ROUNDROBIN:
            self.current_server_index = random.randint(0, len(SERVER_MACHINES))

        conn.addListeners(self)

    def _handle_PortStatsReceived(self, event):
        stats_data = str(flow_stats_to_list(event.stats))
        try:
            log_path = os.path.expanduser("~/sdn_lb/final_stats.txt")
            with open(log_path, "w") as log_file:
                log_file.write("Stats: " + stats_data + "\n")
            logger.debug("Updated stats file")
        except Exception as e:
            logger.error("File write error: %s" % str(e))

    def _handle_PacketIn(self, event):
        packet = event.parse()
        if packet.type == packet.ARP_TYPE:
            logger.debug("ARP from %s" % packet.next.protosrc)
            self.process_arp(packet, event)
        elif packet.type == packet.IP_TYPE:
            logger.debug("IP from %s" % packet.next.srcip)
            self.process_service(packet, event)

    def process_arp(self, frame, event):
        def create_ethernet_frame(original_frame):
            eth_frame = ethernet()
            eth_frame.type = ethernet.ARP_TYPE
            eth_frame.dst = original_frame.src
            eth_frame.src = SWITCH_MACHINE.mac_addr
            return eth_frame

        def create_arp_reply(original_frame, arp_request, from_client):
            arp_reply = arp()
            arp_reply.opcode = arp.REPLY
            arp_reply.hwsrc = SWITCH_MACHINE.mac_addr
            arp_reply.hwdst = arp_request.hwsrc
            if from_client:
                arp_reply.protosrc = SWITCH_MACHINE.ip_addr
            else:
                arp_reply.protosrc = arp_request.protodst
            arp_reply.protodst = arp_request.protosrc
            return arp_reply

        from_client = find_machine_by_mac(CLIENT_MACHINES, frame.src) is not None
        eth_frame = create_ethernet_frame(frame)
        arp_request = frame.next
        arp_reply = create_arp_reply(frame, arp_request, from_client)
        eth_frame.set_payload(arp_reply)

        reply_msg = of.ofp_packet_out()
        reply_msg.data = eth_frame.pack()
        reply_msg.actions.append(of.ofp_action_output(port=of.OFPP_IN_PORT))
        reply_msg.in_port = event.port
        logger.debug("Sending ARP reply")
        self.conn.send(reply_msg)

    def process_service(self, frame, event):
        def select_server():
            if SCHED_ALGORITHM == SCHED_RANDOM:
                selected = random.choice(SERVER_MACHINES.values())
            elif SCHED_ALGORITHM == SCHED_ROUNDROBIN:
                self.current_server_index = (self.current_server_index + 1) % len(SERVER_MACHINES)
                selected = SERVER_MACHINES[self.current_server_index]
            return selected

        def is_server_reply(packet_frame):
            return find_machine_by_mac(SERVER_MACHINES, packet_frame.src) is not None

        def modify_icmp_reply(original_frame, destination):
            original_frame.src = SWITCH_MACHINE.mac_addr
            original_frame.dst = destination.mac_addr
            original_frame.next.srcip = SWITCH_MACHINE.ip_addr
            return original_frame

        ip_packet = frame.next

        if is_server_reply(frame):
            output_msg = of.ofp_packet_out()
            destination = find_machine_by_ip(CLIENT_MACHINES, ip_packet.dstip)
            output_msg.data = modify_icmp_reply(frame, destination).pack()
            output_msg.actions.append(of.ofp_action_output(port=destination.port_num))
            output_msg.in_port = event.port
            logger.debug("Forwarding ICMP reply")
            self.conn.send(output_msg)
            return

        selected_server = select_server()
        selected_server.request_count += 1

        server_to_client = of.ofp_flow_mod()
        server_to_client.idle_timeout = FLOW_TIMEOUT
        server_to_client.hard_timeout = FLOW_TIMEOUT
        server_to_client.match.in_port = selected_server.port_num
        server_to_client.match.dl_type = ethernet.IP_TYPE
        server_to_client.match.dl_src = selected_server.mac_addr
        server_to_client.match.dl_dst = SWITCH_MACHINE.mac_addr
        server_to_client.match.nw_src = selected_server.ip_addr
        server_to_client.match.nw_dst = ip_packet.srcip

        logger.debug("Routing %s to %s" % (ip_packet.srcip, selected_server.ip_addr))
        server_to_client.actions.append(of.ofp_action_dl_addr.set_src(SWITCH_MACHINE.mac_addr))
        server_to_client.actions.append(of.ofp_action_dl_addr.set_dst(frame.src))
        server_to_client.actions.append(of.ofp_action_nw_addr.set_src(SWITCH_MACHINE.ip_addr))
        server_to_client.actions.append(of.ofp_action_output(port=event.port))
        logger.debug("Setting server-client path")
        self.conn.send(server_to_client)

        client_to_server = of.ofp_flow_mod()
        client_to_server.idle_timeout = FLOW_TIMEOUT
        client_to_server.hard_timeout = FLOW_TIMEOUT
        client_to_server.data = event.ofp
        client_to_server.match.in_port = event.port
        client_to_server.match.dl_type = ethernet.IP_TYPE
        client_to_server.match.dl_src = frame.src
        client_to_server.match.dl_dst = SWITCH_MACHINE.mac_addr
        client_to_server.match.nw_src = ip_packet.srcip
        client_to_server.match.nw_dst = SWITCH_MACHINE.ip_addr

        client_to_server.actions.append(of.ofp_action_dl_addr.set_dst(selected_server.mac_addr))
        client_to_server.actions.append(of.ofp_action_nw_addr.set_dst(selected_server.ip_addr))
        client_to_server.actions.append(of.ofp_action_output(port=selected_server.port_num))
        logger.debug("Setting client-server path")
        self.conn.send(client_to_server)

class LoadBalancerController(object):
    def __init__(self):
        core.openflow.addListeners(self)

    def _handle_ConnectionUp(self, event):
        logger.debug("Switch connected")
        LoadBalancerProxy(event.connection)

    def _handle_ConnectionDown(self, event):
        logger.debug("Switch disconnected")
        stop_event.set()

def launch():
    core.registerNew(LoadBalancerController)
