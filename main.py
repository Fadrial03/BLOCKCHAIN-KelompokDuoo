from blockchain import Blockchain
from block import Block
from pos import proof_of_stake
from pow import proof_of_work

blockchain = Blockchain()

blockchain.add_block({
    "transaksi_id": "TX-ADM-2026-001",
    "actor": "Universitas",                 # Pihak yang input data
    "action": "Registrasi Mahasiswa",
    "payload": {
        "nim_id": "2530801026",
        "nama": "Fadrial Junyana Putra",
        "status_akademik": "Mahasiswa Aktif",  # Status saat perkuliahan
        "program_studi": "Teknik Informatika",
        "universitas": "UINSSC",
        "tahun_masuk": "2025"
    }
})

blockchain.add_block({
    "transaksi_id": "TX-IJZ-2026-1026",
    "actor": "Mahasiswa",                   # Pemilik ijazah / Alumni
    "action": "Klaim Kredensial Ijazah",
    "payload": {
        "certificate_id": "IJZ-2026-UINSSC-2530801026",
        "nim_id": "2530801026",
        "nama": "Fadrial Junyana Putra",
        "status_akademik": "Lulusan S1",       # Status setelah lulus
        "ipk": "3.85",
        "universitas": "UINSSC",
        "tanggal_lulus": "2026-09-12",
        "document_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" # SHA-256 PDF Ijazah
    }
})

print("=== DAFTAR BLOK DALAM CHAIN ===")
for block in blockchain.chain:
    print("=" * 50)
    print("INDEX: ", block.index)
    print("DATA: ", block.data)
    print("PREV: ", block.previous_hash)
    print("HASH: ", block.hash)

print("\nBlockchain valid: ", blockchain.is_valid())

print("\n" + "=" * 50)
print("PROOF OF WORK")
block = Block(
    index=1,
    data="Ijazah dari Dosen",
    previous_hash="0"
)

difficulty = 5

print("Data Block     :", block.data)
print("Difficulty     :", difficulty)

proof_of_work(block, difficulty)

print("Nonce          :", block.nonce)
print("Hash           :", block.hash)

print("\n" + "=" * 50)
print("PROOF OF STAKE")

validators = {
    "UINSSC": 70,
    "Kemdikbud": 10,
    "LLDIKTI": 10,
    "FASTIH": 10
}

print("Daftar Validator:")
for name, stake in validators.items():
    print(f"- {name}: {stake} stake")

selected = proof_of_stake(validators)
print("\nValidator terpilih:", selected)