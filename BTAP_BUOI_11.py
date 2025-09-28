import random
import tkinter as tk
from tkinter import messagebox

##########################
# Genetic Algorithm phần logic
##########################

def make_individual(n):
    ind = list(range(n))
    random.shuffle(ind)
    return ind

def board_conflicts(ind):
    n = len(ind)
    conflicts = 0
    for i in range(n):
        for j in range(i + 1, n):
            if abs(i - j) == abs(ind[i] - ind[j]):
                conflicts += 1
    return conflicts

def fitness(ind):
    n = len(ind)
    max_pairs = n * (n - 1) // 2
    return max_pairs - board_conflicts(ind)

def tournament_selection(pop, k=3):
    chosen = random.sample(pop, k)
    return max(chosen, key=fitness)[:]

def order_crossover(p1, p2):
    n = len(p1)
    a, b = sorted(random.sample(range(n), 2))
    def ox(pa, pb):
        child = [-1] * n
        child[a:b+1] = pa[a:b+1]
        pos = 0
        for i in range(n):
            if child[i] == -1:
                while pb[pos] in child:
                    pos += 1
                child[i] = pb[pos]
        return child
    return ox(p1, p2), ox(p2, p1)

def swap_mutation(ind, rate):
    if random.random() < rate:
        i, j = random.sample(range(len(ind)), 2)
        ind[i], ind[j] = ind[j], ind[i]

def genetic_n_queens(n=8, pop_size=200, generations=1000, mutation_rate=0.2):
    population = [make_individual(n) for _ in range(pop_size)]
    for gen in range(1, generations + 1):
        conflicts_list = [board_conflicts(ind) for ind in population]
        if 0 in conflicts_list:
            idx = conflicts_list.index(0)
            return population[idx], gen
        fitnesses = [fitness(ind) for ind in population]
        new_pop = []
        # elitism
        best_idx = max(range(len(population)), key=lambda i: fitnesses[i])
        new_pop.append(population[best_idx][:])
        while len(new_pop) < pop_size:
            p1 = tournament_selection(population)
            p2 = tournament_selection(population)
            c1, c2 = order_crossover(p1, p2)
            swap_mutation(c1, mutation_rate)
            swap_mutation(c2, mutation_rate)
            new_pop.append(c1)
            if len(new_pop) < pop_size:
                new_pop.append(c2)
        population = new_pop
    return None, generations

##########################
# Tkinter GUI
##########################

class NQueensGUI:
    def __init__(self, root, n=8):
        self.root = root
        self.n = n
        self.cell_size = 50

        self.root.title("N-Queens - Tìm kiếm niềm tin (GA)")

        # Frame chính: chia 2 bên
        frame = tk.Frame(root)
        frame.pack(padx=10, pady=10)

        # Canvas bên trái (bàn cờ trống)
        self.canvas_left = tk.Canvas(frame, width=n*self.cell_size, height=n*self.cell_size)
        self.canvas_left.grid(row=0, column=0, padx=10)

        # Canvas bên phải (bàn cờ có solution)
        self.canvas_right = tk.Canvas(frame, width=n*self.cell_size, height=n*self.cell_size)
        self.canvas_right.grid(row=0, column=1, padx=10)

        # Button Solve
        self.btn_solve = tk.Button(root, text="Solve", command=self.solve)
        self.btn_solve.pack(pady=10)

        # Vẽ bàn cờ trống và ví dụ mẫu
        self.draw_empty_board(self.canvas_left)
        self.show_example_solution()

    def draw_empty_board(self, canvas):
        n = self.n
        cs = self.cell_size
        canvas.delete("all")
        for i in range(n):
            for j in range(n):
                color = "white" if (i+j) % 2 == 0 else "gray"
                canvas.create_rectangle(j*cs, i*cs, (j+1)*cs, (i+1)*cs, fill=color)

    def draw_solution(self, canvas, solution):
        self.draw_empty_board(canvas)
        n = self.n
        cs = self.cell_size
        for row in range(n):
            col = solution[row]
            x = col * cs + cs/2
            y = row * cs + cs/2
            canvas.create_text(x, y, text="♛", font=("Arial", 24), fill="red")

    def show_example_solution(self):
        # Ví dụ mẫu cho N=8 (một lời giải chuẩn của bài toán 8-queens)
        example = [0, 4, 7, 5, 2, 6, 1, 3]
        self.draw_solution(self.canvas_right, example)

    def solve(self):
        sol, gen = genetic_n_queens(self.n)
        if sol:
            self.draw_solution(self.canvas_right, sol)
            messagebox.showinfo("Kết quả", f"Tìm được lời giải sau {gen} thế hệ!")
        else:
            messagebox.showwarning("Kết quả", "Không tìm thấy lời giải!")

##########################
# Run
##########################

if __name__ == "__main__":
    root = tk.Tk()
    app = NQueensGUI(root, n=8)  # bạn có thể đổi n=10, 12,...
    root.mainloop()
