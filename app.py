import time
import random
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
from pynput import keyboard

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.1

class TotemBotUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Habbo Totem Effect Collector")
        self.root.geometry("500x580")
        self.root.attributes("-topmost", True)

        self.is_running = False
        self.listener = None

        # Clean English Keys mapping directly to game actions
        self.coords = {
            "totem_head_item": (0, 0),
            "room_pickup_button": (0, 0),
            "totem_floor_spot": (0, 0),
            "inventory_totem_head_slot": (0, 0),
            "inventory_place_in_room_button": (0, 0),
            "character_reset_tile": (0, 0),
            "red_plate": (0, 0),
            "blue_plate": (0, 0),
            "yellow_plate": (0, 0),
            "green_plate": (0, 0),
        }

        self._build_ui()
        self._start_key_listener()

    def _build_ui(self):
        # Header Bar
        top_bar = ttk.Frame(self.root)
        top_bar.pack(fill="x", padx=10, pady=5)
        reset_all_btn = ttk.Button(top_bar, text="Reset All Coordinates", command=self.reset_coordinates)
        reset_all_btn.pack(fill="x")

        # Calibration Frame
        calib_frame = ttk.LabelFrame(self.root, text=" Coordinate Calibration ")
        calib_frame.pack(fill="both", expand=True, padx=10, pady=5)

        canvas = tk.Canvas(calib_frame, borderwidth=0)
        scroll = ttk.Scrollbar(calib_frame, orient="vertical", command=canvas.yview)
        frame = ttk.Frame(canvas)
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.labels = {}
        for key in self.coords:
            f = ttk.Frame(frame)
            f.pack(fill="x", padx=5, pady=2)
            
            # Format display label (e.g., "inventory_place_in_room_button" -> "Inventory Place In Room Button")
            display_name = key.replace("_", " ").title()
            lbl = ttk.Label(f, text=f"{display_name}: {self.coords[key]}", width=34)
            lbl.pack(side="left")
            self.labels[key] = lbl
            btn = ttk.Button(f, text="Set", command=lambda k=key: self.calibrate(k))
            btn.pack(side="right")

        # Bottom Control Panel
        bottom = ttk.Frame(self.root)
        bottom.pack(fill="x", padx=10, pady=10)

        self.start_btn = ttk.Button(bottom, text="Start Automation", command=self.toggle_automation)
        self.start_btn.pack(fill="x", pady=5)
        ttk.Label(bottom, text="Emergency Stop: Press 'DELETE' key anytime", foreground="red", font=("Arial", 9, "bold")).pack()

    def reset_coordinates(self):
        for key in self.coords:
            self.coords[key] = (0, 0)
            display_name = key.replace("_", " ").title()
            self.labels[key].config(text=f"{display_name}: (0, 0)")
        messagebox.showinfo("Reset Complete", "All coordinate mappings have been reset to (0, 0).")

    def _start_key_listener(self):
        def on_press(key):
            if key == keyboard.Key.delete:
                if self.is_running:
                    self.stop_automation("Emergency Stop (DEL pressed)!")

        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.daemon = True
        self.listener.start()

    def stop_automation(self, reason="Automation stopped."):
        self.is_running = False
        self.start_btn.config(text="Start Automation")
        messagebox.showinfo("Status", reason)

    def calibrate(self, key):
        def capture():
            display_name = key.replace("_", " ").title()
            for i in range(3, 0, -1):
                self.labels[key].config(text=f"Hover mouse... {i}s")
                time.sleep(1)
            pos = pyautogui.position()
            self.coords[key] = (pos.x, pos.y)
            self.labels[key].config(text=f"{display_name}: ({pos.x}, {pos.y})")

        threading.Thread(target=capture, daemon=True).start()

    def human_click(self, coord_key, double=False):
        if not self.is_running:
            return False

        x, y = self.coords[coord_key]
        if (x, y) == (0, 0):
            return False

        jx = x + random.randint(-2, 2)
        jy = y + random.randint(-2, 2)

        pyautogui.moveTo(jx, jy, duration=random.uniform(0.18, 0.35))
        time.sleep(random.uniform(0.05, 0.12))
        
        if double:
            pyautogui.doubleClick()
        else:
            pyautogui.click()
            
        time.sleep(random.uniform(0.3, 0.6))
        return True

    def process_totem_effect(self, plate_key):
        if not self.is_running:
            return

        # 1. Walk onto colored plate
        if not self.human_click(plate_key):
            return
        time.sleep(random.uniform(2.5, 3.2))

        # 2. Trigger effect
        if not self.human_click("totem_head_item", double=True):
            return
        time.sleep(random.uniform(1.2, 1.8))

        # 3. Pick up totem head
        if not self.human_click("totem_head_item"):
            return
        time.sleep(random.uniform(0.4, 0.8))
        if not self.human_click("room_pickup_button"):
            return
        time.sleep(random.uniform(1.2, 1.8))

        # 4. Select from inventory & place back in room
        if not self.human_click("inventory_totem_head_slot"):
            return
        time.sleep(random.uniform(0.5, 0.8))
        
        if not self.human_click("inventory_place_in_room_button"):
            return
        time.sleep(random.uniform(0.8, 1.2))

        if not self.human_click("totem_floor_spot"):
            return
        time.sleep(random.uniform(2.0, 2.8))

        # 5. Walk character back to neutral reset spot ONLY after completing green plate
        if plate_key == "green_plate":
            self.human_click("character_reset_tile")
            time.sleep(random.uniform(2.2, 3.0))

    def run_loop(self):
        color_order = ["red_plate", "blue_plate", "yellow_plate", "green_plate"]

        while self.is_running:
            for plate_key in color_order:
                if not self.is_running:
                    break
                self.process_totem_effect(plate_key)

    def toggle_automation(self):
        if not self.is_running:
            self.is_running = True
            self.start_btn.config(text="Stop Automation")
            threading.Thread(target=self.run_loop, daemon=True).start()
        else:
            self.stop_automation("Automation stopped by user.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TotemBotUI(root)
    root.mainloop()
