# rr_hill_climb_step_auto.py
# Random-Restart Hill-Climbing — step-by-step + auto-play control
# Mỗi improvement in 1 lần và vẽ 1 lần, sau đó chờ Next hoặc auto-delay.

import tkinter as tk
from tkinter import messagebox
import random
from copy import deepcopy
import time

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

def all_neighbors(trang_thai):
    res = []
    for hang in range(BAN_CO):
        for cot in range(BAN_CO):
            if cot == trang_thai[hang]:
                continue
            nh = list(trang_thai)
            nh[hang] = cot
            res.append((nh, hang, trang_thai[hang], cot))
    return res

class RRHillStepAuto(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RR Hill-Climb — Step / Auto control")
        # fullscreen attempt
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
        left_x = int((self.scr_w - total_board_width - 460) // 2)
        top_y = 140
        self.left_origin = (left_x, top_y)
        self.right_origin = (left_x + BAN_CO * self.o_size + 28, top_y)

        self.canvas = tk.Canvas(self, width=self.scr_w, height=self.scr_h, bg="#f8f8f8")
        self.canvas.pack(fill="both", expand=True)

        self.build_controls()
        self.build_listbox()
        self.reset_state()

        # initial draw
        self.draw_board(self.left_origin, side="left", state=[])
        self.draw_board(self.right_origin, side="right", state=self._trang_thai)

    def build_controls(self):
        frm = tk.Frame(self)
        self.canvas.create_window(self.scr_w//2, 34, window=frm)
        tk.Label(frm, text="Random-Restart Hill-Climbing (Step / Auto)", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=10, pady=(0,6))

        tk.Label(frm, text="Max steps:").grid(row=1, column=0, sticky="e")
        self.ent_steps = tk.Entry(frm, width=6); self.ent_steps.insert(0, "200"); self.ent_steps.grid(row=1, column=1, padx=6)
        tk.Label(frm, text="Max restarts:").grid(row=1, column=2, sticky="e")
        self.ent_restarts = tk.Entry(frm, width=6); self.ent_restarts.insert(0, "50"); self.ent_restarts.grid(row=1, column=3, padx=6)

        tk.Label(frm, text="Tốc độ (ms):").grid(row=1, column=4, sticky="e")
        self.sld_speed = tk.Scale(frm, from_=50, to=2000, orient=tk.HORIZONTAL, length=200)
        self.sld_speed.set(250)
        self.sld_speed.grid(row=1, column=5, columnspan=2, padx=6)

        # control buttons
        btn_frm = tk.Frame(self)
        self.canvas.create_window(self.scr_w//2, 96, window=btn_frm)
        self.btn_start = tk.Button(btn_frm, text="Start", width=12, command=self.start_run)
        self.btn_start.grid(row=0, column=0, padx=6)
        self.btn_stop = tk.Button(btn_frm, text="Stop", width=10, command=self.stop_run, state=tk.DISABLED)
        self.btn_stop.grid(row=0, column=1, padx=6)
        self.btn_reset = tk.Button(btn_frm, text="Reset", width=10, command=self.reset_state)
        self.btn_reset.grid(row=0, column=2, padx=6)

        self.btn_next = tk.Button(btn_frm, text="Next ▶", width=10, command=self.step_next, state=tk.DISABLED)
        self.btn_next.grid(row=0, column=3, padx=6)
        self.auto_var = tk.BooleanVar(value=False)
        self.chk_auto = tk.Checkbutton(btn_frm, text="Auto", variable=self.auto_var, command=self.on_toggle_auto)
        self.chk_auto.grid(row=0, column=4, padx=6)
        self.lbl_status = tk.Label(self, text="Ready", font=("Segoe UI", 10))
        self.canvas.create_window(self.scr_w//2, 126, window=self.lbl_status)

    def build_listbox(self):
        frame = tk.Frame(self, bg="#ffffff")
        x = self.right_origin[0] + BAN_CO * self.o_size + 48
        y = 76
        self.canvas.create_window(x, y, window=frame, anchor="nw")
        tk.Label(frame, text="Accepted improvements (click to view)", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.lst = tk.Listbox(frame, width=64, height=34)
        self.lst.pack(side="left", fill="y")
        sb = tk.Scrollbar(frame, orient="vertical", command=self.lst.yview)
        sb.pack(side="right", fill="y")
        self.lst.config(yscrollcommand=sb.set)
        self.lst.bind("<<ListboxSelect>>", self.on_select_history)

    def reset_state(self):
        self._trang_thai = [random.randrange(BAN_CO) for _ in range(BAN_CO)]
        self._best = list(self._trang_thai)
        self._best_cost = tinh_cost(self._best)
        self._history = []  # list of accepted improvements
        self._running = False
        self._cur_restart = 0
        self._cur_step_restart = 0
        self._global_step = 0
        self._accepted_total = 0
        self._start_time = None
        self._waiting_for_next = False
        self._auto = False
        self.lst.delete(0, tk.END)
        self.btn_next.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_start.config(state=tk.NORMAL)
        self.chk_auto.deselect()
        self.draw_board(self.left_origin, side="left", state=[])
        self.draw_board(self.right_origin, side="right", state=self._trang_thai)
        self.lbl_status.config(text=f"Reset. Start cost={self._best_cost}")

    # drawing with tags
    def draw_board(self, origin, side="right", state=None):
        x0, y0 = origin
        s = self.o_size
        w = BAN_CO * s
        h = BAN_CO * s
        tag_board = f"board_{side}"
        tag_piece = f"piece_{side}"
        tag_high = f"high_{side}"

        # delete piece/high/board tags inside region
        self.canvas.delete(tag_high)
        self.canvas.delete(tag_piece)
        self.canvas.delete(tag_board)

        # background rect
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

    def highlight_move(self, origin, hang, cot, duration_ms=300):
        x0, y0 = origin
        s = self.o_size
        x1 = x0 + cot*s
        y1 = y0 + hang*s
        x2 = x1 + s
        y2 = y1 + s
        tag_high = f"high_{ 'left' if origin==self.left_origin else 'right' }"
        rect = self.canvas.create_rectangle(x1+2, y1+2, x2-2, y2-2, outline="red", width=3, tags=(tag_high,))
        self.canvas.update()
        self.after(duration_ms, lambda: self.canvas.delete(tag_high))

    def on_select_history(self, event):
        sel = self.lst.curselection()
        if not sel:
            return
        idx = sel[0]
        rec = self._history[idx]
        self.draw_board(self.right_origin, side="right", state=rec["state"])
        self.lbl_status.config(text=f"Show step {rec['global_step']} | restart={rec['restart']} | cost={rec['cost']}")

    # start run: initialize params and start first restart
    def start_run(self):
        try:
            self._max_steps = int(self.ent_steps.get())
            self._max_restarts = int(self.ent_restarts.get())
        except Exception:
            messagebox.showerror("Lỗi", "Tham số không hợp lệ")
            return
        self._delay = self.sld_speed.get()
        self._running = True
        self._auto = self.auto_var.get()
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_reset.config(state=tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL)
        self._cur_restart = 0
        self._global_step = 0
        self._accepted_total = 0
        self._history.clear()
        self.lst.delete(0, tk.END)
        self._start_time = time.time()
        # start first restart cycle but do not auto-run continuous improvements:
        self.after(10, self._do_restart_cycle)

    def stop_run(self):
        self._running = False
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_reset.config(state=tk.NORMAL)
        self.btn_next.config(state=tk.DISABLED)
        elapsed = time.time() - self._start_time if self._start_time else 0
        self.lbl_status.config(text=f"Stopped. Best cost={self._best_cost}. Time={elapsed:.2f}s")

    def on_toggle_auto(self):
        self._auto = self.auto_var.get()
        # if turned on and waiting for next, schedule continue
        if self._auto and self._waiting_for_next:
            self._waiting_for_next = False
            self.after(10, self._process_next_after_wait)

    # invoked by Next button or Auto scheduling
    def step_next(self):
        # user-driven: process one accepted move if available or force next search
        if not self._running:
            return
        # if currently waiting_for_next (i.e. after a restart or after last accepted), process next
        if self._waiting_for_next:
            self._waiting_for_next = False
            self.after(10, self._process_next_after_wait)

    # internal: start a restart cycle
    def _do_restart_cycle(self):
        if not self._running:
            return
        if self._cur_restart >= self._max_restarts:
            self._finish_run()
            return
        self._cur_restart += 1
        self._cur_step_restart = 0
        # random initial state for this restart
        self._trang_thai = [random.randrange(BAN_CO) for _ in range(BAN_CO)]
        cur_cost = tinh_cost(self._trang_thai)
        print(f"--- Restart {self._cur_restart} start (cost={cur_cost}): {self._trang_thai}", flush=True)
        self.draw_board(self.right_origin, side="right", state=self._trang_thai)
        self.lbl_status.config(text=f"Restart {self._cur_restart}/{self._max_restarts} | start cost={cur_cost}")
        # begin searching neighbors but stop at first accepted (we will step)
        self._waiting_for_next = True
        # if auto on, immediately process next; else wait for user Next
        if self._auto:
            self._waiting_for_next = False
            self.after(10, self._process_next_after_wait)

    # internal: search until next accepted move or local optimum; then stop and present result
    def _process_next_after_wait(self):
        if not self._running:
            return
        # run neighbor search until find improvement or reach max_steps for this restart
        steps_this_restart = 0
        while steps_this_restart < self._max_steps:
            # compute best neighbor
            neighbors = all_neighbors(self._trang_thai)
            best_neighbor = None
            best_cost = tinh_cost(self._trang_thai)
            for nh, hang, fr, to in neighbors:
                c = tinh_cost(nh)
                if c < best_cost:
                    best_cost = c
                    best_neighbor = (nh, hang, fr, to)
            self._cur_step_restart += 1
            self._global_step += 1
            steps_this_restart += 1

            if best_neighbor is not None:
                nh, hang, fr, to = best_neighbor
                self._trang_thai = nh
                new_cost = best_cost
                self._accepted_total += 1
                rec = {
                    "restart": self._cur_restart,
                    "local_step": self._cur_step_restart,
                    "global_step": self._global_step,
                    "state": deepcopy(self._trang_thai),
                    "cost": new_cost,
                    "move": f"{hang}:{fr}->{to}"
                }
                self._history.append(rec)
                line = f"#{rec['global_step']:05d} | restart={rec['restart']} | cost={rec['cost']:2d} | move={rec['move']} | state={rec['state']}"
                # print once, add to listbox, draw and highlight once
                print(line, flush=True)
                self.lst.insert(tk.END, line)
                self.lst.yview_moveto(1.0)
                self.draw_board(self.right_origin, side="right", state=self._trang_thai)
                self.highlight_move(self.right_origin, hang, to, duration_ms=max(200, self.sld_speed.get()))
                self.lbl_status.config(text=f"Restart {self._cur_restart} | step {self._cur_step_restart} | cost={new_cost}")
                if new_cost < self._best_cost:
                    self._best_cost = new_cost
                    self._best = list(self._trang_thai)
                # after showing this accepted move, pause and wait (or auto-continue after delay)
                if self._auto:
                    # schedule next after user speed delay
                    self.after(self.sld_speed.get(), self._process_next_after_wait)
                else:
                    # set flag waiting for user Next
                    self._waiting_for_next = True
                    # enable Next button (should be enabled)
                    self.btn_next.config(state=tk.NORMAL)
                return  # IMPORTANT: return so we show ONE accepted move only

            # else: no neighbor improvement at this state -> local optimum
            # check next iteration; if none within max_steps we will restart
        # if reached here => no improvement within allowed steps -> restart
        self.lbl_status.config(text=f"Local optimum at restart {self._cur_restart}, cost={tinh_cost(self._trang_thai)} -> restarting...")
        # small pause then restart
        self.after(200, self._do_restart_cycle)

    def step_next(self):
        # user clicked Next: if waiting flag -> process next
        if not self._running:
            return
        if self._waiting_for_next:
            self._waiting_for_next = False
            # disable Next until next improvement presented
            self.btn_next.config(state=tk.DISABLED)
            # process next accepted (or cause restart)
            self.after(10, self._process_next_after_wait)

    def on_select_history(self, event):
        sel = self.lst.curselection()
        if not sel:
            return
        idx = sel[0]
        rec = self._history[idx]
        self.draw_board(self.right_origin, side="right", state=rec["state"])
        self.lbl_status.config(text=f"Show step {rec['global_step']} | restart={rec['restart']} | cost={rec['cost']}")

    def highlight_move(self, origin, hang, cot, duration_ms=300):
        x0, y0 = origin
        s = self.o_size
        x1 = x0 + cot*s
        y1 = y0 + hang*s
        x2 = x1 + s
        y2 = y1 + s
        tag_high = f"high_{ 'left' if origin==self.left_origin else 'right' }"
        self.canvas.delete(tag_high)
        rect = self.canvas.create_rectangle(x1+3, y1+3, x2-3, y2-3, outline="red", width=3, tags=(tag_high,))
        self.canvas.update()
        self.after(duration_ms, lambda: self.canvas.delete(tag_high))

    def on_toggle_auto(self):
        self._auto = self.auto_var.get()
        if self._auto and self._waiting_for_next:
            self._waiting_for_next = False
            self.btn_next.config(state=tk.DISABLED)
            self.after(10, self._process_next_after_wait)

    def stop_run(self):
        self._running = False
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_reset.config(state=tk.NORMAL)
        self.btn_next.config(state=tk.DISABLED)
        elapsed = time.time() - self._start_time if self._start_time else 0
        self.lbl_status.config(text=f"Stopped. Best cost={self._best_cost}. Time={elapsed:.2f}s")

    def _finish_run(self):
        self._running = False
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_reset.config(state=tk.NORMAL)
        self.btn_next.config(state=tk.DISABLED)
        elapsed = time.time() - self._start_time if self._start_time else 0
        self.lbl_status.config(text=f"Finished. Best cost={self._best_cost}. Time={elapsed:.2f}s")
        self.draw_board(self.right_origin, side="right", state=self._best)
        messagebox.showinfo("Finished", f"Best cost={self._best_cost}\nBest state={self._best}\nTotal improvements={len(self._history)}\nTime={elapsed:.2f}s")

if __name__ == "__main__":
    app = RRHillStepAuto()
    app.mainloop()
