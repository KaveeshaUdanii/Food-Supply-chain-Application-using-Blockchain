# blockchain.py
import hashlib
import json
import time
from typing import List, Dict
from pathlib import Path

CHAIN_PATH = Path("chain.json")


class Block:
    def __init__(self, index: int, timestamp: float, transactions: List[Dict], previous_hash: str, nonce: int = 0):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def to_dict(self):
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash
        }


class Blockchain:
    difficulty = 3  # number of leading zeros required

    def __init__(self):
        self.chain: List[Block] = []
        self.current_transactions: List[Dict] = []
        self.load_chain()

    def create_genesis(self):
        genesis_block = Block(0, time.time(), [{"system": "genesis"}], "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain = [genesis_block]
        self.save_chain()

    def load_chain(self):
        if CHAIN_PATH.exists():
            try:
                with open(CHAIN_PATH, 'r') as f:
                    raw = json.load(f)
                self.chain = []
                for b in raw:
                    block = Block(b['index'], b['timestamp'], b['transactions'], b['previous_hash'], b['nonce'])
                    block.hash = b.get('hash') or block.compute_hash()
                    self.chain.append(block)
            except Exception:
                self.create_genesis()
        else:
            self.create_genesis()

    def save_chain(self):
        with open(CHAIN_PATH, 'w') as f:
            json.dump([b.to_dict() for b in self.chain], f, indent=2)

    def add_transaction(self, transaction: Dict):
        self.current_transactions.append(transaction)

    def proof_of_work(self, block: Block) -> str:
        block.nonce = 0
        computed_hash = block.compute_hash()
        target = '0' * self.difficulty
        while not computed_hash.startswith(target):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def mine(self):
        if not self.current_transactions:
            return None
        last_block = self.chain[-1]
        new_block = Block(index=last_block.index + 1,
                          timestamp=time.time(),
                          transactions=self.current_transactions.copy(),
                          previous_hash=last_block.hash)
        proof = self.proof_of_work(new_block)
        new_block.hash = proof
        self.chain.append(new_block)
        self.current_transactions = []
        self.save_chain()
        return new_block.to_dict()

    def last_block(self):
        return self.chain[-1]

    def is_valid_chain(self, chain: List[Dict] = None) -> bool:
        if chain is None:
            chain = [b.to_dict() for b in self.chain]
        for i in range(1, len(chain)):
            prev = chain[i-1]
            block = chain[i]
            # check hash linkage
            computed_prev_hash = hashlib.sha256(json.dumps({
                'index': prev['index'],
                'timestamp': prev['timestamp'],
                'transactions': prev['transactions'],
                'previous_hash': prev['previous_hash'],
                'nonce': prev['nonce']
            }, sort_keys=True).encode()).hexdigest()
            if prev.get('hash') != computed_prev_hash and prev.get('hash') != prev.get('hash'):
                # We'll accept stored hash but verify link:
                pass
            if block['previous_hash'] != prev.get('hash'):
                return False
            # verify proof of work
            block_obj = Block(block['index'], block['timestamp'], block['transactions'], block['previous_hash'], block['nonce'])
            if block_obj.compute_hash() != block['hash']:
                return False
            if not block['hash'].startswith('0' * self.difficulty):
                return False
        return True

    def get_product_history(self, batch_id: str) -> List[Dict]:
        history = []
        for block in self.chain:
            for tx in block.transactions:
                if tx.get('batch_id') == batch_id:
                    history.append({
                        'block_index': block.index,
                        'timestamp': tx.get('timestamp', block.timestamp),
                        **tx
                    })
        return sorted(history, key=lambda x: x['timestamp'])
