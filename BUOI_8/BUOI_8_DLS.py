import tkinter as tk

# ====== Cau hinh giao dien ======
BAN_CO = 8
O_VUONG = 64
LE = 16
MAU_SANG = "#EEEED2"
MAU_TOI = "#769656"

# ====== DLS (Depth-Limited Search) sinh nghiem 8 con xe ======
def dls_nghiem_xe(gioi_han):

    n = BAN_CO
    danh_sach = []

    def backtrack(hang, used_cols):
        # hang: so hang da dat (cung la len(danh_sach))
        # neu da vuot gioi han thi dung
        if hang > gioi_han:
            return
        if hang == n:
            # dat du 8 xe -> tra ve nghiem
            yield [(r, danh_sach[r]) for r in range(n)]
            return
        # neu hang == gioi_han ma < n thi khong du toi muc -> ko tiep tuc
        if hang == gioi_han and hang < n:
            return

        for cot in range(n):
            if cot in used_cols:
                continue
            # dat xe o (hang, cot)
            danh_sach.append(cot)
            used_cols.add(cot)
            # de quy
            yield from backtrack(hang + 1, used_cols)
            # quay lui
            used_cols.remove(cot)
            danh_sach.pop()

    yield from backtrack(0, set())


# ====== Giao dien Tkinter ======
class GiaoDien8XeDLS(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("8 con xe — DLS (Depth-Limited Search)")
        rong = (BAN_CO * O_VUONG) * 2 + LE * 3
        cao = BAN_CO * O_VUONG + LE * 2 + 120
        self.geometry(f"{rong}x{cao}")
        self.resizable(False, False)

        khung_chinh = tk.Frame(self, bg=self.cget("bg"))
        khung_chinh.pack(fill=tk.BOTH, expand=True, padx=LE, pady=LE)

        # Ban co trai (trong)
        khung_trai = tk.Frame(khung_chinh)
        khung_trai.pack(side=tk.LEFT, padx=(0, LE))
        tk.Label(khung_trai, text="Ban co trong (8x8)", font=("Segoe UI", 12, "bold")).pack(pady=(0, 4))
        self.banco_trai = tk.Canvas(khung_trai, width=BAN_CO * O_VUONG, height=BAN_CO * O_VUONG, highlightthickness=0)
        self.banco_trai.pack()
        self.ve_banco(self.banco_trai)

        # Ban co phai (co nghiem)
        khung_phai = tk.Frame(khung_chinh)
        khung_phai.pack(side=tk.LEFT, padx=(LE, 0))
        tk.Label(khung_phai, text="Ban co (nghiem DLS)", font=("Segoe UI", 12, "bold")).pack(pady=(0, 4))
        self.banco_phai = tk.Canvas(khung_phai, width=BAN_CO * O_VUONG, height=BAN_CO * O_VUONG, highlightthickness=0)
        self.banco_phai.pack()
        self.ve_banco(self.banco_phai)

        # Thanh dieu khien va tu chon gioi han
        khung_dieu_khien = tk.Frame(self)
        khung_dieu_khien.pack(pady=(8, 4))

        tk.Label(khung_dieu_khien, text="Gioi han (do sau):").grid(row=0, column=0)
        self.entry_gioi_han = tk.Entry(khung_dieu_khien, width=4, justify="center")
        self.entry_gioi_han.insert(0, "8")  # mac dinh 8
        self.entry_gioi_han.grid(row=0, column=1, padx=(4, 12))

        self.nut_giai = tk.Button(khung_dieu_khien, text="Giai (DLS)", command=self.bam_giai, width=12)
        self.nut_giai.grid(row=0, column=2, padx=6)

        self.nut_tiep = tk.Button(khung_dieu_khien, text="Nghiem tiep ▶", command=self.bam_tiep, width=12, state=tk.DISABLED)
        self.nut_tiep.grid(row=0, column=3, padx=6)

        self.nut_dung = tk.Button(khung_dieu_khien, text="Dung", command=self.bam_dung, width=8, state=tk.DISABLED)
        self.nut_dung.grid(row=0, column=4, padx=6)

        self.trang_thai = tk.Label(khung_dieu_khien, text="Chua chay DLS", font=("Segoe UI", 10))
        self.trang_thai.grid(row=0, column=5, padx=10)

        # Bien luu generator va thong tin
        self._sinh_nghiem = None
        self._so_nghiem = 0

    def ve_banco(self, canvas: tk.Canvas):
        canvas.delete("o_vuong")
        for r in range(BAN_CO):
            for c in range(BAN_CO):
                x1, y1 = c * O_VUONG, r * O_VUONG
                x2, y2 = x1 + O_VUONG, y1 + O_VUONG
                mau = MAU_TOI if (r + c) % 2 else MAU_SANG
                canvas.create_rectangle(x1, y1, x2, y2, fill=mau, outline=mau, tags="o_vuong")

    def ve_xe(self, canvas: tk.Canvas, vi_tri):
        canvas.delete("xe")
        for (r, c) in vi_tri:
            cx = c * O_VUONG + O_VUONG / 2
            cy = r * O_VUONG + O_VUONG / 2 + 2
            mau = "white" if ((r + c) % 2 == 1) else "black"
            canvas.create_text(cx, cy, text="♖", font=("Segoe UI Symbol", int(O_VUONG * 0.75), "bold"), fill=mau, tags="xe")

    def bam_giai(self):
        # doc gioi han tu entry
        try:
            gioi_han = int(self.entry_gioi_han.get())
            if gioi_han < 0:
                raise ValueError
        except ValueError:
            self.trang_thai.config(text="Gioi han phai la so nguyen >= 0")
            return

        self._sinh_nghiem = dls_nghiem_xe(gioi_han)
        self._so_nghiem = 0
        self.nut_tiep.config(state=tk.NORMAL)
        self.nut_dung.config(state=tk.NORMAL)
        self.trang_thai.config(text=f"Dang chay DLS (gioi_han={gioi_han})...")
        # hien nghiem dau tien neu co
        self.hien_nghiem_tiep()

    def bam_tiep(self):
        self.hien_nghiem_tiep()

    def bam_dung(self):
        self._sinh_nghiem = None
        self.nut_tiep.config(state=tk.DISABLED)
        self.nut_dung.config(state=tk.DISABLED)
        self.trang_thai.config(text=f"Dung. Tong nghiem da xem: {self._so_nghiem}")

    def hien_nghiem_tiep(self):
        if self._sinh_nghiem is None:
            return
        try:
            nghiem = next(self._sinh_nghiem)
            self._so_nghiem += 1
            self.ve_banco(self.banco_phai)
            self.ve_xe(self.banco_phai, nghiem)
            self.trang_thai.config(text=f"Nghiem #{self._so_nghiem} (DLS)")
        except StopIteration:
            self.trang_thai.config(text=f"Het nghiem hoac het pham vi. Tong: {self._so_nghiem}")
            self.nut_tiep.config(state=tk.DISABLED)
            self.nut_dung.config(state=tk.DISABLED)
            self._sinh_nghiem = None


if __name__ == "__main__":
    app = GiaoDien8XeDLS()
    app.mainloop()
