import hashlib

from blockchain import Blockchain
from block import Block

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
        "document_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"  # SHA-256 PDF Ijazah
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


# =====================================================
# PROOF OF AUTHORITY (menggantikan Proof of Work & Proof of Stake)
# =====================================================

def sign(block_hash, secret):
    # Tanda tangan sederhana (simulasi): hash dari hash block + kunci rahasia validator
    return hashlib.sha256((block_hash + secret).encode()).hexdigest()


def proof_of_authority(block, authorities):
    # Validator dipilih bergantian (round-robin) berdasarkan index block
    names = list(authorities)
    proposer = names[block.index % len(names)]
    signature = sign(block.hash, authorities[proposer])
    return proposer, signature


def verify_authority(block, proposer, signature, authorities):
    # Block sah jika validator terdaftar dan tanda tangannya cocok
    if proposer not in authorities:
        return False
    return signature == sign(block.hash, authorities[proposer])


print("\n" + "=" * 50)
print("PROOF OF AUTHORITY")

authorities = {
    "UINSSC": "kunci-uinssc",
    "Kemdikbud": "kunci-kemdikbud",
    "LLDIKTI": "kunci-lldikti",
    "FASTIH": "kunci-fastih"
}

print("Daftar Validator (Authority):")
for name in authorities:
    print(f"- {name}")

block = Block(
    index=1,
    data={"message": "Ijazah dari Dosen"},
    previous_hash="0"
)

proposer, signature = proof_of_authority(block, authorities)

print("\nData Block         :", block.data)
print("Validator terpilih :", proposer)
print("Tanda tangan       :", signature)
print("Block disetujui    :", verify_authority(block, proposer, signature, authorities))

print("\n--- Simulasi serangan ---")
print("Validator palsu    :", verify_authority(block, "Hacker", signature, authorities))
print("Tanda tangan palsu :", verify_authority(block, proposer, "tanda-tangan-palsu", authorities))