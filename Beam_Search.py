# beam_search_8xe_gui_fixed.py
# Beam Search cho bài toán 8 con xe — GUI Tkinter (đã fix: phát hiện tất cả solutions trong candidates trước khi prune)

import tkinter as tk
from tkinter import messagebox
from copy import deepcopy
import time

# ====== Cấu hình bài toán ======
BAN_CO = 8

def tinh_cost(trang_thai):
    dem_cot = {}
    for c in trang_thai:
        dem_cot[c] = dem_cot.get(c, 0) + 1
    dem = 0
    for v in dem_cot.values():
        if v > 1:
            dem += v * (v - 1) // 2
    return dem

class GiaoDienBeamSearchFixed(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Beam Search — 8 con xe (fixed)")
        try:
            self.state('zoomed')
        except Exception:
            self.attributes('-fullscreen', True)

        self.update_idletasks()
        self.scr_w = self.winfo_screenwidth()
        self.scr_h = self.winfo_screenheight()

        max_board_width = int(self.scr_w * 0.60)
        size_from_height = (self.scr_h - 260) // BAN_CO
        size_from_width = max_board_width // (2 * BAN_CO)
        self.o_size = max(28, min(size_from_height, size_from_width))

        total_board_width = 2 * BAN_CO * self.o_size
        left_x = int((self.scr_w - total_board_width - 520) // 2)
        top_y = 140
        self.left_origin = (left_x, top_y)
        self.right_origin = (left_x + BAN_CO * self.o_size + 28, top_y)

        self.canvas = tk.Canvas(self, width=self.scr_w, height=self.scr_h, bg="#f8f8f8")
        self.canvas.pack(fill="both", expand=True)

        self.build_controls()
        self.build_listbox()

        self.reset_state()
        self.draw_board(self.left_origin, side="left", state=[])
        self.draw_board(self.right_origin, side="right", state=self._beam_best_state())

    def build_controls(self):
        frm = tk.Frame(self)
        self.canvas.create_window(self.scr_w//2, 34, window=frm)
        tk.Label(frm, text="Beam Search (8 rooks) — fixed", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=12, pady=(0,6))

        tk.Label(frm, text="Beam width (k):").grid(row=1, column=0, sticky="e")
        self.ent_width = tk.Entry(frm, width=6); self.ent_width.insert(0, "20"); self.ent_width.grid(row=1, column=1, padx=6)

        tk.Label(frm, text="Max depth:").grid(row=1, column=2, sticky="e")
        self.ent_depth = tk.Entry(frm, width=6); self.ent_depth.insert(0, str(BAN_CO)); self.ent_depth.grid(row=1, column=3, padx=6)

        tk.Label(frm, text="Max expansions:").grid(row=1, column=4, sticky="e")
        self.ent_maxexp = tk.Entry(frm, width=8); self.ent_maxexp.insert(0, "20000"); self.ent_maxexp.grid(row=1, column=5, padx=6)

        tk.Label(frm, text="Tốc độ (ms):").grid(row=1, column=6, sticky="e")
        self.sld_speed = tk.Scale(frm, from_=50, to=2000, orient=tk.HORIZONTAL, length=200)
        self.sld_speed.set(300)
        self.sld_speed.grid(row=1, column=7, columnspan=2, padx=6)

        btn_frm = tk.Frame(self)
        self.canvas.create_window(self.scr_w//2, 106, window=btn_frm)
        self.btn_start = tk.Button(btn_frm, text="Start", width=12, command=self.start_search)
        self.btn_start.grid(row=0, column=0, padx=6)
        self.btn_stop = tk.Button(btn_frm, text="Stop", width=10, command=self.stop_search, state=tk.DISABLED)
        self.btn_stop.grid(row=0, column=1, padx=6)
        self.btn_reset = tk.Button(btn_frm, text="Reset", width=10, command=self.reset_state)
        self.btn_reset.grid(row=0, column=2, padx=6)

        self.btn_next = tk.Button(btn_frm, text="Next level ▶", width=12, command=self.next_level, state=tk.DISABLED)
        self.btn_next.grid(row=0, column=3, padx=6)
        self.auto_var = tk.BooleanVar(value=False)
        self.chk_auto = tk.Checkbutton(btn_frm, text="Auto", variable=self.auto_var, command=self.on_toggle_auto)
        self.chk_auto.grid(row=0, column=4, padx=6)

        self.lbl_status = tk.Label(self, text="Ready", font=("Segoe UI", 10))
        self.canvas.create_window(self.scr_w//2, 136, window=self.lbl_status)

    def build_listbox(self):
        frame = tk.Frame(self, bg="#ffffff")
        x = self.right_origin[0] + BAN_CO * self.o_size + 48
        y = 76
        self.canvas.create_window(x, y, window=frame, anchor="nw")
        tk.Label(frame, text="Beam kept states + SOLs (click để xem)", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.lst = tk.Listbox(frame, width=78, height=36)
        self.lst.pack(side="left", fill="y")
        sb = tk.Scrollbar(frame, orient="vertical", command=self.lst.yview)
        sb.pack(side="right", fill="y")
        self.lst.config(yscrollcommand=sb.set)
        self.lst.bind("<<ListboxSelect>>", self.on_select_state)

    def _beam_best_state(self):
        if not self._beam:
            return [i for i in range(BAN_CO)]
        best = min(self._beam, key=lambda s: (tinh_cost(s), -len(s)))
        return best

    def reset_state(self):
        self._beam = [[]]
        self._level = 0
        self._max_depth = BAN_CO
        self._max_expansions = 20000
        self._expansions_done = 0
        self._running = False
        self._auto = False
        self._waiting = False
        self._found_solutions = []   # list of unique solution states (tuples)
        self._found_set = set()
        self.lst.delete(0, tk.END)
        self.btn_next.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_start.config(state=tk.NORMAL)
        self.chk_auto.deselect()
        self.draw_board(self.left_origin, side="left", state=[])
        self.draw_board(self.right_origin, side="right", state=self._beam_best_state())
        self.lbl_status.config(text="Reset. Beam chỉ có trạng thái rỗng.")

    def draw_board(self, origin, side="right", state=None):
        x0, y0 = origin
        s = self.o_size
        w = BAN_CO * s
        h = BAN_CO * s
        tag_board = f"board_{side}"
        tag_piece = f"piece_{side}"
        tag_high = f"high_{side}"

        self.canvas.delete(tag_high)
        self.canvas.delete(tag_piece)
        self.canvas.delete(tag_board)

        self.canvas.create_rectangle(x0 - 2, y0 - 2, x0 + w + 2, y0 + h + 2,
                                     fill="#f8f8f8", outline="#f8f8f8", tags=(tag_board,))

        for r in range(BAN_CO):
            for c in range(BAN_CO):
                color = "#EEEED2" if (r + c) % 2 == 0 else "#769656"
                self.canvas.create_rectangle(x0 + c*s, y0 + r*s, x0 + (c+1)*s, y0 + (r+1)*s,
                                             fill=color, outline=color, tags=(tag_board,))

        if state:
            for r, c in enumerate(state):
                cx = x0 + c*s + s//2
                cy = y0 + r*s + s//2
                self.canvas.create_text(cx, cy, text="♖", font=("Segoe UI", s//2, "bold"),
                                        fill="black", tags=(tag_piece,))

        self.canvas.update()
        self.update_idletasks()

    def highlight_cell(self, origin, hang, cot, duration_ms=300):
        x0, y0 = origin
        s = self.o_size
        x1 = x0 + cot*s
        y1 = y0 + hang*s
        x2 = x1 + s
        y2 = y1 + s
        tag_high = f"high_{ 'left' if origin==self.left_origin else 'right' }"
        self.canvas.delete(tag_high)
        self.canvas.create_rectangle(x1+3, y1+3, x2-3, y2-3, outline="red", width=3, tags=(tag_high,))
        self.canvas.update()
        self.after(duration_ms, lambda: self.canvas.delete(tag_high))

    def start_search(self):
        try:
            self._beam_width = max(1, int(self.ent_width.get()))
            self._max_depth = max(1, int(self.ent_depth.get()))
            self._max_expansions = max(1, int(self.ent_maxexp.get()))
        except Exception:
            messagebox.showerror("Lỗi", "Tham số không hợp lệ")
            return
        self._expansions_done = 0
        self._running = True
        self._auto = self.auto_var.get()
        self._waiting = False
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_next.config(state=tk.NORMAL)
        self.lst.delete(0, tk.END)
        self._beam = [[]]
        self._level = 0
        self._found_solutions = []
        self._found_set = set()
        self.lbl_status.config(text=f"Beam chạy: width={self._beam_width}, max_depth={self._max_depth}")
        self.draw_board(self.right_origin, side="right", state=self._beam_best_state())
        if self._auto:
            self.after(10, self.next_level)
        else:
            self._waiting = True

    def stop_search(self):
        self._running = False
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_next.config(state=tk.DISABLED)
        self.lbl_status.config(text=f"Stopped. Expansions={self._expansions_done}. Found solutions={len(self._found_solutions)}")

    def on_toggle_auto(self):
        self._auto = self.auto_var.get()
        if self._auto and self._waiting:
            self._waiting = False
            self.after(10, self.next_level)

    def next_level(self):
        if not self._running:
            return
        if self._expansions_done >= self._max_expansions:
            self.lbl_status.config(text="Đã đạt giới hạn mở rộng (max expansions). Kết thúc.")
            self.stop_search()
            return
        if self._level >= self._max_depth:
            self.lbl_status.config(text="Đã đạt max depth.")
            self.stop_search()
            return

        # expand current beam -> danh_sach_moi
        danh_sach_moi = []   # list of (state, cost)
        for st in self._beam:
            hang_tiep = len(st)
            if hang_tiep >= self._max_depth:
                continue
            for cot in range(BAN_CO):
                st_moi = st + [cot]
                cost = tinh_cost(st_moi)
                danh_sach_moi.append((st_moi, cost))
                self._expansions_done += 1
                if self._expansions_done >= self._max_expansions:
                    break
            if self._expansions_done >= self._max_expansions:
                break

        # --- MỚI: trước khi prune, kiểm tra tất cả candidates xem có solution hoàn chỉnh không ---
        solutions_here = []
        if len(danh_sach_moi) > 0:
            for st, cost in danh_sach_moi:
                if len(st) == self._max_depth and cost == 0:
                    tup = tuple(st)
                    if tup not in self._found_set:
                        self._found_set.add(tup)
                        self._found_solutions.append(list(st))
                        solutions_here.append(list(st))
        # nếu có solution(s) ở level này thì liệt kê vào listbox (nhãn SOL)
        for sol in solutions_here:
            line = f"[SOL] level={self._level+1} | cost=0 | {sol}"
            self.lst.insert(tk.END, line)
            print("FOUND SOL:", sol, flush=True)

        # tiếp tục: prune để giữ beam_width tốt nhất
        # sort theo (cost asc, -len desc)
        danh_sach_moi.sort(key=lambda x: (x[1], -len(x[0])))
        # giữ top-k
        self._beam = [deepcopy(x[0]) for x in danh_sach_moi[:self._beam_width]]
        self._level += 1

        # cập nhật listbox với beam (ghi sau các SOL để ưu tiên SOL hiển thị)
        # (xóa các entry beam trước đó chỉ, nhưng giữ SOL entries)
        # để đơn giản: xóa toàn bộ rồi thêm SOLs trước, rồi beam
        sol_lines = [f"[SOL] level={self._level} | cost=0 | {s}" for s in self._found_solutions]
        self.lst.delete(0, tk.END)
        for l in sol_lines:
            self.lst.insert(tk.END, l)
        for idx, st in enumerate(self._beam):
            cost = tinh_cost(st)
            line = f"[Beam L{self._level}] #{idx+1} | len={len(st)} | cost={cost} | {st}"
            self.lst.insert(tk.END, line)

        # draw best beam state
        best = self._beam_best_state()
        self.draw_board(self.right_origin, side="right", state=best)

        # print summary
        print(f"Level {self._level} — kept {len(self._beam)} states (expansions={self._expansions_done})", flush=True)
        for st in self._beam:
            print(f"  kept: len={len(st)} cost={tinh_cost(st)} state={st}", flush=True)

        # nếu tìm được ít nhất 1 solution trong toàn bộ quá trình -> thông báo tạm thời (không stop toàn bộ)
        if self._found_solutions:
            self.lbl_status.config(text=f"Level {self._level} done. Found solutions so far: {len(self._found_solutions)}")
        else:
            self.lbl_status.config(text=f"Level {self._level} done. Expansions={self._expansions_done}")

        # decide auto vs manual
        if self._auto:
            delay = self.sld_speed.get()
            self.after(delay, self.next_level)
        else:
            self._waiting = True
            self.btn_next.config(state=tk.NORMAL)

    def on_select_state(self, event):
        sel = self.lst.curselection()
        if not sel:
            return
        idx = sel[0]
        raw = self.lst.get(idx)
        # parse a state from line (very simple parse: last token is state list)
        try:
            state_str = raw.split("|")[-1].strip()
            # eval is safe here because state_str looks like "[..]" (trusting local use)
            st = eval(state_str)
            self.draw_board(self.right_origin, side="right", state=st)
            self.lbl_status.config(text=f"Show: {st} | cost={tinh_cost(st)}")
        except Exception:
            pass

if __name__ == "__main__":
    app = GiaoDienBeamSearchFixed()
    app.mainloop()
