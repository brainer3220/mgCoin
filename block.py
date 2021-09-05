from datetime import datetime
from hashlib import sha3_512


class Block:
    def __init__(self, transactions, previous_hash, nonce=0):
        self.timestamp = datetime.now()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.generate_hash()

    @property
    def time_stamp(self):
        return self.timestamp

    # @property
    # def transactions(self):
    #     return self.transactions

    @property
    def current_hash(self):
        return self.current_hash

    def generate_hash(self):
        # hash the blocks contents
        block_contents = str(self.timestamp) + str(self.transactions) + str(self.previous_hash) + str(self.nonce)
        block_hash = sha3_512(block_contents.encode())
        return block_hash.hexdigest()

    # @transactions.setter
    # def transactions(self, value):
    #     self._transactions = value
