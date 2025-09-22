# Genetic_algorithm_print_control.py
# Genetic Algorithm cho 8 con xe — GUI Tkinter
# Sửa: thêm kiểm soát in (chỉ in khi best giảm / in mỗi N thế hệ / always)

import tkinter as tk
from tkinter import messagebox
import random
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

def fitness_of(state):
    return -tinh_cost(state)

# ====== Toán tử GA (safe) ======
def tao_individual_random():
    return [random.randrange(BAN_CO) for _ in range(BAN_CO)]

def tao_pop(pop_size):
    return [tao_individual_random() for _ in range(pop_size)]

def tournament_selection(pop, k=3):
    if not pop:
        raise ValueError("population empty in tournament_selection")
    k_use = min(k, len(pop))
    samp = random.sample(pop, k_use)
    best = max(samp, key=fitness_of)
    return deepcopy(best)

def one_point_crossover(p1, p2):
    if len(p1) != len(p2):
        return deepcopy(p1), deepcopy(p2)
    n = len(p1)
    if n <= 1:
        return deepcopy(p1), deepcopy(p2)
    point = random.randint(1, n-1)
    c1 = p1[:point] + p2[point:]
    c2 = p2[:point] + p1[point:]
    return c1, c2

def mutate(ind, mutation_rate):
    child = list(ind)
    for i in range(len(child)):
        if random.random() < mutation_rate:
            choices = [c for c in range(BAN_CO) if c != child[i]]
            child[i] = random.choice(choices) if choices else child[i]
    return child

# ====== GUI + GA control ======
class GiaoDienGA(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Genetic Algorithm — 8 con xe (print control)")
        try:
            self.state('zoomed')
        except Exception:
            self.attributes('-fullscreen', True)

        self.update_idletasks()
        self.scr_w = self.winfo_screenwidth()
        self.scr_h = self.winfo_screenheight()

        max_board_width = int(self.scr_w * 0.60)
        size_from_height = (self.scr_h - 320) // BAN_CO
        size_from_width = max_board_width // (2 * BAN_CO)
        self.o_size = max(28, min(size_from_height, size_from_width))

        total_board_width = 2 * BAN_CO * self.o_size
        left_x = int((self.scr_w - total_board_width - 480) // 2)
        top_y = 160
        self.left_origin = (left_x, top_y)
        self.right_origin = (left_x + BAN_CO * self.o_size + 28, top_y)

        # canvas
        self.canvas = tk.Canvas(self, width=self.scr_w, height=self.scr_h, bg="#f8f8f8")
        self.canvas.pack(fill="both", expand=True)

        self.build_controls()
        self.build_listbox()
        self.reset_state()

        # initial draw
        self.draw_board(self.left_origin, side="left", state=[])
        self.draw_board(self.right_origin, side="right", state=self.lay_best_individual())

    def build_controls(self):
        frm = tk.Frame(self)
        self.canvas.create_window(self.scr_w//2, 34, window=frm)
        tk.Label(frm, text="Genetic Algorithm (8 rooks) — Print control", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=14, pady=(0,6))

        # GA params
        tk.Label(frm, text="Kích thước quần thể:").grid(row=1, column=0, sticky="e")
        self.ent_pop = tk.Entry(frm, width=6); self.ent_pop.insert(0, "100"); self.ent_pop.grid(row=1, column=1, padx=6)

        tk.Label(frm, text="Tỉ lệ lai (0-1):").grid(row=1, column=2, sticky="e")
        self.ent_cr = tk.Entry(frm, width=6); self.ent_cr.insert(0, "0.9"); self.ent_cr.grid(row=1, column=3, padx=6)

        tk.Label(frm, text="Tỉ lệ đột biến (0-1):").grid(row=1, column=4, sticky="e")
        self.ent_mr = tk.Entry(frm, width=6); self.ent_mr.insert(0, "0.05"); self.ent_mr.grid(row=1, column=5, padx=6)

        tk.Label(frm, text="Max thế hệ:").grid(row=1, column=6, sticky="e")
        self.ent_maxgen = tk.Entry(frm, width=6); self.ent_maxgen.insert(0, "200"); self.ent_maxgen.grid(row=1, column=7, padx=6)

        # speed
        tk.Label(frm, text="Tốc độ (ms):").grid(row=1, column=8, sticky="e")
        self.sld_speed = tk.Scale(frm, from_=50, to=2000, orient=tk.HORIZONTAL, length=180)
        self.sld_speed.set(300)
        self.sld_speed.grid(row=1, column=9, columnspan=2, padx=6)

        # Print control UI
        tk.Label(frm, text="In log:").grid(row=2, column=0, sticky="e")
        self.chk_only_best_var = tk.BooleanVar(value=True)
        self.chk_only_best = tk.Checkbutton(frm, text="Chỉ in khi best giảm", variable=self.chk_only_best_var)
        self.chk_only_best.grid(row=2, column=1, columnspan=2, sticky="w")

        tk.Label(frm, text="Hoặc in mỗi N thế hệ:").grid(row=2, column=3, sticky="e")
        self.ent_print_every = tk.Entry(frm, width=6); self.ent_print_every.insert(0, "0")  # 0 = disabled
        self.ent_print_every.grid(row=2, column=4, padx=6)

        self.chk_always_var = tk.BooleanVar(value=False)
        self.chk_always = tk.Checkbutton(frm, text="Luôn in (debug)", variable=self.chk_always_var)
        self.chk_always.grid(row=2, column=5, columnspan=2, sticky="w")

        # control buttons
        btn_frm = tk.Frame(self)
        self.canvas.create_window(self.scr_w//2, 140, window=btn_frm)
        self.btn_start = tk.Button(btn_frm, text="Start", width=12, command=self.start_ga)
        self.btn_start.grid(row=0, column=0, padx=6)
        self.btn_stop = tk.Button(btn_frm, text="Stop", width=10, command=self.stop_ga, state=tk.DISABLED)
        self.btn_stop.grid(row=0, column=1, padx=6)
        self.btn_reset = tk.Button(btn_frm, text="Reset", width=10, command=self.reset_state)
        self.btn_reset.grid(row=0, column=2, padx=6)

        self.btn_next = tk.Button(btn_frm, text="Next ▶", width=10, command=self.step_generation, state=tk.DISABLED)
        self.btn_next.grid(row=0, column=3, padx=6)
        self.auto_var = tk.BooleanVar(value=False)
        self.chk_auto = tk.Checkbutton(btn_frm, text="Auto", variable=self.auto_var, command=self.on_toggle_auto)
        self.chk_auto.grid(row=0, column=4, padx=6)

        self.lbl_status = tk.Label(self, text="Ready", font=("Segoe UI", 10))
        self.canvas.create_window(self.scr_w//2, 168, window=self.lbl_status)

    def build_listbox(self):
        frame = tk.Frame(self, bg="#ffffff")
        x = self.right_origin[0] + BAN_CO * self.o_size + 48
        y = 100
        self.canvas.create_window(x, y, window=frame, anchor="nw")
        tk.Label(frame, text="Pop hiện tại (click để vẽ cá thể)", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.lst = tk.Listbox(frame, width=64, height=34)
        self.lst.pack(side="left", fill="y")
        sb = tk.Scrollbar(frame, orient="vertical", command=self.lst.yview)
        sb.pack(side="right", fill="y")
        self.lst.config(yscrollcommand=sb.set)
        self.lst.bind("<<ListboxSelect>>", self.on_select_individual)

    def reset_state(self):
        self._pop = []
        self._pop_size = 100
        self._crossover_rate = 0.9
        self._mutation_rate = 0.05
        self._max_gen = 200
        self._generation = 0
        self._running = False
        self._auto = False
        self._best_history = []
        self._start_time = None
        self._waiting = False
        self.lst.delete(0, tk.END)
        self.btn_next.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_start.config(state=tk.NORMAL)
        self.chk_auto.deselect()
        # draw empty boards
        self.draw_board(self.left_origin, side="left", state=[])
        self.draw_board(self.right_origin, side="right", state=self.lay_best_individual())
        self.lbl_status.config(text="Reset.")

    def lay_best_individual(self):
        if self._pop:
            best = min(self._pop, key=lambda ind: (tinh_cost(ind),))
            return best
        else:
            return [i % BAN_CO for i in range(BAN_CO)]

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

    def highlight_best(self, origin, state, duration_ms=300):
        prev_tag = getattr(self, "_last_high_tag", None)
        if prev_tag:
            try:
                self.canvas.delete(prev_tag)
            except:
                pass
        tag = f"high_{int(time.time()*1000)}"
        self._last_high_tag = tag
        for r, c in enumerate(state):
            x0, y0 = origin
            s = self.o_size
            x1 = x0 + c*s; y1 = y0 + r*s; x2 = x1 + s; y2 = y1 + s
            self.canvas.create_rectangle(x1+2, y1+2, x2-2, y2-2, outline="blue", width=2, tags=(tag,))
        self.canvas.update()
        self.after(duration_ms, lambda: self.canvas.delete(tag))

    def on_select_individual(self, event):
        sel = self.lst.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx < 0 or idx >= len(self._pop):
            return
        ind = self._pop[idx]
        self.draw_board(self.right_origin, side="right", state=ind)
        self.lbl_status.config(text=f"Show individual idx={idx} cost={tinh_cost(ind)}")

    # ====== GA control ======
    def start_ga(self):
        try:
            self._pop_size = max(2, int(self.ent_pop.get()))
            self._crossover_rate = float(self.ent_cr.get())
            self._mutation_rate = float(self.ent_mr.get())
            self._max_gen = max(1, int(self.ent_maxgen.get()))
        except Exception:
            messagebox.showerror("Lỗi", "Tham số không hợp lệ")
            return

        # clamp rates
        self._crossover_rate = min(max(self._crossover_rate, 0.0), 1.0)
        self._mutation_rate = min(max(self._mutation_rate, 0.0), 1.0)

        # print control params
        try:
            self._print_every = int(self.ent_print_every.get())
        except Exception:
            self._print_every = 0
        self._only_print_on_best_decrease = bool(self.chk_only_best_var.get())
        self._always_print = bool(self.chk_always_var.get())

        # init pop
        self._pop = tao_pop(self._pop_size)
        self._generation = 0
        self._best_history.clear()
        self._running = True
        self._auto = self.auto_var.get()
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_next.config(state=tk.NORMAL)
        self.lst.delete(0, tk.END)
        self._start_time = time.time()
        # show initial population and initial print behavior
        self.update_listbox_and_draw_best(force_print=True)
        if self._auto:
            self.after(10, self._run_generation_auto)
        else:
            self._waiting = True

    def stop_ga(self):
        self._running = False
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_next.config(state=tk.DISABLED)
        elapsed = time.time() - self._start_time if self._start_time else 0
        best = self._best_history[-1] if self._best_history else None
        self.lbl_status.config(text=f"Stopped. Gen={self._generation}. Best cost={tinh_cost(best) if best else 'N/A'} Time={elapsed:.2f}s")

    def on_toggle_auto(self):
        self._auto = self.auto_var.get()
        if self._auto and self._running:
            self._waiting = False
            self.after(10, self._run_generation_auto)

    def step_generation(self):
        if not self._running:
            return
        self._waiting = False
        self._run_one_generation()
        if not self._auto:
            self._waiting = True
            self.btn_next.config(state=tk.NORMAL)

    def _run_generation_auto(self):
        if not self._running:
            return
        self._run_one_generation()
        if self._running and self._auto:
            delay = self.sld_speed.get()
            self.after(delay, self._run_generation_auto)

    def _should_print(self, force=False, best_decreased=False):
        # logic: if always_print -> True
        if self._always_print:
            return True
        # if force (initial) -> True
        if force:
            return True
        # if only_print_on_best_decrease and best_decreased -> True
        if self._only_print_on_best_decrease and best_decreased:
            return True
        # if print_every > 0 and generation % print_every == 0 -> True
        if self._print_every and self._print_every > 0:
            if (self._generation % self._print_every) == 0:
                return True
        return False

    def _run_one_generation(self):
        if not self._running:
            return
        if self._generation >= self._max_gen:
            self._finish_ga()
            return

        # compute best of current pop
        sorted_pop = sorted(self._pop, key=lambda ind: (tinh_cost(ind),))
        best_now = deepcopy(sorted_pop[0])
        best_cost_now = tinh_cost(best_now)

        prev_best_cost = tinh_cost(self._best_history[-1]) if self._best_history else None
        best_decreased = (prev_best_cost is None) or (best_cost_now < prev_best_cost)

        # record best
        self._best_history.append(best_now)

        # prepare new population (elitism = 1)
        new_pop = [best_now]
        while len(new_pop) < self._pop_size:
            parent1 = tournament_selection(self._pop, k=3)
            parent2 = tournament_selection(self._pop, k=3)
            if random.random() < self._crossover_rate:
                child1, child2 = one_point_crossover(parent1, parent2)
            else:
                child1, child2 = deepcopy(parent1), deepcopy(parent2)
            child1 = mutate(child1, self._mutation_rate)
            if len(new_pop) < self._pop_size:
                new_pop.append(child1)
            if len(new_pop) < self._pop_size:
                child2 = mutate(child2, self._mutation_rate)
                new_pop.append(child2)

        self._pop = new_pop
        self._generation += 1

        # decide printing
        do_print = self._should_print(force=False, best_decreased=best_decreased)
        # update UI (listbox + draw best). Pass whether to print a console line
        self.update_listbox_and_draw_best(do_print=do_print, best_decreased=best_decreased)

        # check solution
        current_best = self._best_history[-1]
        if tinh_cost(current_best) == 0:
            # always print solution
            if not do_print:
                # ensure we at least print solution line
                print(f"FOUND SOLUTION at gen {self._generation}: {current_best}", flush=True)
            self._finish_ga()
            return

        if not self._auto:
            self._waiting = True
            self.btn_next.config(state=tk.NORMAL)

    def update_listbox_and_draw_best(self, do_print=False, best_decreased=False, force_print=False):
        # update listbox
        self.lst.delete(0, tk.END)
        for idx, ind in enumerate(self._pop):
            line = f"#{idx:03d} | cost={tinh_cost(ind):2d} | {ind}"
            self.lst.insert(tk.END, line)
        best = min(self._pop, key=lambda ind: (tinh_cost(ind),))
        self.draw_board(self.right_origin, side="right", state=best)
        # highlight best
        self.highlight_best(self.right_origin, best, duration_ms=max(150, self.sld_speed.get()//2))
        self.lbl_status.config(text=f"Gen={self._generation} | Best cost={tinh_cost(best)}")

        # print selective
        if do_print or force_print:
            # print a single succinct line
            print(f"Gen {self._generation} | Best cost={tinh_cost(best)} | Best={best} | best_decreased={best_decreased}", flush=True)

    def _finish_ga(self):
        self._running = False
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_reset.config(state=tk.NORMAL)
        self.btn_next.config(state=tk.DISABLED)
        elapsed = time.time() - self._start_time if self._start_time else 0
        best = self._best_history[-1] if self._best_history else None
        self.lbl_status.config(text=f"Finished. Gen={self._generation} Best cost={tinh_cost(best) if best else 'N/A'} Time={elapsed:.2f}s")
        if best and tinh_cost(best) == 0:
            messagebox.showinfo("GA Finished", f"Found solution at gen {self._generation}: {best}")
        else:
            messagebox.showinfo("GA Finished", f"Stopped after {self._generation} generations. Best cost={tinh_cost(best) if best else 'N/A'} Best={best}")

if __name__ == "__main__":
    app = GiaoDienGA()
    app.mainloop()
