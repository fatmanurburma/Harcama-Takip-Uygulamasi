import csv 
from datetime import datetime 

DATA_FILE = "data.csv"

def init_file():
    try:
        with open(DATA_FILE, "x", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Tarih, Kategori, Miktar, Açıklama"])
    except FileExistsError:
        pass
def harcama_ekle(kategori, miktar, aciklama):
    tarih = datetime.now().strftime("%Y-&m-&d &H:%M")
    with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([tarih, kategori, miktar, aciklama])
    print("Harcama eklendi.")

def harcamalari_listele():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader) 
        for row in reader:
            print(f"{row[0]}| {row[1]}| {row[2]} TL | {row[3]}")

def menu():
    init_file()
    while True:
        print("\n--- Harcama Takip ---")
        print("1) Harcama Ekle")
        print("2) Harcamaları Listele")
        print("3) Çıkış")
        secim = input("Secim:")

        if secim == "1":
            kategori = input("Kategori:")
            miktar = input("Miktar(TL):")
            aciklama = input("Açıklama:")
            harcama_ekle(kategori, miktar, aciklama)
        elif secim == "2":
            harcamalari_listele()
        elif secim == "3":
            print("Çıkılıyor...")
            break
        else:
            print("Geçersiz seçim.")

if __name__ == "__main__":
    menu()
