import tkinter as tk
from pynput import keyboard, mouse
import string

class MouselessApp:
    GRID_SIZE = 27
    OVERLAY_ALPHA = 0.6
    BACKGROUND_COLOR = "black"
    GRID_COLOR = "white"
    FONT = ("Arial", 12)

    def __init__(self):
        self.root = tk.Tk()
        self._setup_overlay()

        self.cell_width = self.root.winfo_screenwidth() // self.GRID_SIZE
        self.cell_height = self.root.winfo_screenheight() // self.GRID_SIZE

        self.grid = {}
        self.overlay_active = False
        self.selection = ""
        self.mouse_controller = mouse.Controller()

        self.create_grid()
        self._start_keyboard_listener()

    def _setup_overlay(self):
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-alpha", self.OVERLAY_ALPHA)
        self.root.configure(background=self.BACKGROUND_COLOR)
        self.root.withdraw()

    def create_grid(self):
        canvas = tk.Canvas(self.root, bg=self.BACKGROUND_COLOR, highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)

        letters = string.ascii_uppercase
        letter_pairs = [f"{a}         {b}" for a in letters for b in letters[:self.GRID_SIZE]]
        index = 0

        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                x1, y1 = col * self.cell_width, row * self.cell_height
                x2, y2 = x1 + self.cell_width, y1 + self.cell_height
                canvas.create_rectangle(x1, y1, x2, y2, outline=self.GRID_COLOR)
                text_x_left = x1 + self.cell_width // 4
                text_x_right = x1 + (3 * self.cell_width) // 4
                text_y = y1 + self.cell_height // 2
                canvas.create_text(text_x_left, text_y, text=letters[index % len(letters)], fill=self.GRID_COLOR, font=self.FONT)
                canvas.create_text(text_x_right, text_y, text=letters[(index // len(letters)) % len(letters)], fill=self.GRID_COLOR, font=self.FONT)
                self.grid[f"{letters[index % len(letters)]}{letters[(index // len(letters)) % len(letters)]}"] = (col, row)
                index += 1

    def _start_keyboard_listener(self):
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()

    def toggle_overlay(self):
        if self.overlay_active:
            self.root.withdraw()
        else:
            self.root.deiconify()
        self.overlay_active = not self.overlay_active

    def move_mouse_to_cell(self, col, row, position=None):
        x_center = col * self.cell_width + self.cell_width // 2
        y_center = row * self.cell_height + self.cell_height // 2

        if position == "left":
            x_center -= self.cell_width // 4
        elif position == "right":
            x_center += self.cell_width // 4

        self.mouse_controller.position = (x_center, y_center)

    def click_mouse(self, button=mouse.Button.left):
        self.mouse_controller.click(button, 1)

    def close_overlay_and_click(self, col, row, position=None, button=mouse.Button.left):
        self.move_mouse_to_cell(col, row, position)
        self.toggle_overlay()
        self.click_mouse(button)

    def on_key_press(self, key):
        try:
            if key == keyboard.Key.cmd_l and keyboard.Key.shift:  # Toggle overlay with Win+Shift
                self.toggle_overlay()
            elif self.overlay_active:
                self._handle_overlay_keypress(key)
        except AttributeError:
            pass

    def _handle_overlay_keypress(self, key):
        if hasattr(key, 'char') and key.char:
            char = key.char.upper()
            if len(self.selection) < 2:
                self.selection += char
                if len(self.selection) == 2 and self.selection in self.grid:
                    col, row = self.grid[self.selection]
                    self.move_mouse_to_cell(col, row)
            elif len(self.selection) == 2:
                col, row = self.grid[self.selection]
                if char == self.selection[0]:
                    self.close_overlay_and_click(col, row, position="left")
                elif char == self.selection[1]:
                    self.close_overlay_and_click(col, row, position="right")
                self.selection = ""
        elif key == keyboard.Key.space and len(self.selection) == 2:
            col, row = self.grid[self.selection]
            self.close_overlay_and_click(col, row)
            self.selection = ""

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MouselessApp()
    app.run()
