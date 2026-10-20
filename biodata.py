"""
Sistem Pengisian Biodata Mahasiswa (CLI)
Data: NIM, Nama, Kelas, Tanggal Lahir, Alamat, Agama, Email
Fitur: tambah, lihat, cari, ubah, hapus, dan ekspor ke CSV.
Data disimpan di file biodata.json pada folder yang sama.
"""

import csv
import json
import os
import re
from datetime import datetime

FILE_DATA = "biodata.json"
FILE_CSV = "biodata.csv"

AGAMA = {
    "1": "Islam",
    "2": "Kristen",
    "3": "Katolik",
    "4": "Hindu",
    "5": "Buddha",
    "6": "Konghucu",
}


# ---------- Penyimpanan ----------
def muat_data():
    if not os.path.exists(FILE_DATA):
        return []
    try:
        with open(FILE_DATA, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        print("Peringatan: file data rusak atau tidak bisa dibaca, memulai dari kosong.")
        return []


def simpan_data(data):
    with open(FILE_DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ---------- Input & validasi ----------
def input_teks(label, default=None):
    while True:
        prompt = label + (f" [{default}]" if default else "")
        nilai = input(prompt + ": ").strip()
        if not nilai and default:
            return default
        if nilai:
            return nilai
        print("  -> Tidak boleh kosong.")


def input_nim(data, nim_lama=None):
    while True:
        nilai = input_teks("NIM (angka)", default=nim_lama)
        if not re.fullmatch(r"\d{5,15}", nilai):
            print("  -> NIM harus berupa angka (5-15 digit).")
            continue
        if nilai != nim_lama and any(d["nim"] == nilai for d in data):
            print("  -> NIM sudah terdaftar.")
            continue
        return nilai


def input_nama(default=None):
    while True:
        nilai = input_teks("Nama lengkap", default=default)
        if re.fullmatch(r"[A-Za-z .'\-]+", nilai):
            return nilai.title()
        print("  -> Nama hanya boleh berisi huruf, spasi, titik, apostrof, atau tanda hubung.")


def input_kelas(default=None):
    return input_teks("Kelas (contoh: TI-2A)", default=default).upper()


def input_tanggal(default=None):
    while True:
        nilai = input_teks("Tanggal lahir (DD-MM-YYYY)", default=default)
        try:
            tgl = datetime.strptime(nilai, "%d-%m-%Y")
        except ValueError:
            print("  -> Format salah. Contoh: 17-08-2005")
            continue
        if tgl > datetime.now():
            print("  -> Tanggal lahir tidak boleh di masa depan.")
            continue
        return tgl.strftime("%d-%m-%Y")


def input_agama(default=None):
    daftar = ", ".join(f"{k}={v}" for k, v in AGAMA.items())
    kode_default = next((k for k, v in AGAMA.items() if v == default), None)
    while True:
        nilai = input_teks(f"Agama ({daftar})", default=kode_default)
        if nilai in AGAMA:
            return AGAMA[nilai]
        print("  -> Pilihan tidak valid.")


def input_email(default=None):
    while True:
        nilai = input_teks("Email", default=default)
        if re.fullmatch(r"[\w.+\-]+@[\w\-]+(\.[\w\-]+)+", nilai):
            return nilai.lower()
        print("  -> Format email tidak valid.")


def hitung_umur(tgl_lahir):
    lahir = datetime.strptime(tgl_lahir, "%d-%m-%Y")
    now = datetime.now()
    return now.year - lahir.year - ((now.month, now.day) < (lahir.month, lahir.day))


# ---------- Fitur utama ----------
def form_biodata(data, lama=None):
    lama = lama or {}
    return {
        "nim": input_nim(data, lama.get("nim")),
        "nama": input_nama(lama.get("nama")),
        "kelas": input_kelas(lama.get("kelas")),
        "tanggal_lahir": input_tanggal(lama.get("tanggal_lahir")),
        "alamat": input_teks("Alamat", default=lama.get("alamat")),
        "agama": input_agama(lama.get("agama")),
        "email": input_email(lama.get("email")),
    }


def tambah(data):
    print("\n=== Tambah Biodata ===")
    entri = form_biodata(data)
    data.append(entri)
    simpan_data(data)
    print(f"\nBiodata {entri['nama']} berhasil disimpan.")


def tampilkan_satu(d):
    print("-" * 50)
    print(f"NIM            : {d['nim']}")
    print(f"Nama           : {d['nama']}")
    print(f"Kelas          : {d['kelas']}")
    print(f"Tanggal lahir  : {d['tanggal_lahir']} ({hitung_umur(d['tanggal_lahir'])} tahun)")
    print(f"Alamat         : {d['alamat']}")
    print(f"Agama          : {d['agama']}")
    print(f"Email          : {d['email']}")


def lihat(data):
    print("\n=== Daftar Biodata ===")
    if not data:
        print("Belum ada data.")
        return
    for d in data:
        tampilkan_satu(d)
    print("-" * 50)
    print(f"Total: {len(data)} data")


def cari(data):
    print("\n=== Cari Biodata ===")
    kata = input("Masukkan NIM, nama, atau kelas: ").strip().lower()
    hasil = [
        d for d in data
        if kata in d["nim"] or kata in d["nama"].lower() or kata in d["kelas"].lower()
    ]
    if not hasil:
        print("Data tidak ditemukan.")
        return
    for d in hasil:
        tampilkan_satu(d)


def ubah(data):
    print("\n=== Ubah Biodata ===")
    nim = input("Masukkan NIM yang akan diubah: ").strip()
    for i, d in enumerate(data):
        if d["nim"] == nim:
            print("Tekan Enter untuk mempertahankan nilai lama.")
            data[i] = form_biodata(data, d)
            simpan_data(data)
            print("Data berhasil diperbarui.")
            return
    print("NIM tidak ditemukan.")


def hapus(data):
    print("\n=== Hapus Biodata ===")
    nim = input("Masukkan NIM yang akan dihapus: ").strip()
    for i, d in enumerate(data):
        if d["nim"] == nim:
            yakin = input(f"Yakin hapus data {d['nama']}? (y/n): ").strip().lower()
            if yakin == "y":
                data.pop(i)
                simpan_data(data)
                print("Data berhasil dihapus.")
            else:
                print("Dibatalkan.")
            return
    print("NIM tidak ditemukan.")


def ekspor_csv(data):
    if not data:
        print("Belum ada data untuk diekspor.")
        return
    with open(FILE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
        writer.writeheader()
        writer.writerows(data)
    print(f"Data diekspor ke {FILE_CSV}")


def menu():
    data = muat_data()
    aksi = {
        "1": ("Tambah biodata", tambah),
        "2": ("Lihat semua biodata", lihat),
        "3": ("Cari biodata", cari),
        "4": ("Ubah biodata", ubah),
        "5": ("Hapus biodata", hapus),
        "6": ("Ekspor ke CSV", ekspor_csv),
    }
    while True:
        print("\n" + "=" * 50)
        print("     SISTEM PENGISIAN BIODATA MAHASISWA")
        print("=" * 50)
        for k, (nama, _) in aksi.items():
            print(f"{k}. {nama}")
        print("0. Keluar")
        pilih = input("Pilih menu: ").strip()
        if pilih == "0":
            print("Terima kasih!")
            break
        if pilih in aksi:
            aksi[pilih][1](data)
        else:
            print("Menu tidak valid.")


if __name__ == "__main__":
    try:
        menu()
    except (KeyboardInterrupt, EOFError):
        print("\nProgram dihentikan.")