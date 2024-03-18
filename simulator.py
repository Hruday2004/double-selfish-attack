import numpy as np
import random
from node import Node
from queue import PriorityQueue
import networkx as nx
from events import *
import matplotlib.pyplot as plt

class Simulator:
    """ 
    Simulator
    
    Attributes:
    num_nodes: Number of nodes in the network
    slowfrac: Fraction of nodes which have slow transmission
    lowCPUfrac: Fraction of nodes having low hashing power
    txnDelay_meantime: Mean for transaction delay exponential distribution
    max_sim_time: Maximum simulation time for simulator
    
    """
    def __init__(self, num_nodes, slowfrac, lowCPUfrac, txnDelay_meantime, max_sim_time):

        self.txnDelay_meantime = txnDelay_meantime
        self.num_nodes = num_nodes
        self.block_id = 1 # initial BlockID
        self.txn_id = 1 # initial TxnID

        self.p = []
        self.c = []


        self.time = 0    # keeps track of time in the simulator    
        self.max_sim_time = max_sim_time

        self.events = PriorityQueue() # Priority Queue to store the events in the ascending order of executuion time

        
        self.nodes = self.create_nodes(slowfrac,lowCPUfrac)
        self.peers = self.create_peers(num_nodes)

        self.initial_events()
        

    def __str__(self):
        pass
    def create_nodes(self, slowfrac, lowCPUfrac): 
        """ Creates the nodes in the Simulator

        :param slowfrac: Fraction of nodes which have slow transmission
        :param lowCPUfrac: Fraction of nodes having low hashing power
        :return : A list of nodes
        """

        slownodes = int(slowfrac * self.num_nodes)
        lowCPUnodes = int(lowCPUfrac * self.num_nodes)

        l1 = [1]*int(self.num_nodes-slownodes) + [0]*slownodes
        l2 = [1]*int(self.num_nodes-lowCPUnodes) + [0]*lowCPUnodes

        # Sum of hashing power of all the nodes
        hashingSum = (self.num_nodes-lowCPUnodes)*10 + lowCPUnodes 


        random.shuffle(l1)  
        random.shuffle(l2)

        nodes = {}

        for i in range(self.num_nodes):
            hashFrac = 1/hashingSum
            if l2[i] == 1:
                hashFrac = 10/hashingSum
        
            nodes[i] = Node(coins=100,isFast=l1[i], isHighCPU=l2[i],id=i,hashingFraction=hashFrac )

        for i in range(self.num_nodes):
            self.p.append([])
            self.c.append([])
            for j in range(self.num_nodes):
                # Speed of light propagation for node pair (i,j)
                self.p[i].append(np.random.uniform(10,500,1)[0]/1000) 
                
                # Link speed for node pair (i,j)
                if l1[i] == 1 and l1[j] == 1:                         
                    # Set 100Mbps if both nodes are fast
                    self.c[i].append(100 *(10**6))
                else:                   
                    # Set to 5 Mbps if atleast one is slow
                    self.c[i].append(5 *(10**6))
        
        

        return nodes
    def interArrival_txndelay(self):
        """
        To get the value of inter arrival transaction delay from an exponential distribution

        :return: Value of inter arrival transaction delay
        """
        return np.random.exponential(self.txnDelay_meantime, 1)[0]
    
    def create_constrained_graph(self,num_peers):
        """Creates a graph ensuring each node has 3 to 6 connections.
        
           :param num_peers: The number of nodes in the network
           :return: A Graph object 'G' which is the required graph
        """
        G = nx.Graph()
        G.add_nodes_from(range(num_peers))
        
        # Initialize all nodes with an empty list of connections
        connections = {i: [] for i in range(num_peers)}
        
        # List to manage nodes needing more connections
        needs_connection = list(range(num_peers))
        
        while needs_connection:
            peer = needs_connection.pop(0)
            # Ensure we do not exceed the max connections while also meeting the minimum
            possible_connections = [p for p in range(num_peers) if p != peer and len(connections[p]) < 6 and p not in connections[peer]]
            while len(connections[peer]) < 3 and possible_connections:
                # Choose a random peer to connect, ensuring it does not exceed its connection limit
                connect_to = random.choice(possible_connections)
                connections[peer].append(connect_to)
                connections[connect_to].append(peer)

                G.add_edge(peer, connect_to)
              
                possible_connections.remove(connect_to)
        
            if len(connections[peer]) < 3:
                # If number of connections are less than 3, it is put back into the list
                needs_connection.append(peer)
        
        return G
    
    def is_connected(self,G):
        """Checks if the graph is connected."""
        return nx.is_connected(G)

    def create_and_check_constrained_graph(self,num_peers):
        """Recreates the graph until it meets the connected and constraints criteria."""

        while True:
            G = self.create_constrained_graph(num_peers)
            if self.is_connected(G):
                break
        return G
    
    def create_peers(self, num_nodes):
        G = self.create_and_check_constrained_graph(num_nodes)
        # peers stores the node to neighbour mapping, where key is the node and value is a list of neighbours
        peers = {}
        for node in G.nodes():
            peers[node] = list(G.neighbors(node))

        plt.figure(figsize=(8, 5))
        nx.draw(G, with_labels=True, node_color='lightgreen', edge_color='gray')
        plt.savefig("network.png")
        

        return peers
          
    def initial_events(self):
        """
        Puts initial events in the events queue
        """
        for i in range(self.num_nodes):
            # Initial transactions
            self.events.put(TransactionGen(self.interArrival_txndelay(), i,0))
        
        for i in range(self.num_nodes):
            # Initial Block generation events
            self.events.put(BlockGen(self.nodes[i].T_k(),i,0,self.nodes[i].blocks[0][0]))

    def run(self):
        """
        Executes the events in the Queue till time elapsed is less than max simulation time
        """
    
        ne = 0
        while self.time < self.max_sim_time:
            event = self.events.get()
            ne += 1
            if self.events.qsize() == 0:
                print("No more events")
                break
            self.time = event.timeOfexec
            event.execute(self)
       
        # Creates a Blockchain graph for each node in the network
        for i in range(self.num_nodes):
            self.nodes[i].create_chain()
        
       
    def delay(self, message_length,sender_id,receiver_id):
        """
        :param message_length: Size of the message to be transmitted in bits
        :param sender_id: Sender node ID
        :param receiver_id: Receiver node ID
        :return: Delay associcated with the given transmission """

        # Queueing Delay
        dij = np.random.exponential(96 * (10 ** 3)/self.c[sender_id][receiver_id], 1)[0] 

        # delay = pij + |m|/cij + dij
        return self.p[sender_id][receiver_id] + (message_length)/self.c[sender_id][receiver_id] + dij

        

        