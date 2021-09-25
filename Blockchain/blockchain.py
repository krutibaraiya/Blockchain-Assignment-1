#Implementation of a simple decentralized blockchain class with multiple nodes in the network

import hashlib
import json
from datetime import datetime
from urllib.parse import urlparse
import requests

# Blockchain class
class Blockchain(object):
    
    # Constructor which creates lists to store the blockchain and the transactions
    def __init__(self):

        #List to store the blockchain
        self.chain = []

        #List to store the unverified transactions
        self.unverified_transactions = []  

        #List to store verified transactions
        self.verified_transactions = []

        #Genesis block        
        self.new_block(previous_hash = 1, proof = 100)

        #Set containing the nodes in the network. Used set here to prevent the same node getting added again.
        self.nodes = set()
    

    # Method to create a new block in the Blockchain
    def new_block(self, proof,previous_hash = None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'transactions': self.unverified_transactions,
            'nonce': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }
        self.verified_transactions += self.unverified_transactions
        print(self.verified_transactions)
        self.unverified_transactions = []

        #appending the block at the end of the blockchain
        self.chain.append(block)
        return block

    #Method to add a new transaction in the next block
    def new_transaction(self, sender, item_name, bill_amount):
        self.unverified_transactions.append({
            'Customer name': sender,
            'Recipient': "Dexter's Coffee Shop",
            'Item name': item_name,
            'Total billing amount': bill_amount,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        return self.last_block['index'] + 1


    @property
    def last_block(self):
        return self.chain[-1]


    #Static method to create a SHA-256 Hash of a given block
    @staticmethod
    def hash(block):       
        block_string = json.dumps(block, sort_keys = True).encode()
        hash_val = hashlib.sha256(block_string).hexdigest()
        return hash_val
    

    #Method to calculate the proof of work
    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1       
        return proof


    #Static method to verify the proof. 
    #Here we consider the transaction to be validated if hash of (previous proof, given proof) contains 4 leading zeros.
    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
    

    #Method to add node using its IP address to our Blockchain network. 
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    
    #Method to check if the chain is validated.
    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            #If the hash value of the current block isn't correct then return false
            if block['previous_hash'] != self.hash(last_block):
                return False
            
            #If the proof of work is incorrect then return false            
            if not self.valid_proof(last_block['nonce'], block['nonce']):
                return False
            
            last_block = block
            current_index += 1

        return True
    

    #Method to replace the blockchain with the longest validated chain in the network.
    def resolve_chain(self):
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)

        for node in neighbours: 
            response = requests.get(f'http://{node}/chain')
        
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
        
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        
        if new_chain:
            self.chain = new_chain
            return True

        return False    