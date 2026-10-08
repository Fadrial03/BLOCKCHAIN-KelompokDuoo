import hashlib


def sign(block_hash, secret):
    return hashlib.sha256((block_hash + secret).encode()).hexdigest()


def proof_of_authority(block, authorities):
    names = list(authorities)
    proposer = names[block.index % len(names)]   # giliran bergantian (round-robin)
    signature = sign(block.hash, authorities[proposer])
    return proposer, signature


def verify_authority(block, proposer, signature, authorities):
    if proposer not in authorities:
        return False
    return signature == sign(block.hash, authorities[proposer])