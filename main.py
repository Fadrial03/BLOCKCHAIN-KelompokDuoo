from blockchain import Blockchain

blockchain = Blockchain()

blockchain.add_block({
    "batch_id": "BATCH-001",
    "product":"Coffee Beans",
    "actor": "Farmer John",
    "location": "aceh, Indonesia",
})

blockchain.add_block({
    "batch_id": "BATCH-002",
    "product":"Coffee Beans",
    "actor": "Distributor Jane",
    "location": "jakarta, Indonesia",
})

for block in blockchain.chain:

    print("-" * 20)
    print("INDEX:", block.index)
    print("DATA:", block.data)
    print("PREV :", block.previous_hash)
    print("HASH :", block.hash)

print("\nBlockchain valid:", blockchain.is_chain_valid())
