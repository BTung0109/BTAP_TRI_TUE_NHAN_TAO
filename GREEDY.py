import tkinter as tk

# ====== Cau hinh giao dien ======
BAN_CO = 8
O_VUONG = 64
LE = 16
MAU_SANG = "#EEEED2"
MAU_TOI = "#769656"

# ====== Greedy cho 8 con xe ======
def greedy_nghiem_xe():

    n = BAN_CO
    trung_tam = (n - 1) / 2.0
    cot_da_dung = set()
    ket_qua = []

    for hang in range(n):
        # danh sach cac cot hop le chua duoc dung
        ung_cot = [c for c in range(n) if c not in cot_da_dung]
        if not ung_cot:
            # khong con cot -> that bai
            return None
        # tinh heuristic va chon cot nho nhat, tie-breaker: cot nho hon
        ung_cot.sort(key=lambda c: (abs(c - trung_tam), c))
        cot_chon = ung_cot[0]
        ket_qua.append((hang, cot_chon))
        cot_da_dung.add(cot_chon)

    return ket_qua


# ====== Giao dien Tkinter ======
class GiaoDien8XeGreedy(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("8 con xe — Greedy")
        rong = (BAN_CO * O_VUONG) * 2 + LE * 3
        cao = BAN_CO * O_VUONG + LE * 2 + 100
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
        tk.Label(khung_phai, text="Ban co (nghiem Greedy)", font=("Segoe UI", 12, "bold")).pack(pady=(0, 4))
        self.banco_phai = tk.Canvas(khung_phai, width=BAN_CO * O_VUONG, height=BAN_CO * O_VUONG, highlightthickness=0)
        self.banco_phai.pack()
        self.ve_banco(self.banco_phai)

        # Thanh dieu khien
        khung_nut = tk.Frame(self)
        khung_nut.pack(pady=(8, 4))
        self.nut_giai = tk.Button(khung_nut, text="Giai (Greedy)", command=self.bam_giai, width=14)
        self.nut_giai.grid(row=0, column=0, padx=6)

        # Greedy chi tra 1 nghiem -> nut tiep vo hieu
        self.nut_tiep = tk.Button(khung_nut, text="Nghiem tiep ▶", command=self.bam_tiep, width=14, state=tk.DISABLED)
        self.nut_tiep.grid(row=0, column=1, padx=6)

        self.trang_thai = tk.Label(khung_nut, text="Chua chay Greedy", font=("Segoe UI", 10))
        self.trang_thai.grid(row=0, column=2, padx=10)

        # luu ket qua
        self._ket_qua = None
        self._da_hien = False

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
        self._ket_qua = greedy_nghiem_xe()
        self._da_hien = False
        if self._ket_qua is None:
            self.trang_thai.config(text="Greedy khong tim duoc nghiem")
            self.nut_tiep.config(state=tk.DISABLED)
            return
        self.ve_banco(self.banco_phai)
        self.ve_xe(self.banco_phai, self._ket_qua)
        self.trang_thai.config(text="Da hien nghiem Greedy (1 ket qua)")
        # Khong co nghiem tiep theo theo dung phuong phap greedy don gian
        self.nut_tiep.config(state=tk.DISABLED)
        self._da_hien = True

    def bam_tiep(self):
        # vo hieu, chi de dong giao dien tuong dong voi cac ung dung truoc
        pass


if __name__ == "__main__":
    app = GiaoDien8XeGreedy()
    app.mainloop()
