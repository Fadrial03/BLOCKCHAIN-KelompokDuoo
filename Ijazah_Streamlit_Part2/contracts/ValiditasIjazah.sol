// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ValiditasIjazah {
    address public owner;

    // SHA-256 dari file kosong. Ditolak karena file kosong apa pun akan "lolos" verifikasi.
    bytes32 private constant HASH_FILE_KOSONG =
        0xe3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855;

    // 1. Enum status akademik
    enum StatusAkademik {
        AKTIF,   // "Mahasiswa Aktif"
        LULUS    // "Lulusan S1"
    }

    // 2. Struct tipe data kustom
    struct Mahasiswa {
        string nim;
        string nama;
        string programStudi;
        string universitas;
        uint256 tahunMasuk;
        address wallet;          // wallet pemilik ijazah (untuk klaim)
        StatusAkademik status;
        bool terdaftar;
    }

    struct Ijazah {
        string certificateId;
        string nim;
        uint256 ipk;             // disimpan x100 (3.85 -> 385); tampilan desimal lewat lihatDetailIjazah()
        string tanggalLulus;
        bytes32 documentHash;    // SHA-256 dari PDF ijazah
        address penerbit;
        uint256 timestamp;
        bool diklaim;
        bool dicabut;
        bool ada;
    }

    // 3. Mapping
    mapping(string => Mahasiswa) public daftarMahasiswa;   // nim => data mahasiswa
    mapping(string => Ijazah) public daftarIjazah;         // certificateId => data ijazah
    mapping(bytes32 => bool) public hashSudahTerdaftar;    // cegah dokumen yang sama didaftarkan 2x

    // Proof of Authority: hanya alamat terdaftar yang boleh menulis data
    mapping(address => bool) public isAuthority;
    mapping(address => string) public namaAuthority;

    // 4. Events (string tidak di-index supaya nilainya terbaca di log)
    event AuthorityDitambahkan(address indexed authority, string nama);
    event AuthorityDihapus(address indexed authority);
    event MahasiswaDiregistrasi(string nim, string nama, address indexed oleh);
    event IjazahDiterbitkan(string certificateId, string nim, bytes32 documentHash, address indexed penerbit);
    event IjazahDiklaim(string certificateId, address indexed pemilik);
    event IjazahDicabut(string certificateId, string alasan, address indexed oleh);

    // 5. Custom errors
    error HanyaOwner();
    error HanyaAuthority();
    error BukanPemilikIjazah();
    error AlamatTidakValid();
    error InputKosong();
    error FormatIpkTidakValid();
    error HashTidakValid();
    error MahasiswaSudahTerdaftar(string nim);
    error MahasiswaTidakAda(string nim);
    error MahasiswaSudahLulus(string nim);
    error IjazahSudahAda(string certificateId);
    error IjazahTidakAda(string certificateId);
    error IjazahSudahDiklaim(string certificateId);
    error IjazahSudahDicabut(string certificateId);
    error DokumenSudahTerdaftar(bytes32 documentHash);

    constructor() {
        owner = msg.sender;
        isAuthority[msg.sender] = true;
        namaAuthority[msg.sender] = "UINSSC";
        emit AuthorityDitambahkan(msg.sender, "UINSSC");
    }

    modifier onlyOwner() {
        if (msg.sender != owner) revert HanyaOwner();
        _;
    }

    modifier onlyAuthority() {
        if (!isAuthority[msg.sender]) revert HanyaAuthority();
        _;
    }

    // ---------------------------------------------------------
    // Manajemen Authority (Kemdikbud, LLDIKTI, FASTIH, dst.)
    // ---------------------------------------------------------
    function tambahAuthority(address _authority, string memory _nama) external onlyOwner {
        if (_authority == address(0)) revert AlamatTidakValid();
        if (bytes(_nama).length == 0) revert InputKosong();

        isAuthority[_authority] = true;
        namaAuthority[_authority] = _nama;
        emit AuthorityDitambahkan(_authority, _nama);
    }

    function hapusAuthority(address _authority) external onlyOwner {
        // owner tidak boleh mencabut dirinya sendiri agar kontrak tidak terkunci
        if (_authority == owner) revert AlamatTidakValid();

        isAuthority[_authority] = false;
        emit AuthorityDihapus(_authority);
    }

    // ---------------------------------------------------------
    // Aksi 1: Registrasi Mahasiswa (actor: Universitas)
    // ---------------------------------------------------------
    function registrasiMahasiswa(
        string memory _nim,
        string memory _nama,
        string memory _programStudi,
        string memory _universitas,
        uint256 _tahunMasuk,
        address _wallet
    ) external onlyAuthority {
        if (bytes(_nim).length == 0 || bytes(_nama).length == 0) revert InputKosong();
        if (_wallet == address(0)) revert AlamatTidakValid();
        if (daftarMahasiswa[_nim].terdaftar) revert MahasiswaSudahTerdaftar(_nim);
        require(_tahunMasuk >= 1900 && _tahunMasuk <= 2100, "Tahun masuk tidak valid");

        Mahasiswa storage mhs = daftarMahasiswa[_nim];
        mhs.nim = _nim;
        mhs.nama = _nama;
        mhs.programStudi = _programStudi;
        mhs.universitas = _universitas;
        mhs.tahunMasuk = _tahunMasuk;
        mhs.wallet = _wallet;
        mhs.status = StatusAkademik.AKTIF;
        mhs.terdaftar = true;

        emit MahasiswaDiregistrasi(_nim, _nama, msg.sender);
    }

    // ---------------------------------------------------------
    // Aksi 2: Terbitkan Ijazah (actor: Universitas / Authority)
    // _ipk berupa teks desimal, contoh: "3.85" atau "3,85"
    // ---------------------------------------------------------
    function terbitkanIjazah(
        string memory _certificateId,
        string memory _nim,
        string memory _ipk,
        string memory _tanggalLulus,
        bytes32 _documentHash
    ) external onlyAuthority {
        if (bytes(_certificateId).length == 0) revert InputKosong();
        if (_documentHash == bytes32(0) || _documentHash == HASH_FILE_KOSONG) revert HashTidakValid();

        Mahasiswa storage mhs = daftarMahasiswa[_nim];
        if (!mhs.terdaftar) revert MahasiswaTidakAda(_nim);
        if (mhs.status == StatusAkademik.LULUS) revert MahasiswaSudahLulus(_nim);
        if (daftarIjazah[_certificateId].ada) revert IjazahSudahAda(_certificateId);
        if (hashSudahTerdaftar[_documentHash]) revert DokumenSudahTerdaftar(_documentHash);

        uint256 ipkNilai = _parseIpk(_ipk);

        Ijazah storage ijz = daftarIjazah[_certificateId];
        ijz.certificateId = _certificateId;
        ijz.nim = _nim;
        ijz.ipk = ipkNilai;
        ijz.tanggalLulus = _tanggalLulus;
        ijz.documentHash = _documentHash;
        ijz.penerbit = msg.sender;
        ijz.timestamp = block.timestamp;
        ijz.ada = true;

        hashSudahTerdaftar[_documentHash] = true;
        mhs.status = StatusAkademik.LULUS;   // Mahasiswa Aktif -> Lulusan S1

        emit IjazahDiterbitkan(_certificateId, _nim, _documentHash, msg.sender);
    }

    // ---------------------------------------------------------
    // Aksi 3: Klaim Kredensial Ijazah (actor: Mahasiswa / Alumni)
    // ---------------------------------------------------------
    function klaimIjazah(string memory _certificateId) external {
        Ijazah storage ijz = daftarIjazah[_certificateId];

        if (!ijz.ada) revert IjazahTidakAda(_certificateId);
        if (ijz.dicabut) revert IjazahSudahDicabut(_certificateId);
        if (ijz.diklaim) revert IjazahSudahDiklaim(_certificateId);
        if (msg.sender != daftarMahasiswa[ijz.nim].wallet) revert BukanPemilikIjazah();

        ijz.diklaim = true;
        emit IjazahDiklaim(_certificateId, msg.sender);
    }

    // ---------------------------------------------------------
    // Pencabutan ijazah (dibatalkan / terbukti bermasalah)
    // ---------------------------------------------------------
    function cabutIjazah(string memory _certificateId, string memory _alasan) external onlyAuthority {
        if (bytes(_alasan).length == 0) revert InputKosong();

        Ijazah storage ijz = daftarIjazah[_certificateId];
        if (!ijz.ada) revert IjazahTidakAda(_certificateId);
        if (ijz.dicabut) revert IjazahSudahDicabut(_certificateId);

        ijz.dicabut = true;
        emit IjazahDicabut(_certificateId, _alasan, msg.sender);
    }

    // ---------------------------------------------------------
    // VALIDASI: inti deteksi pemalsuan
    // Hash PDF yang diajukan harus sama persis dengan hash di blockchain.
    // ---------------------------------------------------------
    function verifikasiIjazah(
        string memory _certificateId,
        bytes32 _documentHash
    ) external view returns (bool) {
        Ijazah storage ijz = daftarIjazah[_certificateId];
        return ijz.ada && !ijz.dicabut && ijz.documentHash == _documentHash;
    }

    // Versi dengan penjelasan hasil (enak untuk demo)
    function cekStatusIjazah(
        string memory _certificateId,
        bytes32 _documentHash
    ) external view returns (string memory) {
        Ijazah storage ijz = daftarIjazah[_certificateId];

        if (!ijz.ada) return "TIDAK DITEMUKAN";
        if (ijz.dicabut) return "DICABUT";
        if (ijz.documentHash != _documentHash) return "TIDAK VALID: hash dokumen berbeda (kemungkinan dipalsukan)";
        return "VALID";
    }

    // Detail ijazah untuk verifikator (IPK ditampilkan desimal, contoh "3.85")
    function lihatDetailIjazah(string memory _certificateId)
        external
        view
        returns (
            string memory nim,
            string memory nama,
            string memory ipk,
            string memory tanggalLulus
        )
    {
        Ijazah storage ijz = daftarIjazah[_certificateId];
        if (!ijz.ada) revert IjazahTidakAda(_certificateId);

        return (
            ijz.nim,
            daftarMahasiswa[ijz.nim].nama,
            _formatIpk(ijz.ipk),
            ijz.tanggalLulus
        );
    }

    // Status penerbitan ijazah
    function lihatStatusIjazah(string memory _certificateId)
        external
        view
        returns (
            bytes32 documentHash,
            address penerbit,
            uint256 waktuTerbit,
            bool diklaim,
            bool dicabut
        )
    {
        Ijazah storage ijz = daftarIjazah[_certificateId];
        if (!ijz.ada) revert IjazahTidakAda(_certificateId);

        return (ijz.documentHash, ijz.penerbit, ijz.timestamp, ijz.diklaim, ijz.dicabut);
    }

    // ---------------------------------------------------------
    // Helper: teks "3.85" / "3,85" / "4" -> angka x100 (385 / 385 / 400)
    // ---------------------------------------------------------
    function _parseIpk(string memory _ipk) internal pure returns (uint256) {
        bytes memory b = bytes(_ipk);
        if (b.length == 0 || b.length > 4) revert FormatIpkTidakValid();

        uint256 bulat;
        uint256 pecahan;
        uint256 digitPecahan;
        bool adaPemisah;

        for (uint256 i = 0; i < b.length; i++) {
            uint8 c = uint8(b[i]);

            if (c == 46 || c == 44) {                       // '.' atau ','
                if (adaPemisah || i == 0) revert FormatIpkTidakValid();
                adaPemisah = true;
            } else if (c >= 48 && c <= 57) {                // '0'..'9'
                uint256 digit = c - 48;
                if (!adaPemisah) {
                    bulat = bulat * 10 + digit;
                } else {
                    if (digitPecahan >= 2) revert FormatIpkTidakValid();
                    pecahan = pecahan * 10 + digit;
                    digitPecahan++;
                }
            } else {
                revert FormatIpkTidakValid();
            }
        }

        if (adaPemisah && digitPecahan == 0) revert FormatIpkTidakValid();   // contoh "3."
        if (digitPecahan == 1) pecahan = pecahan * 10;                       // "3.8" -> 3.80

        uint256 total = bulat * 100 + pecahan;
        if (total == 0 || total > 400) revert FormatIpkTidakValid();
        return total;
    }

    // Helper: 385 -> "3.85"
    function _formatIpk(uint256 _nilai) internal pure returns (string memory) {
        uint256 pecahan = _nilai % 100;
        string memory nol = "";
        if (pecahan < 10) nol = "0";   // 3.05 bukan 3.5
        return string(abi.encodePacked(_toString(_nilai / 100), ".", nol, _toString(pecahan)));
    }

    function _toString(uint256 _v) internal pure returns (string memory) {
        if (_v == 0) return "0";
        uint256 temp = _v;
        uint256 digits;
        while (temp != 0) {
            digits++;
            temp /= 10;
        }
        bytes memory buffer = new bytes(digits);
        while (_v != 0) {
            digits--;
            buffer[digits] = bytes1(uint8(48 + (_v % 10)));
            _v /= 10;
        }
        return string(buffer);
    }
}
