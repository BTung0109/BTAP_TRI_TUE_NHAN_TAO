# sa_to_board_print.py
# Simulated Annealing cho 8 con xe
# In ra console và hiển thị LẦN LƯỢT các "vị trí hợp lí" (accepted & cost <= threshold)
# Có GUI Tkinter: bàn trái trống, bàn phải hiển thị trạng thái được in/ghi nhận.

import tkinter as tk
import random
import math
from copy import deepcopy
import time

# ====== Cau hinh chung ======
BAN_CO = 8
O_VUONG = 56
LE = 12
MAU_SANG = "#EEEED2"
MAU_TOI = "#769656"

# ====== Ham tinh cost (so cap xung dot theo cot) ======
def tinh_cost(trang_thai):
    dem_cot = {}
    for c in trang_thai:
        dem_cot[c] = dem_cot.get(c, 0) + 1
    dem = 0
    for v in dem_cot.values():
        if v > 1:
            dem += v * (v - 1) // 2
    return dem

# ====== Tao lan can (neighbor) ======
def tao_lan_can(trang_thai):
    """Tra ve (trang_thai_moi, hang, cot_from, cot_to)"""
    n = BAN_CO
    nh = list(trang_thai)
    hang = random.randrange(n)
    cot_from = nh[hang]
    ung = [c for c in range(n) if c != cot_from]
    cot_to = random.choice(ung)
    nh[hang] = cot_to
    return nh, hang, cot_from, cot_to

# ====== GUI chinh ======
class GiaoDienSAInLenBanCo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("8 con xe — SA (In ra & Hien thi len ban co)")
        rong = (BAN_CO * O_VUONG) * 2 + 380
        cao = BAN_CO * O_VUONG + LE * 6 + 160
        self.geometry(f"{rong}x{cao}")
        self.resizable(False, False)

        # khung chinh
        khung = tk.Frame(self, bg=self.cget("bg"))
        khung.pack(fill=tk.BOTH, expand=True, padx=LE, pady=LE)

        # ban co trai (trong)
        khung_trai = tk.Frame(khung)
        khung_trai.pack(side=tk.LEFT, padx=(0, LE))
        tk.Label(khung_trai, text="Bàn cờ trống", font=("Segoe UI", 11, "bold")).pack(pady=(0,6))
        self.banco_trai = tk.Canvas(khung_trai, width=BAN_CO*O_VUONG, height=BAN_CO*O_VUONG, highlightthickness=0)
        self.banco_trai.pack()
        self.ve_banco(self.banco_trai)

        # ban co phai (hien thi trang thai minh muon in)
        khung_phai = tk.Frame(khung)
        khung_phai.pack(side=tk.LEFT, padx=(LE,0))
        tk.Label(khung_phai, text="Bàn cờ (hiển thị vị trí hợp lí được in)", font=("Segoe UI", 11, "bold")).pack(pady=(0,6))
        self.banco_phai = tk.Canvas(khung_phai, width=BAN_CO*O_VUONG, height=BAN_CO*O_VUONG, highlightthickness=0)
        self.banco_phai.pack()
        self.ve_banco(self.banco_phai)

        # tham so
        khung_thamso = tk.Frame(self)
        khung_thamso.pack(pady=(8,4), anchor="w")

        tk.Label(khung_thamso, text="T0:").grid(row=0, column=0, sticky="e")
        self.entry_T0 = tk.Entry(khung_thamso, width=6, justify="center"); self.entry_T0.insert(0,"10.0"); self.entry_T0.grid(row=0,column=1,padx=(6,12))

        tk.Label(khung_thamso, text="alpha:").grid(row=0, column=2, sticky="e")
        self.entry_alpha = tk.Entry(khung_thamso, width=6, justify="center"); self.entry_alpha.insert(0,"0.95"); self.entry_alpha.grid(row=0,column=3,padx=(6,12))

        tk.Label(khung_thamso, text="Buoc/T:").grid(row=0, column=4, sticky="e")
        self.entry_buoc = tk.Entry(khung_thamso, width=6, justify="center"); self.entry_buoc.insert(0,"100"); self.entry_buoc.grid(row=0,column=5,padx=(6,12))

        tk.Label(khung_thamso, text="Delay(ms):").grid(row=0, column=6, sticky="e")
        self.entry_delay = tk.Entry(khung_thamso, width=6, justify="center"); self.entry_delay.insert(0,"5"); self.entry_delay.grid(row=0,column=7,padx=(6,12))

        tk.Label(khung_thamso, text="Threshold (in):").grid(row=1, column=0, sticky="e")
        self.entry_threshold = tk.Entry(khung_thamso, width=6, justify="center"); self.entry_threshold.insert(0,"0"); self.entry_threshold.grid(row=1,column=1,padx=(6,12))

        tk.Label(khung_thamso, text="Max buoc:").grid(row=1, column=2, sticky="e")
        self.entry_maxbuoc = tk.Entry(khung_thamso, width=8, justify="center"); self.entry_maxbuoc.insert(0,"20000"); self.entry_maxbuoc.grid(row=1,column=3,padx=(6,12))

        tk.Label(khung_thamso, text="Seed (None):").grid(row=1, column=4, sticky="e")
        self.entry_seed = tk.Entry(khung_thamso, width=8, justify="center"); self.entry_seed.insert(0,""); self.entry_seed.grid(row=1,column=5,padx=(6,12))

        # nut
        khung_nut = tk.Frame(self)
        khung_nut.pack(pady=(6,4), anchor="w")
        self.nut_giai = tk.Button(khung_nut, text="Giai (SA)", command=self.bat_dau_sa, width=12)
        self.nut_giai.grid(row=0,column=0,padx=6)
        self.nut_dung = tk.Button(khung_nut, text="Dung", command=self.dung_sa, width=10, state=tk.DISABLED)
        self.nut_dung.grid(row=0,column=1,padx=6)
        self.nut_reset = tk.Button(khung_nut, text="Reset", command=self.reset_sa, width=10)
        self.nut_reset.grid(row=0,column=2,padx=6)

        # thong tin va listbox lich su cac vi tri da in
        self.thong_tin = tk.Label(self, text="Chua chay SA", font=("Segoe UI", 10))
        self.thong_tin.pack(pady=(4,6), anchor="w")

        khung_lichsu = tk.Frame(self)
        khung_lichsu.place(x=(BAN_CO*O_VUONG)*2 + 40, y=20)

        tk.Label(khung_lichsu, text="Vị trí hợp lí (in/hiện):", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.listbox = tk.Listbox(khung_lichsu, width=48, height=30)
        self.listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.scrollbar = tk.Scrollbar(khung_lichsu, orient=tk.VERTICAL, command=self.listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.listbox.bind("<<ListboxSelect>>", self.on_chon_item)

        # trang thai ban dau
        self._dang_chay = False
        self._trang_thai = [i for i in range(BAN_CO)]  # default: hang i -> cot i
        self._best = list(self._trang_thai)
        self._best_cost = tinh_cost(self._best)

        # thong ke
        self._global_step = 0
        self._accepted_count = 0
        self._printed_count = 0
        self._printed_records = []

        # ve trang thai ban dau len ban phai
        self.ve_xe(self.banco_phai, self._trang_thai)

    # ---- ve ban co + xe ----
    def ve_banco(self, canvas):
        canvas.delete("square")
        for r in range(BAN_CO):
            for c in range(BAN_CO):
                x1 = c*O_VUONG; y1 = r*O_VUONG
                x2 = x1 + O_VUONG; y2 = y1 + O_VUONG
                mau = MAU_TOI if (r + c) % 2 else MAU_SANG
                canvas.create_rectangle(x1, y1, x2, y2, fill=mau, outline=mau, tags="square")

    def ve_xe(self, canvas, trang_thai):
        canvas.delete("piece")
        for r, c in enumerate(trang_thai):
            cx = c*O_VUONG + O_VUONG/2
            cy = r*O_VUONG + O_VUONG/2 + 2
            fill = "white" if ((r + c) % 2 == 1) else "black"
            canvas.create_text(cx, cy, text="♖", font=("Segoe UI Symbol", int(O_VUONG*0.75), "bold"), fill=fill, tags="piece")

    # ---- bat dau SA ----
    def bat_dau_sa(self):
        # doc tham so tu entry
        try:
            T0 = float(self.entry_T0.get())
            alpha = float(self.entry_alpha.get())
            buoc_tren_T = int(self.entry_buoc.get())
            delay = int(self.entry_delay.get())
            threshold = int(self.entry_threshold.get())
            max_buoc = int(self.entry_maxbuoc.get())
            seed_txt = self.entry_seed.get().strip()
            seed = int(seed_txt) if seed_txt != "" else None
        except Exception as e:
            self.thong_tin.config(text="Tham số không hợp lệ")
            return

        # seed
        if seed is not None:
            random.seed(seed)

        # khoi tao trang thai bat dau random
        self._trang_thai = [random.randrange(BAN_CO) for _ in range(BAN_CO)]
        self._best = list(self._trang_thai); self._best_cost = tinh_cost(self._best)

        # reset thong ke va listbox
        self._global_step = 0
        self._accepted_count = 0
        self._printed_count = 0
        self._printed_records.clear()
        self.listbox.delete(0, tk.END)

        # in thong tin ban dau ra console
        print("=== SA START ===", flush=True)
        print(f"T0={T0}, alpha={alpha}, buoc_tren_T={buoc_tren_T}, max_buoc={max_buoc}, threshold={threshold}, seed={seed}", flush=True)
        print("Ban dau:", self._trang_thai, "cost=", self._best_cost, flush=True)
        print("-"*70, flush=True)
        print("#step | cost |   T    | A/R | hang:from->to | state", flush=True)
        print("-"*70, flush=True)

        # neu state ban dau hop le va muon in luon
        if self._best_cost <= threshold:
            self._printed_count += 1
            rec = {"step": 0, "trang_thai": deepcopy(self._trang_thai), "cost": self._best_cost, "T": T0, "accepted": True, "note":"init"}
            self._printed_records.append(rec)
            self.listbox.insert(tk.END, f"#00000 | cost={self._best_cost} | T={T0:.4f} | A | init      | {self._trang_thai}")
            print(f"#00000 | {self._best_cost:4d} | {T0:7.4f} | A   | init      | {self._trang_thai}", flush=True)
            self.ve_xe(self.banco_phai, self._trang_thai)

        # set cac bien luu va bat dau vong lap khong block UI
        self._T = float(T0)
        self._alpha = float(alpha)
        self._buoc_tren_T = int(buoc_tren_T)
        self._delay = int(delay)
        self._threshold = int(threshold)
        self._max_buoc = int(max_buoc)

        self._dang_chay = True
        self.nut_giai.config(state=tk.DISABLED)
        self.nut_dung.config(state=tk.NORMAL)
        self.nut_reset.config(state=tk.DISABLED)
        self.thong_tin.config(text=f"SA dang chay... T={self._T:.4f}")

        # bat dau mot vong lap
        self.after(self._delay, self._buoc_sa)

    # ---- moi buoc chinh cua SA (non-blocking) ----
    def _buoc_sa(self):
        if not self._dang_chay:
            return

        buoc_trong_level = 0
        # lap them _buoc_tren_T lan moi goi
        for _ in range(self._buoc_tren_T):
            if not self._dang_chay:
                break
            if self._global_step >= self._max_buoc:
                self._dang_chay = False
                break

            trang_thai_moi, hang, cot_from, cot_to = tao_lan_can(self._trang_thai)
            cost_ht = tinh_cost(self._trang_thai)
            cost_moi = tinh_cost(trang_thai_moi)
            delta = cost_moi - cost_ht

            if delta <= 0:
                chap_nhan = True
            else:
                p = math.exp(-delta / self._T) if self._T > 0 else 0.0
                chap_nhan = (random.random() < p)

            self._global_step += 1
            buoc_trong_level += 1

            if chap_nhan:
                self._accepted_count += 1
                self._trang_thai = trang_thai_moi
                # cap nhat best
                if cost_moi < self._best_cost:
                    self._best = list(self._trang_thai)
                    self._best_cost = cost_moi

            # Neu chap nhan AND cost_moi <= threshold -> in + hien thi len ban co + luu vao listbox
            if chap_nhan and cost_moi <= self._threshold:
                self._printed_count += 1
                rec = {
                    "step": self._global_step,
                    "trang_thai": deepcopy(trang_thai_moi),
                    "cost": cost_moi,
                    "T": self._T,
                    "accepted": chap_nhan,
                    "hang": hang,
                    "from": cot_from,
                    "to": cot_to
                }
                self._printed_records.append(rec)
                # in ra console luon
                print(f"#{self._global_step:05d} | {cost_moi:4d} | {self._T:7.4f} | A   | {hang}:{cot_from}->{cot_to} | {trang_thai_moi}", flush=True)
                # them vao listbox
                self.listbox.insert(tk.END, f"#{self._global_step:05d} | cost={cost_moi} | T={self._T:.4f} | A | {hang}:{cot_from}->{cot_to} | {trang_thai_moi}")
                self.listbox.yview_moveto(1.0)
                # hien thi len ban co phai
                self.ve_xe(self.banco_phai, trang_thai_moi)
                # cap nhat thong tin label
                self.thong_tin.config(text=f"Step {self._global_step} | cost={cost_moi} | T={self._T:.4f} | In/Hiện step")
                # cap nhat giao dien de nguoi dung thay doi nhin duoc
                self.update_idletasks()

            # neu tim duoc nghiem tuyet doi -> dung ngay
            if self._best_cost == 0:
                self._dang_chay = False
                break

        # ket thuc mot level -> lam mat T
        self._T *= self._alpha
        # cap nhat tren nhan thong tin
        if self._dang_chay:
            self.thong_tin.config(text=f"SA dang chay... T={self._T:.6f} | Step={self._global_step}")
            self.after(self._delay, self._buoc_sa)
        else:
            # da dung -> in thong ke va cap nhat UI
            self.ket_thuc_va_in_thong_ke()

    # ---- khi dung SA ----
    def dung_sa(self):
        self._dang_chay = False
        self.nut_dung.config(state=tk.DISABLED)
        self.nut_giai.config(state=tk.NORMAL)
        self.nut_reset.config(state=tk.NORMAL)
        self.thong_tin.config(text=f"Dừng. Best cost = {self._best_cost}. Steps = {self._global_step}")

    # ---- ket thuc va in thong ke ----
    def ket_thuc_va_in_thong_ke(self):
        # in thong ke ra console
        print("-"*70, flush=True)
        print("=== SA FINISHED ===", flush=True)
        print(f"Total steps: {self._global_step}, Accepted steps: {self._accepted_count}, Printed steps: {self._printed_count}", flush=True)
        print(f"Best cost = {self._best_cost}, Best state = {self._best}", flush=True)
        print("Parameters used:")
        print(f"  T0={self.entry_T0.get()}, alpha={self.entry_alpha.get()}, buoc_tren_T={self.entry_buoc.get()}, max_buoc={self.entry_maxbuoc.get()}, threshold={self.entry_threshold.get()}, seed={self.entry_seed.get()}", flush=True)
        print("-"*70, flush=True)

        # cap nhat UI
        self.nut_dung.config(state=tk.DISABLED)
        self.nut_giai.config(state=tk.NORMAL)
        self.nut_reset.config(state=tk.NORMAL)
        self.thong_tin.config(text=f"Finished. Best cost={self._best_cost}. Steps={self._global_step}")

    # ---- khi click 1 dong trong listbox -> hien thi trang thai do len ban co phai ----
    def on_chon_item(self, event):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx < 0 or idx >= len(self._printed_records):
            return
        rec = self._printed_records[idx]
        self.ve_xe(self.banco_phai, rec["trang_thai"])
        self.thong_tin.config(text=f"Step {rec['step']} | cost={rec['cost']} | T={rec['T']:.4f} | accepted={rec['accepted']}")

    # ---- reset ve ban dau ----
    def reset_sa(self):
        self._dang_chay = False
        self._trang_thai = [i for i in range(BAN_CO)]
        self._best = list(self._trang_thai)
        self._best_cost = tinh_cost(self._best)
        self._global_step = 0
        self._accepted_count = 0
        self._printed_count = 0
        self._printed_records.clear()
        self.listbox.delete(0, tk.END)
        self.ve_xe(self.banco_phai, self._trang_thai)
        self.thong_tin.config(text="Đã reset. Sẵn sàng chạy SA.")
        self.nut_giai.config(state=tk.NORMAL)
        self.nut_dung.config(state=tk.DISABLED)

if __name__ == "__main__":
    app = GiaoDienSAInLenBanCo()
    app.mainloop()
