import tkinter as tk
import heapq
from itertools import count


BAN_CO = 8
O_VUONG = 64
LE = 16
MAU_SANG = "#EEEED2"
MAU_TOI = "#769656"

# ====== A* cho 8 con xe ======
def astar_nghiem_xe():

    n = BAN_CO
    pq = []  # priority queue: (f, tie, g, trang_thai)
    tie = count()
    khoi_tao = []
    g0 = 0
    h0 = n - g0
    f0 = g0 + h0
    heapq.heappush(pq, (f0, next(tie), g0, khoi_tao))

    while pq:
        f, _, g, trang_thai = heapq.heappop(pq)
        hang = len(trang_thai)
        # Goal check
        if hang == n:
            yield [(r, trang_thai[r]) for r in range(n)]
            continue

        cot_da_dung = set(trang_thai)
        # expand: dat xe o hang (hang) vao tat ca cot chua dung
        for cot in range(n):
            if cot in cot_da_dung:
                continue
            trang_thai_moi = trang_thai + [cot]
            g_moi = g + 1
            h_moi = n - len(trang_thai_moi)  # so xe con phai dat
            f_moi = g_moi + h_moi
            heapq.heappush(pq, (f_moi, next(tie), g_moi, trang_thai_moi))


# ====== Giao dien Tkinter ======
class GiaoDien8XeAStar(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("8 con xe — A*")
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
        tk.Label(khung_phai, text="Ban co (nghiem A*)", font=("Segoe UI", 12, "bold")).pack(pady=(0, 4))
        self.banco_phai = tk.Canvas(khung_phai, width=BAN_CO * O_VUONG, height=BAN_CO * O_VUONG, highlightthickness=0)
        self.banco_phai.pack()
        self.ve_banco(self.banco_phai)

        # Thanh dieu khien
        khung_nut = tk.Frame(self)
        khung_nut.pack(pady=(8, 4))
        self.nut_giai = tk.Button(khung_nut, text="Giai (A*)", command=self.bam_giai, width=14)
        self.nut_giai.grid(row=0, column=0, padx=6)

        self.nut_tiep = tk.Button(khung_nut, text="Nghiem tiep ▶", command=self.bam_tiep, width=14, state=tk.DISABLED)
        self.nut_tiep.grid(row=0, column=1, padx=6)

        self.nut_dung = tk.Button(khung_nut, text="Dung", command=self.bam_dung, width=10, state=tk.DISABLED)
        self.nut_dung.grid(row=0, column=2, padx=6)

        self.trang_thai = tk.Label(khung_nut, text="Chua chay A*", font=("Segoe UI", 10))
        self.trang_thai.grid(row=0, column=3, padx=10)

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
        # Khoi tao generator A* va hien nghiem dau tien
        self._sinh_nghiem = astar_nghiem_xe()
        self._so_nghiem = 0
        self.nut_tiep.config(state=tk.NORMAL)
        self.nut_dung.config(state=tk.NORMAL)
        self.trang_thai.config(text="Dang chay A*...")
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
            self.trang_thai.config(text=f"Nghiem #{self._so_nghiem} (A*)")
        except StopIteration:
            self.trang_thai.config(text=f"Het nghiem. Tong: {self._so_nghiem}")
            self.nut_tiep.config(state=tk.DISABLED)
            self.nut_dung.config(state=tk.DISABLED)
            self._sinh_nghiem = None


if __name__ == "__main__":
    app = GiaoDien8XeAStar()
    app.mainloop()
