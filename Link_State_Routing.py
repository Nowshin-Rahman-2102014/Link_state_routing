import heapq
import copy
import tkinter as tk
from tkinter import ttk, scrolledtext
import math


class Router:
    def __init__(self, name, logger_func):
        self.name = name
        self.logger = logger_func
        self.lsdb = {self.name: {}}
        self.routing_table = {}
        self.sequence_numbers = {}

    def add_link(self, neighbor_name, cost):
        self.lsdb[self.name][neighbor_name] = cost

    def receive_lsp(self, sender, lsp_data, sequence_num):
        if sender in self.sequence_numbers and sequence_num <= self.sequence_numbers[sender]:
            return False

        self.sequence_numbers[sender] = sequence_num
        self.lsdb[sender] = lsp_data
        self.run_dijkstra()
        return True

    def run_dijkstra(self):
        pq = [(0, self.name, [])]
        visited = set()
        min_costs = {self.name: 0}
        self.routing_table = {}

        while pq:
            current_cost, current_node, path = heapq.heappop(pq)

            if current_node in visited:
                continue
            visited.add(current_node)

            next_hop = path[0] if path else "Local"

            if current_node != self.name:
                self.routing_table[current_node] = (next_hop, current_cost)

            neighbors = self.lsdb.get(current_node, {})
            for neighbor, link_cost in neighbors.items():
                new_cost = current_cost + link_cost

                if neighbor not in min_costs or new_cost < min_costs[neighbor]:
                    min_costs[neighbor] = new_cost
                    new_path = path + [neighbor]
                    heapq.heappush(pq, (new_cost, neighbor, new_path))

    def get_full_path_to(self, target_name):
        if target_name == self.name:
            return [self.name]
        if target_name not in self.routing_table:
            return None

        pq = [(0, self.name, [self.name])]
        visited = set()

        while pq:
            cost, curr, path_seq = heapq.heappop(pq)

            if curr == target_name:
                return path_seq
            if curr in visited:
                continue
            visited.add(curr)

            neighbors = self.lsdb.get(curr, {})
            for neighbor, link_cost in neighbors.items():
                if neighbor not in visited:

                    heapq.heappush(
                        pq, (cost + link_cost, neighbor, path_seq + [neighbor]))
        return None

    def get_routing_table_str(self):
        lines = [f"ROUTING TABLE: {self.name}"]
        lines.append(f"{'Dest':<8} | {'Next Hop':<10} | {'Cost':<5}")
        lines.append("-" * 35)
        for dest in sorted(self.routing_table.keys()):
            hop, cost = self.routing_table[dest]
            lines.append(f"{dest:<8} | {hop:<10} | {cost:<5}")
        return "\n".join(lines)


class NetworkSimulator:
    def __init__(self, logger_func):
        self.routers = {}
        self.lsp_sequence = 0
        self.logger = logger_func

    def log(self, msg):
        self.logger(msg)

    def add_router(self, name):
        if name not in self.routers:
            self.routers[name] = Router(name, self.logger)

    def add_link(self, r1, r2, cost):
        self.routers[r1].add_link(r2, cost)
        self.routers[r2].add_link(r1, cost)

    def trigger_flood(self):
        self.lsp_sequence += 1

        pending = []
        for r_name, router in self.routers.items():
            data = copy.deepcopy(router.lsdb[r_name])
            pending.append((r_name, data, self.lsp_sequence))

        updates_count = 0

        stable = False
        while not stable:
            stable = True
            for sender, data, seq in pending:
                for receiver_name, receiver in self.routers.items():
                    if sender != receiver_name:
                        if receiver.receive_lsp(sender, data, seq):
                            updates_count += 1
                            stable = False

        self.log(
            f"[CONVERGENCE] Network stabilized after {updates_count} updates. (Seq {self.lsp_sequence})")

    def update_link_cost(self, r1, r2, new_cost):
        self.log(f"\n[EVENT] Link {r1} <-> {r2} updated to cost {new_cost}")
        self.add_link(r1, r2, new_cost)
        self.trigger_flood()


class NetworkGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Link State Routing Simulator")
        self.root.geometry("1100x750")

        self.bg_color = "#1e1e2e"
        self.sidebar_color = "#252535"
        self.accent_color = "#89b4fa"
        self.node_color = "#f38ba8"
        self.node_text_color = "#11111b"
        self.line_color = "#a6adc8"
        self.text_color = "#cdd6f4"
        self.highlight_color = "#00ff00"  # Bright Green for the path

        self.root.configure(bg=self.bg_color)

        self.current_path_nodes = []

        self.main_frame = tk.Frame(root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            self.main_frame, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH,
                         expand=True, padx=10, pady=10)

        self.sidebar = tk.Frame(
            self.main_frame, bg=self.sidebar_color, width=350)
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=0, pady=0)
        self.sidebar.pack_propagate(False)

        lbl_title = tk.Label(self.sidebar, text="CONTROL PANEL", font=("Consolas", 16, "bold"),
                             bg=self.sidebar_color, fg=self.accent_color)
        lbl_title.pack(pady=(20, 10))

        self.create_control_panel()

        self.create_path_panel()

        self.lbl_table_title = tk.Label(self.sidebar, text="Click a Node to View Table",
                                        font=("Consolas", 10, "bold"), bg=self.sidebar_color, fg=self.node_color)
        self.lbl_table_title.pack(pady=(15, 5))

        self.txt_table = tk.Text(self.sidebar, height=8, bg="#181825", fg="#a6e3a1", font=(
            "Consolas", 10), relief=tk.FLAT)
        self.txt_table.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(self.sidebar, text="Simulation Log", font=("Consolas", 10, "bold"),
                 bg=self.sidebar_color, fg=self.text_color).pack(pady=(15, 5))

        self.log_display = scrolledtext.ScrolledText(
            self.sidebar, height=10, bg="#181825", fg="#fab387", font=("Consolas", 9), relief=tk.FLAT)
        self.log_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.sim = NetworkSimulator(self.log_to_gui)

        self.node_coords = {
            'A': (300, 100), 'B': (500, 100),
            'C': (200, 300), 'D': (600, 300),
            'E': (400, 400)
        }
        self.node_radius = 25

        for r in self.node_coords.keys():
            self.sim.add_router(r)

        self.initial_links = [
            ('A', 'B', 5), ('A', 'C', 1),
            ('B', 'D', 2), ('B', 'E', 3),
            ('C', 'E', 1), ('D', 'E', 4)
        ]
        for u, v, c in self.initial_links:
            self.sim.add_link(u, v, c)

        self.sim.trigger_flood()
        self.draw_network()
        self.log_to_gui("System Initialized.")

        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def create_control_panel(self):
        ctrl_frame = tk.LabelFrame(self.sidebar, text="Update Link Cost",
                                   bg=self.sidebar_color, fg=self.text_color, font=("Arial", 10, "bold"))
        ctrl_frame.pack(fill=tk.X, padx=10, pady=5)

        frame_inputs = tk.Frame(ctrl_frame, bg=self.sidebar_color)
        frame_inputs.pack(pady=5)

        tk.Label(frame_inputs, text="Src:", bg=self.sidebar_color,
                 fg=self.text_color).pack(side=tk.LEFT)
        self.entry_src = tk.Entry(frame_inputs, width=4)
        self.entry_src.pack(side=tk.LEFT, padx=2)
        tk.Label(frame_inputs, text="Dst:", bg=self.sidebar_color,
                 fg=self.text_color).pack(side=tk.LEFT)
        self.entry_dst = tk.Entry(frame_inputs, width=4)
        self.entry_dst.pack(side=tk.LEFT, padx=2)
        tk.Label(frame_inputs, text="Cost:", bg=self.sidebar_color,
                 fg=self.text_color).pack(side=tk.LEFT)
        self.entry_cost = tk.Entry(frame_inputs, width=5)
        self.entry_cost.pack(side=tk.LEFT, padx=2)

        btn_update = tk.Button(ctrl_frame, text="Update Link", bg=self.accent_color, fg="black", font=(
            "Arial", 9, "bold"), command=self.apply_update)
        btn_update.pack(fill=tk.X, padx=10, pady=5)

    def create_path_panel(self):
        path_frame = tk.LabelFrame(self.sidebar, text="Highlight Shortest Path",
                                   bg=self.sidebar_color, fg=self.highlight_color, font=("Arial", 10, "bold"))
        path_frame.pack(fill=tk.X, padx=10, pady=10)

        frame_inputs = tk.Frame(path_frame, bg=self.sidebar_color)
        frame_inputs.pack(pady=5)

        tk.Label(frame_inputs, text="From:", bg=self.sidebar_color,
                 fg=self.text_color).pack(side=tk.LEFT)
        self.path_src = tk.Entry(frame_inputs, width=5)
        self.path_src.pack(side=tk.LEFT, padx=5)
        tk.Label(frame_inputs, text="To:", bg=self.sidebar_color,
                 fg=self.text_color).pack(side=tk.LEFT)
        self.path_dst = tk.Entry(frame_inputs, width=5)
        self.path_dst.pack(side=tk.LEFT, padx=5)

        btn_frame = tk.Frame(path_frame, bg=self.sidebar_color)
        btn_frame.pack(fill=tk.X, pady=5)

        btn_show = tk.Button(btn_frame, text="Show Path", bg=self.highlight_color, fg="black", font=(
            "Arial", 9, "bold"), width=10, command=self.show_path_on_canvas)
        btn_show.pack(side=tk.LEFT, padx=10)

        btn_clear = tk.Button(btn_frame, text="Clear", bg="#fab387", fg="black", font=(
            "Arial", 9, "bold"), width=8, command=self.clear_path_on_canvas)
        btn_clear.pack(side=tk.RIGHT, padx=10)

    def log_to_gui(self, message):
        self.log_display.insert(tk.END, message + "\n")
        self.log_display.see(tk.END)

    def apply_update(self):
        src, dst = self.entry_src.get().upper(), self.entry_dst.get().upper()
        cost_str = self.entry_cost.get()
        if src in self.sim.routers and dst in self.sim.routers and cost_str.isdigit():
            self.sim.update_link_cost(src, dst, int(cost_str))
            # Re-calculate path if one was active
            if self.current_path_nodes:
                self.show_path_on_canvas()
            self.draw_network()
            self.refresh_current_table()
        else:
            self.log_to_gui("[ERROR] Invalid Link Input.")

    def show_path_on_canvas(self):
        src, dst = self.path_src.get().upper(), self.path_dst.get().upper()
        if src in self.sim.routers and dst in self.sim.routers:
            # Call the new backend method to get the full sequence
            path_seq = self.sim.routers[src].get_full_path_to(dst)

            if path_seq:
                self.current_path_nodes = path_seq
                self.log_to_gui(f"[PATH] Highlighted: {' -> '.join(path_seq)}")
                self.draw_network()
            else:
                self.log_to_gui(f"[PATH] No path found from {src} to {dst}.")
                self.clear_path_on_canvas()
        else:
            self.log_to_gui("[ERROR] Invalid Path Sources/Dest.")

    def clear_path_on_canvas(self):
        self.current_path_nodes = []
        self.draw_network()

    def draw_network(self):
        self.canvas.delete("all")

        path_edges = set()
        if len(self.current_path_nodes) > 1:
            for i in range(len(self.current_path_nodes) - 1):
                u, v = self.current_path_nodes[i], self.current_path_nodes[i+1]
                # Store as sorted tuple so A-B is the same as B-A
                path_edges.add(tuple(sorted((u, v))))

        drawn_links = set()
        for r_name, router in self.sim.routers.items():
            x1, y1 = self.node_coords[r_name]
            for neighbor, cost in router.lsdb[r_name].items():
                link_key = tuple(sorted((r_name, neighbor)))
                if link_key not in drawn_links:
                    x2, y2 = self.node_coords[neighbor]

                    width = 2
                    fill_color = self.line_color
                    if link_key in path_edges:
                        width = 5
                        fill_color = self.highlight_color

                    # Draw line behind nodes
                    self.canvas.create_line(
                        x1, y1, x2, y2, fill=fill_color, width=width, tags="link")

                    # Draw Cost Label
                    mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                    self.canvas.create_rectangle(
                        mid_x-10, mid_y-10, mid_x+10, mid_y+10, fill=self.bg_color, outline="")
                    self.canvas.create_text(mid_x, mid_y, text=str(
                        cost), fill="white", font=("Arial", 10, "bold"))
                    drawn_links.add(link_key)

        self.canvas.tag_lower("link")

        for name, (x, y) in self.node_coords.items():
            r = self.node_radius
            outline_col = self.highlight_color if name in self.current_path_nodes else self.accent_color
            outline_w = 4 if name in self.current_path_nodes else 2

            self.canvas.create_oval(
                x-r-2, y-r-2, x+r+2, y+r+2, fill=self.bg_color, outline=outline_col, width=outline_w)
            self.canvas.create_oval(
                x-r, y-r, x+r, y+r, fill=self.node_color, outline="")
            self.canvas.create_text(
                x, y, text=name, fill=self.node_text_color, font=("Arial", 12, "bold"))

    def on_canvas_click(self, event):
        for name, (x, y) in self.node_coords.items():
            if math.sqrt((event.x - x)**2 + (event.y - y)**2) <= self.node_radius:
                self.show_routing_table(name)
                return

    def show_routing_table(self, node_name):
        self.lbl_table_title.config(text=f"Routing Table: {node_name}")
        self.txt_table.delete("1.0", tk.END)
        self.txt_table.insert(
            tk.END, self.sim.routers[node_name].get_routing_table_str())

    def refresh_current_table(self):
        title = self.lbl_table_title.cget("text")
        if "Routing Table:" in title:
            node_name = title.split(": ")[1]
            self.show_routing_table(node_name)


if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkGUI(root)
    root.mainloop()
