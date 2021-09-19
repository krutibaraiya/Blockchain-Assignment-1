#Interacting with the simple decentralized blockchain with multiple nodes using HTTP requests

from uuid import uuid4
from flask import Flask, jsonify, request

from blockchain import Blockchain

#Initialise our node with identifier and instantiate the Blockchain class
app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', '')
blockchain = Blockchain()

#API endpoint to mine a block, its an HTTP GET request
@app.route('/mine', methods=['GET'])
#Method to mine a block by calculating the proof of work and getting reward for same.
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1
    )

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New block mined!",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }

    return jsonify(response), 200

#Endpoint for a posting new transaction
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values! Please enter sender, recipient and amount.', 400
    
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {
        'message': f'Transaction will be added to block {index}'
    }
    return jsonify(response), 201

#Endpoint for viewing the blockchain
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

#Endpoint for adding new nodes in the network in the form of HTTP address.
@app.route('/nodes/add', methods=['POST'])
def add_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please enter a valid list of HTTP nodes", 400
    
    for node in nodes:
        blockchain.add_node(node)
    
    response = {
        'message': 'New nodes are added!',
        'total_nodes': list(blockchain.nodes)
    }
    return jsonify(response), 201


#Endpoint to resolve and replace current chain with the longest validated one
@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_chain()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
    return jsonify(response), 200

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    app.run(host='0.0.0.0', port=port)