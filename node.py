from cProfile import label
from block import Block
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import os


class Node:
    def __init__(self, id, coins, isFast, isHighCPU, hashingFraction, isAttacker):
        
        self.id = id
        self.coins = coins
        self.isFast = isFast
        self.isHighCPU = isHighCPU
        self.isAttacker = isAttacker
        # All transactions seen by the node
        self.all_transactions   = []
        self.hashingFraction = hashingFraction
        # All transaction present in the longest chain
        self.already_in_blockchain_transactions = []
        # Collection of public_blocks seen by the node (initialized with a genesis block)
        self.public_blocks = {
            0 : [Block(0, 0, 0, -1, 0), 0],
        }
        # Collection of private_blocks mined by the attacker
        self.private_blocks = {}
        self.lead_from_honest_block = 0
        
        
    def calculate_longest_blockchain(self):
        """
        Calculates the longest chain in the node

        :return: List containing the public_blocks in the longest chain"""
        
        max_length = 0
        block_id = 0
            
        for id, block in self.public_blocks.items():
            # Go through all the public_blocks seen and get the block with max length
            length = block[0].length
            if length > max_length:
                max_length = length
                block_id = id

        # Creation time of the block with max length  
        earliest_block_time = self.public_blocks[block_id][1]
        
        for _, blk in self.public_blocks.items():
            # Checks if there is block with the same length but an earlier creation time
            if blk[0].length == max_length and blk[0].id != block_id and blk[1] < earliest_block_time:
                earliest_block_time = blk[1]
                block_id = blk[0].id
                
                # print(f"Same Length Block found for node {self.id}, length: {max_length}")
                
        long_chain = [self.public_blocks[block_id][0]]
        
        block_id = self.public_blocks[block_id][0].prev_block_id
        
        while block_id != -1:
            # Create the list of longest chain
            long_chain.append(self.public_blocks[block_id][0])
            block_id = self.public_blocks[block_id][0].prev_block_id
            
        return long_chain
    
    def T_k(self):
        """
        Simulates the delay in Proof of Work mining

        :return: Value of the delay from an exponential distribution
        """
        return np.random.exponential(5/self.hashingFraction, 1)[0]
    
    def create_chain(self):
        
        file = f"node_{self.id}.dot"
        

        with open(os.path.join("output", file), "w+") as fh:

            # Graphviz header format
            fh.write("digraph G { \n")
            fh.write('rankdir="LR";\n\n')

            # Draw edges of the blockchain tree
            for block in self.public_blocks.values():
                
                a1c = "red" 
                a2c = "blue"
                hc = "green"
                node_color = "white"
                
                if block[0].node_id == 0:
                    node_color = a1c
                elif block[0].node_id == 1:
                    node_color = a2c
                else:
                    node_color = hc
                    
                if block[0].id == 0:
                    node_color = "white"

                node_definition = f'\t{block[0].id} [color=black, style=filled, fillcolor={node_color}];\n'
                fh.write(node_definition)

                if block[0].prev_block_id != -1:
                    edge = "\t%d -> %d\n" % (block[0].prev_block_id, block[0].id)

                    fh.write(edge)

            # Close the graph
            fh.write("\n}")       
            
        for fn in os.listdir("output"):

            if fn.endswith(".dot"):

                fn = os.path.join("output", fn)

                graph = fn[:-4] + ".png"
                cmd = "dot -Tpng %s -o %s" % (fn, graph)

                # TODO: Replace with subprocess.call
                os.system(cmd)
        file1 = f"public_blocks_arrival_time{self.id}.txt"

        with open(os.path.join("output",file1), "w+") as fh:
            for id,bi in self.public_blocks.items():
                fh.write(f"block {id} : arrived at {bi[1]}\n")