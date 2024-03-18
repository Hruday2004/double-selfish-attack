class Transaction:
    def __init__(self, id, sender_id, receiver_id, coins):
        
        self.id = id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        # Amount involved in transaction
        self.coins = coins
        # Block which contains this transaction
        self.block_id = None

        
    def __repr__(self):
        return f"TxnID: {self.id} :: {self.sender_id} pays {self.receiver_id} {self.coins} coins"