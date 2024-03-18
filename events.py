import random
from transaction import Transaction
from block import Block
from copy import deepcopy

class Events:
    """
    Super class for all the possible events in the simulation

    Attributes:
        creator_id: ID of the node that creatd the event
        exec_node_id: ID of the nodes where it is executed
        timeOfexec: Time of execution of the event
        creation_time: Time of event creation
    """
    def __init__(self, creator_id, exec_node_id, timeOfexec, creation_time):
        self.creator_id = creator_id
        self.exec_node_id = exec_node_id
        self.timeOfexec = timeOfexec
        self.creation_time = creation_time 

    def __lt__(self, other):
        """
        Overloading the less than operation so that the events 
        are ordered according to time of exectuion in events queue"""
        return self.timeOfexec < other.timeOfexec



class TransactionGen(Events):
    """
    Simulates the generation of a transaction in a node
    Child class of Event

    Attributes:
        payer_id: ID of the node which creates and executes the transaction
    """
    def __init__(self, timeOfexec, payer_id, creation_time):
        super().__init__(payer_id,payer_id,timeOfexec, creation_time)
        self.payer_id = payer_id
        
    def execute(self, sim):
        payer = sim.nodes[self.payer_id]
        # Selects a payee randomly
        payee_id, payee = random.choice(list(set(list(sim.nodes.items())) - set([(self.payer_id,payer)])))

        # Adds a new transaction generation event to be executed after some transasction delay
        t = sim.interArrival_txndelay()
        sim.events.put(TransactionGen( self.timeOfexec + t, self.payer_id, self.timeOfexec))

        # # If payer has no coins, abort transaction
        if payer.coins == 0:
            return

        # Amount paid is chosen randomly between 1 and balance/2
        amount = random.randint(1,1+(payer.coins)//2)


        # Transaction created
        txn = Transaction(sim.txn_id,self.payer_id,payee_id,amount)
        print(self.timeOfexec, txn)

        # Global transaction ID incremented
        sim.txn_id+=1

        # Transaction added to payer's seen transactions
        payer.all_transactions.append(txn)

        for i in sim.peers[self.payer_id]:
            # Transaction receive event put in the events queue for all the neighbours
            sim.events.put(TransactionRec(self.timeOfexec + sim.delay(8000,self.payer_id,i), i, self.payer_id, self.payer_id, txn,self.creation_time))

           


class TransactionRec(Events):
    """
    Simulates the receiving of a transaction by a node
    Child class of Event

    Attributes:
        receiver_id: ID of the node which receives the transaction
        new_transaction: A deepcopy of the received transaction
        sender_id: ID of the node which sent the transaction
    """
    def __init__(self, timeOfexec, node_id, creator_id, sender_id, txn, creation_time):
        super().__init__(creator_id, node_id, timeOfexec, creation_time)
        
        self.receiver_id = node_id
        self.new_transaction = deepcopy(txn)
        self.sender_id = sender_id
        
    def execute(self, sim):
        
        rcvr = sim.nodes[self.receiver_id]
        
        # Checks if the node has already seen this transaction.
        if self.new_transaction.id in [tx.id for tx in rcvr.all_transactions]:
            # If yes, then returns
            return
        
        # Transaction is added to list of seen trnasactions
        rcvr.all_transactions.append(self.new_transaction)


        
        for i in sim.peers[self.receiver_id]:
            # Transaction receive event put in the events queue for all the neighbours
            if i != self.sender_id:
                sim.events.put(TransactionRec(self.timeOfexec + sim.delay(8000, self.receiver_id, i), i, self.creator_id, self.receiver_id, self.new_transaction, self.timeOfexec))
        
        
        
class BlockGen(Events):
    """
    Simulates the Block generation event by a node
    Child class of Event

    Attributes:
        prev_last_block: Deepcopy of the parent block of the new block
    """
    def __init__(self, timeOfexec, creator_id, creation_time, prev_last_block):
        super().__init__(creator_id,creator_id,timeOfexec, creation_time)
        self.prev_last_block = deepcopy(prev_last_block)
        
    def execute(self,sim):
        
        miner = sim.nodes[self.creator_id]
        # Calculates the longest chain
        new_longest_chain = miner.calculate_longest_blockchain()

        # Checks if the longest chain has changed between tk and tk + Tk        
        if(new_longest_chain[0].id != self.prev_last_block.id):
            # If yes, then returns
            print("Longest chain changed")
            return
         
        # Transactions seen by the node but not included in the longest chain
        remaining_txns = set(miner.all_transactions) - set(miner.already_in_blockchain_transactions)

        valid_remaining_txns = []

        # Filtering out only the valid transactions
        for txn in remaining_txns:
            if sim.nodes[txn.sender_id].coins >= txn.coins:
                valid_remaining_txns.append(txn)
                sim.nodes[txn.sender_id].coins -= txn.coins
                sim.nodes[txn.receiver_id].coins += txn.coins


        if len(list(valid_remaining_txns)) == 0:
            # If thre are no transactions to put in, return
            return
        
        # Create a new Block
        new_block = Block(sim.block_id, self.exec_node_id, self.timeOfexec, self.prev_last_block.id, self.prev_last_block.length + 1)
        # Add the new transactions to the block
        new_block.transactions = list(valid_remaining_txns)[0: min(999, len(valid_remaining_txns))]
        # Node receives the mining reward
        miner.coins += 50
        # Block is added to the collection blocks the node has seen
        miner.blocks[sim.block_id] = [new_block, self.timeOfexec]
        # Newly added transaction are added to the longest chain transactions
        miner.already_in_blockchain_transactions += valid_remaining_txns
        
        
        print(self.timeOfexec, f"BlockID:{sim.block_id} :: {self.creator_id} mines 50 coins")
        
        # Gloabl BlockID is incremented
        sim.block_id += 1
        
        msg_length = (1 + len(new_block.transactions))*8000
        
        for i in sim.peers[self.creator_id]:
            # Block receive event added for all the neighbours 
            sim.events.put(BlockRec(self.timeOfexec + sim.delay(msg_length, self.creator_id, i), i, self.creator_id, self.creator_id, self.timeOfexec, new_block))

class BlockRec(Events):
    """
    Simulates the Block receiving event by a node
    Child class of Event

    Attributes:
        new_block: Deepcopy of the block received
        sender_id: ID of the sender node
    """
    def __init__(self, timeOfexec, node_id, creator_id, sender_id, creation_time, block):
        super().__init__(creator_id, node_id, timeOfexec, creation_time)
        self.new_block = deepcopy(block)
        self.sender_id = sender_id
    
    def execute(self,sim):

        cur_node = sim.nodes[self.exec_node_id]
        
        if self.new_block.id in list(cur_node.blocks.keys()):
            # If block is already seen by the node, then return
            return
        if self.new_block.prev_block_id not in list(cur_node.blocks.keys()):
            # If the parent of the recieved block is not present in the node, return
            return
        
        # Check if all transactions in the block are valid
        for txn in self.new_block.transactions:
            if sim.nodes[txn.sender_id].coins < 0:
                return
        
        # Add the recived block to the collection of seen blocks
        cur_node.blocks[self.new_block.id] = [self.new_block, self.timeOfexec]
        
        # Calculate the longest chain and get the last block
        longest_chain = cur_node.calculate_longest_blockchain()
        last_block = longest_chain[0]
        
        

        # Add the transactions in the new block to the list of longest chain transactions
        cur_node.already_in_blockchain_transactions += self.new_block.transactions


        for i in sim.peers[self.exec_node_id]:
            # Block receive event added for all the neighbours 
            if i == self.sender_id:
                continue
            sim.events.put(BlockRec(self.timeOfexec + sim.delay(8000*(1+len(self.new_block.transactions)), self.exec_node_id, i) , i, self.creator_id, self.exec_node_id, self.timeOfexec, self.new_block))
        
        # Block generation event put in the event queue with a delay (Proof of Work delay)
        sim.events.put(BlockGen(self.timeOfexec + sim.nodes[self.exec_node_id].T_k() , self.exec_node_id , self.timeOfexec, last_block))


        
        

        