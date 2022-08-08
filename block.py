# from crypt import methods
from hashlib import sha256
import json
import time
from flask import Flask, request
import requests


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class Blockchain:
    difficulty = 2

    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        self.create_geneisis_block()

    def create_geneisis_block(self):
        genesis_block = Block(0, [], time.time(), "0" * 64)
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def print_block(self, n):
        if len(self.chain) < n:
            return None
        else:
            block = self.chain[n]
            return (
                "\nIndex: {}\nTransaction: {}\nTimestamp: {}\nPreviousHash: {}".format(
                    block.index,
                    block.transactions,
                    block.timestamp,
                    block.previous_hash,
                )
            )

    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith("0" * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def add_block(self, block, proof):
        previous_hash = self.last_block.hash
        if previous_hash != block.previous_hash:
            return False
        if not self.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    def is_valid_proof(self, block, block_hash):
        return block_hash.startswith("0" * Blockchain.difficulty) and (
            block_hash == block.compute_hash()
        )

    def new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def mine(self):
        if not self.unconfirmed_transactions:
            return False
        last_block = self.last_block
        new_block = Block(
            index=last_block.index + 1,
            transactions=self.unconfirmed_transactions,
            timestamp=time.time(),
            previous_hash=last_block.hash,
        )
        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []
        return new_block.index


# a = Blockchain()
# a.new_transaction("Hola blockchain")
# a.new_transaction("sfsdfsdf")
# a.mine()
# len_bk = len(a.chain)
# print(a.print_block(len_bk - 1))

app = Flask(__name__)

blockchain = Blockchain()


@app.route("/transactions", methods=["POST"])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ["author", "content"]
    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid Input", 104
    tx_data["timestamp"] = time.time()
    blockchain.new_transaction(tx_data)
    return "Done", 201


@app.route("/mine", methods=["GET"])
def mine_unconfirmed_transaction():
    result = blockchain.mine()
    if not result:
        return "Nothing to mine"
    return "Block#{} has mined".format(result)


@app.route("/chain", methods=["GET"])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"lenght": len(chain_data), "chain": chain_data})


@app.route("/transactions/pending", methods=["GET"])
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


@app.route("/")
def get_home():
    return "Welcome to Blockchain"


app.run(port=8000)
