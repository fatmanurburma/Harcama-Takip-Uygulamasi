import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
import csv
from datetime import datetime
import os 

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates

DATA_FILE = "data.csv"


DEFAULT_CATEGORIES = ["Giyim", "Ulaşım", "Gıda", "Fatura", "Eğlence","Diğer"]


def init_file():
    try:
        with open(DATA_FILE, "x", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Tarih", "Kategori", "Miktar", "Açıklama"])
    except FileExistsError:
        pass

def get_all_records():
    records = []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader) 
            records = list(reader)
    except FileNotFoundError:
        init_file()
    return records

def kategori_guncelle():
    kategoriler = set(DEFAULT_CATEGORIES)
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                kategoriler.add(row[1])
    except:
        pass
    kategori_combobox.configure(values=list(sorted(kategoriler)))

def harcama_ekle_mode():
    now = datetime.now()
    tarih_entry.delete(0, tk.END)
    tarih_entry.insert(0, now.strftime("%Y-%m-%d"))

    zaman_entry.delete(0, tk.END)
    zaman_entry.insert(0, now.strftime("%H:%M")) 
    
    kategori_entry.delete(0, tk.END)
    miktar_entry.delete(0, tk.END)
    aciklama_entry.delete(0, tk.END)
    
    ekle_btn.configure(text="➕ Harcama Ekle", fg_color="#3b8ed4", 
                       command=lambda: harcama_ekle(kategori_entry.get(), miktar_entry.get(), aciklama_entry.get(), tarih_entry.get(), zaman_entry.get()))


def fill_form_for_edit(event):
    selected_item = tree.focus()
    if not selected_item:
        return

    harcama_verisi = tree.item(selected_item, 'values')
    if not harcama_verisi or len(harcama_verisi) < 4:
        return

    try:
        tarih_tam = harcama_verisi[0]
        tarih_parca, zaman_parca = tarih_tam.split(' ')[:2] 
    except ValueError:
        tarih_parca = harcama_verisi[0]
        zaman_parca = datetime.now().strftime('%H:%M') 
        
    
    tarih_entry.delete(0, tk.END)
    tarih_entry.insert(0, tarih_parca) 
    
    zaman_entry.delete(0, tk.END)
    zaman_entry.insert(0, zaman_parca[:5]) 

    kategori_entry.delete(0, tk.END)
    kategori_entry.insert(0, harcama_verisi[1])

    miktar_entry.delete(0, tk.END)
    miktar_entry.insert(0, harcama_verisi[2])

    aciklama_entry.delete(0, tk.END)
    aciklama_entry.insert(0, harcama_verisi[3])

   
    ekle_btn.configure(text="💾 Kaydı Güncelle", fg_color="orange", command=harcama_guncelle)


def harcama_ekle(kategori, miktar, aciklama, tarih_str, zaman_str):
    if not kategori or not miktar or not tarih_str or not zaman_str:
        messagebox.showwarning("Hata", "Tarih, Saat, Kategori ve Miktar zorunlu!")
        return

    try:
        miktar_float = float(miktar.replace(",", "."))
    except ValueError:
        messagebox.showerror("Hata", "Miktar geçerli bir sayı olmalıdır.")
        return


    try:
        datetime.strptime(f"{tarih_str} {zaman_str}", "%Y-%m-%d %H:%M")
        tarih_tam = f"{tarih_str} {zaman_str}:00" 
    except ValueError:
        messagebox.showerror("Hata", "Tarih formatı YYYY-MM-DD, Saat formatı HH:MM olmalıdır.")
        return
    
    try:
        with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([tarih_tam, kategori, f"{miktar_float:.2f}", aciklama])

        messagebox.showinfo("Başarılı", "Harcama eklendi ✅")
        harcama_ekle_mode() 
        listele_harcamalar()
        kategori_guncelle()
        guncelle_grafik() 
    except Exception as e:
        messagebox.showerror("Hata", f"Dosyaya yazılamadı: {e}")


def harcama_guncelle():
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showwarning("Uyarı", "Önce bir harcama seçmelisiniz.")
        return
    
    eski_veriler = tree.item(selected_item, 'values')
    
    
    yeni_kategori = kategori_entry.get()
    yeni_miktar = miktar_entry.get()
    yeni_aciklama = aciklama_entry.get()
    yeni_tarih_str = tarih_entry.get()
    yeni_zaman_str = zaman_entry.get()
    
    if not yeni_kategori or not yeni_miktar or not yeni_tarih_str or not yeni_zaman_str:
        messagebox.showwarning("Hata", "Tarih, Saat, Kategori ve Miktar zorunlu!")
        return
        
    try:
        miktar_float = float(yeni_miktar.replace(",", "."))
        datetime.strptime(f"{yeni_tarih_str} {yeni_zaman_str}", "%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        messagebox.showerror("Hata", "Miktar geçerli bir sayı, Tarih YYYY-MM-DD, Saat HH:MM olmalıdır.")
        return
        
    tum_veriler = []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            tum_veriler.append(header)

            guncellendi = False
            for row in reader:
                if list(row) == list(eski_veriler) and not guncellendi: 
                    yeni_tarih_tam = f"{yeni_tarih_str} {yeni_zaman_str}:00" 
                    
                    yeni_satir = [yeni_tarih_tam, yeni_kategori, f"{miktar_float:.2f}", yeni_aciklama]
                    tum_veriler.append(yeni_satir)
                    guncellendi = True
                else:
                    tum_veriler.append(row)

        with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(tum_veriler)
            
        messagebox.showinfo("Başarılı", "Harcama başarıyla güncellendi 👍")
        harcama_ekle_mode() 
        listele_harcamalar()
        kategori_guncelle()
        guncelle_grafik()
        
    except Exception as e:
        messagebox.showerror("Hata", f"Güncelleme hatası: {e}")


def harcama_sil():
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showwarning("Uyarı", "Lütfen silinecek bir harcama seçin.")
        return

    harcama_verisi = tree.item(selected_item, 'values')
    if not harcama_verisi:
        return

    cevap = messagebox.askyesno("Onay", f"Seçili harcamayı silmek istediğinizden emin misiniz?\n{harcama_verisi}")
    
    if cevap:
        tum_veriler = []
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader) 
                tum_veriler.append(header)
                
                silindi = False
                for row in reader:
                    if list(row) == list(harcama_verisi) and not silindi:
                        silindi = True 
                    else:
                        tum_veriler.append(row)
            
            with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(tum_veriler)

            messagebox.showinfo("Başarılı", "Harcama başarıyla silindi 🗑️")
            harcama_ekle_mode() 
            listele_harcamalar()
            kategori_guncelle()
            guncelle_grafik()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Silme işlemi sırasında bir hata oluştu: {e}")


def verileri_disa_aktar():
    try:
        output_file_name = "harcamalar_yedek.csv" 
        
        with open(DATA_FILE, "r", encoding="utf-8") as f_in:
            data = f_in.read()

        with open(output_file_name, "w", encoding="utf-8", newline="") as f_out:
            f_out.write(data)
            
        tam_yol = os.path.abspath(output_file_name) 

        messagebox.showinfo("Başarılı", f"Veriler başarıyla aktarıldı.\nDosya Konumu: {tam_yol}")
    except Exception as e:
        messagebox.showerror("Hata", f"Veri dışa aktarma hatası: {e}")


def listele_harcamalar(filtre_kategori="Tüm Kategoriler", filtre_tipi="Tüm Zamanlar"):
    for row in tree.get_children():
        tree.delete(row)

    toplam = 0
    now = datetime.now()
    records = get_all_records()

    filtered_records = []
    for row in records:
        try:
            if len(row) < 3: continue

            tarih_str = row[0].split(' ')[0]
            tarih_dt = datetime.strptime(tarih_str, "%Y-%m-%d")
            kategori = row[1]
            miktar = float(row[2])

            if filtre_kategori != "Tüm Kategoriler" and kategori != filtre_kategori:
                continue
            
            if filtre_tipi == "Bu Ay" and (tarih_dt.year != now.year or tarih_dt.month != now.month):
                continue
            elif filtre_tipi == "Bu Yıl" and (tarih_dt.year != now.year):
                continue
            elif filtre_tipi == "Son 7 Gün" and (now - tarih_dt).days >= 7: 
                continue
            
            filtered_records.append(row)
            toplam += miktar
        except:
            continue

    for i, row in enumerate(filtered_records):
        tag = "even" if i % 2 == 0 else "odd"
        tree.insert("", tk.END, values=row, tags=(tag,))
        
    toplam_label.configure(text=f"💰 Toplam Harcama: {toplam:.2f} TL")
    guncelle_grafik(filtered_records) 


def guncelle_grafik(records=None):
    for widget in graph_frame.winfo_children():
        widget.destroy() 

    if records is None: records = get_all_records()
    
    kategori_say = {}
    aylik_toplam = {}

    for row in records:
        try:
            tarih_dt = datetime.strptime(row[0].split(' ')[0], "%Y-%m-%d") 
            kategori = row[1]
            miktar = float(row[2])
            
            kategori_say[kategori] = kategori_say.get(kategori, 0) + miktar
            
            ay_yil = tarih_dt.strftime("%Y-%m")
            aylik_toplam[ay_yil] = aylik_toplam.get(ay_yil, 0) + miktar
        except:
            continue
            

    fig_pie = Figure(figsize=(4, 4), dpi=100)
    ax_pie = fig_pie.add_subplot(111)

    if kategori_say:
        ax_pie.pie(kategori_say.values(), labels=kategori_say.keys(), autopct="%1.1f%%", startangle=90)
        ax_pie.set_title("Kategori Dağılımı", fontsize=10)
    else:
        ax_pie.text(0.5, 0.5, "Veri yok", ha="center", va="center")

    canvas_pie = FigureCanvasTkAgg(fig_pie, master=graph_frame)
    canvas_pie.draw()
    canvas_pie.get_tk_widget().pack(side="left", fill="both", expand=True)

    fig_bar = Figure(figsize=(4, 4), dpi=100)
    ax_bar = fig_bar.add_subplot(111)
    
    if aylik_toplam:
        aylar = sorted(aylik_toplam.keys())
        miktarlar = [aylik_toplam[ay] for ay in aylar]
        
        ax_bar.bar(aylar, miktarlar, color='skyblue')
        ax_bar.set_title("Aylık Toplam Harcama", fontsize=10)
        ax_bar.set_ylabel("Miktar (TL)", fontsize=8)
        ax_bar.tick_params(axis='x', rotation=45, labelsize=7)
        ax_bar.tick_params(axis='y', labelsize=8)
        fig_bar.tight_layout()
    else:
        ax_bar.text(0.5, 0.5, "Aylık Veri yok", ha="center", va="center")

    canvas_bar = FigureCanvasTkAgg(fig_bar, master=graph_frame)
    canvas_bar.draw()
    canvas_bar.get_tk_widget().pack(side="right", fill="both", expand=True)


ctk.set_appearance_mode("light")  
ctk.set_default_color_theme("blue")  

root = ctk.CTk()
root.title("💸 Harcama Takip Uygulaması")
root.geometry("1200x650") 

title_label = ctk.CTkLabel(root, text="💸 Harcama Takip Sistemi",
                           font=ctk.CTkFont(size=20, weight="bold"))
title_label.pack(pady=15)

input_frame = ctk.CTkFrame(root)
input_frame.pack(padx=10, pady=10, fill="x")


ctk.CTkLabel(input_frame, text="Tarih (Y-M-D):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
tarih_entry = ctk.CTkEntry(input_frame, width=150, placeholder_text=datetime.now().strftime("%Y-%m-%d"))
tarih_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
tarih_entry.insert(0, datetime.now().strftime("%Y-%m-%d")) 


ctk.CTkLabel(input_frame, text="Saat (HH:MM):").grid(row=0, column=2, padx=5, pady=5, sticky="e")
zaman_entry = ctk.CTkEntry(input_frame, width=100, placeholder_text=datetime.now().strftime("%H:%M"))
zaman_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")
zaman_entry.insert(0, datetime.now().strftime("%H:%M"))

ctk.CTkLabel(input_frame, text="Kategori:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
kategori_entry = ctk.CTkEntry(input_frame, width=150, placeholder_text="örn: Eğlence")
kategori_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

ctk.CTkLabel(input_frame, text="Miktar (TL):").grid(row=1, column=2, padx=5, pady=5, sticky="e")
miktar_entry = ctk.CTkEntry(input_frame, width=100, placeholder_text="örn: 300.50")
miktar_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")

ctk.CTkLabel(input_frame, text="Açıklama:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
aciklama_entry = ctk.CTkEntry(input_frame, width=300, placeholder_text="örn: Bowling")
aciklama_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="w")


ekle_btn = ctk.CTkButton(input_frame, text="➕ Harcama Ekle",
                         command=lambda: harcama_ekle(
                             kategori_entry.get(), miktar_entry.get(), aciklama_entry.get(), tarih_entry.get(), zaman_entry.get()
                         ))
ekle_btn.grid(row=3, column=0, columnspan=2, pady=10) 


sifirla_btn = ctk.CTkButton(input_frame, text="✨ Yeni Harcama Kaydı",
                             command=harcama_ekle_mode, fg_color="gray", hover_color="#555555")
sifirla_btn.grid(row=3, column=2, columnspan=2, pady=10) 

# 📊 Sol (tablo) + Sağ (grafik) layout
main_frame = ctk.CTkFrame(root)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Sol: Harcama Tablosu
table_frame = ctk.CTkFrame(main_frame)
table_frame.pack(side="left", fill="both", expand=True, padx=(0,5)) 

columns = ("Tarih", "Kategori", "Miktar", "Açıklama")
tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15) 

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=125)

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background="#dccdcd", foreground="black", rowheight=25,
                fieldbackground="#dee5e9", font=("Arial", 10))
style.map("Treeview", background=[("selected", "#C65F2B")])

tree.tag_configure("odd", background="#bdaee2")
tree.tag_configure("even", background="#a2cbf9")

tree.bind("<<TreeviewSelect>>", fill_form_for_edit) 

tree.pack(fill="both", expand=True)

graph_frame = ctk.CTkFrame(main_frame)
graph_frame.pack(side="right", fill="both", expand=True, padx=(5,0))

bottom_frame = ctk.CTkFrame(root)
bottom_frame.pack(fill="x", padx=10, pady=10)

toplam_label = ctk.CTkLabel(bottom_frame, text="💰 Toplam Harcama: 0 TL",
                            font=ctk.CTkFont(size=14, weight="bold"))
toplam_label.pack(side="left", padx=10)

kategori_combobox = ctk.CTkComboBox(bottom_frame, values=[], width=150)
kategori_combobox.pack(side="left", padx=10)
kategori_combobox.set("Tüm Kategoriler") 

zaman_filtre_combobox = ctk.CTkComboBox(bottom_frame, 
                                        values=["Tüm Zamanlar", "Bu Ay", "Bu Yıl", "Son 7 Gün"], 
                                        width=150)
zaman_filtre_combobox.pack(side="left", padx=10)
zaman_filtre_combobox.set("Tüm Zamanlar")

filtre_btn = ctk.CTkButton(bottom_frame, text="🔍 Filtrele",
                            command=lambda: listele_harcamalar(kategori_combobox.get(), zaman_filtre_combobox.get()))
filtre_btn.pack(side="left", padx=5)

temizle_btn = ctk.CTkButton(bottom_frame, text="♻️ Tümünü Göster",
                            command=lambda: listele_harcamalar("Tüm Kategoriler", "Tüm Zamanlar"))
temizle_btn.pack(side="left", padx=5)

sil_btn = ctk.CTkButton(bottom_frame, text="🗑️ Seçili Harcamayı Sil",
                        command=harcama_sil, fg_color="#e74c3c", hover_color="#c0392b")
sil_btn.pack(side="left", padx=10)

export_btn = ctk.CTkButton(bottom_frame, text="💾 Verileri Dışa Aktar (CSV)",
                           command=verileri_disa_aktar, fg_color="#27ae60", hover_color="#2ecc71")
export_btn.pack(side="left", padx=10)


init_file()
kategori_guncelle() 
listele_harcamalar("Tüm Kategoriler", "Tüm Zamanlar") 

root.mainloop()
