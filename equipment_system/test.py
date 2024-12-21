import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from items import get_weapons, get_spell_cards, get_accessories

# 使用導入的函數來填充 GEAR_DATA，並在這裡添加圖片路徑
GEAR_DATA = {
    "武器": [
        (weapon.name, weapon.discription, "images/weapon01.png") if weapon.name == "七耀魔法書" else
        (weapon.name, weapon.discription, "images/weapon02.png") if weapon.name == "貪欲的叉勺" else
        (weapon.name, weapon.discription, "images/default_weapon.png")
        for weapon in get_weapons()
    ],
    "魔法卡": [
        (card.name, card.discription, "images/spell_card.png") for card in get_spell_cards()
    ],
    "飾品": [
        (accessory.name, accessory.discription, "images/accessory.png") for accessory in get_accessories()
    ]
}

class GearSelectorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("裝備選擇介面")
        self.geometry("1000x600")

        # 初始化狀態
        self.categories = list(GEAR_DATA.keys())
        self.current_category_index = 0
        self.current_item_index = 0
        self.selected_indices = {cat: None for cat in self.categories}
        self.on_complete_selection = False

        # 設定背景圖片
        self.background_image = Image.open("images/background.png")
        self.background_photo = ImageTk.PhotoImage(self.background_image.resize((1000, 600)))

        self.canvas = tk.Canvas(self, width=1000, height=600)
        self.canvas.pack(fill="both", expand=True)

        # 在畫布上顯示背景圖片
        self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")

        # 創建框架用於放置元件
        self.main_frame = tk.Frame(self.canvas, bg="transparent")
        self.canvas.create_window(0, 0, anchor="nw", window=self.main_frame)

        # 建立視窗元件
        self.create_widgets()

        # 綁定鍵盤操作
        self.bind("<Left>", self.navigate_left)
        self.bind("<Right>", self.navigate_right)
        self.bind("<Up>", self.navigate_up)
        self.bind("<Down>", self.navigate_down)
        self.bind("<Return>", self.select_item_or_complete)

    def create_widgets(self):
        """
        創建視窗中顯示裝備的元件
        """
        self.gear_frames = {}
        self.gear_labels = {}

        for category_index, category in enumerate(self.categories):
            frame = tk.Frame(self.main_frame, bg="transparent")
            frame.grid(row=category_index, column=0, pady=20, sticky="w")
            tk.Label(frame, text=category, font=("Arial", 16), bg="transparent", fg="white").grid(row=0, column=0, sticky="w")
            self.gear_frames[category] = frame
            self.gear_labels[category] = []

            for i, (name, desc, img_path) in enumerate(GEAR_DATA[category]):
                label = tk.Label(frame, text=name, font=("Arial", 12), width=15, height=10, borderwidth=2, relief="groove")
                label.grid(row=1, column=i, padx=10)

                # 加載圖片
                if os.path.exists(img_path):
                    img = Image.open(img_path).resize((100, 100))
                    photo = ImageTk.PhotoImage(img)
                    label.config(image=photo, compound="top")
                    label.image = photo  # 防止垃圾回收
                self.gear_labels[category].append(label)

        # 添加 "選擇完成"
        self.complete_label = tk.Label(self.main_frame, text="選擇完成", font=("Arial", 16),
                                       borderwidth=2, relief="groove", width=20, height=2, bg="gray")
        self.complete_label.grid(row=len(self.categories), column=0, pady=20)

    def update_display(self):
        """
        更新右側顯示，包括當前焦點高亮顯示和完成選擇的狀態
        """
        for category_index, category in enumerate(self.categories):
            for i, label in enumerate(self.gear_labels[category]):
                if category_index == self.current_category_index and i == self.current_item_index and not self.on_complete_selection:
                    label.config(bg="lightblue", fg="black")
                elif i == self.selected_indices[category]:
                    label.config(bg="green", fg="white")  # 已選擇項目
                else:
                    label.config(bg="gray", fg="white")  # 其他狀態

        if self.on_complete_selection:
            self.complete_label.config(bg="lightblue", fg="black")
        else:
            self.complete_label.config(bg="gray", fg="white")

    def select_item_or_complete(self, event):
        """
        按下 Enter 鍵：選擇當前裝備或完成選擇
        """
        if self.on_complete_selection:
            self.finish_selection()
        else:
            category = self.categories[self.current_category_index]
            self.selected_indices[category] = self.current_item_index
            self.update_display()

    def finish_selection(self):
        """
        完成選擇，檢查是否每類裝備都有選擇，並顯示結果
        """
        if any(idx is None for idx in self.selected_indices.values()):
            messagebox.showwarning("未完成", "請選擇每一類裝備！")
            return

        result = "\n".join([f"{cat}: {GEAR_DATA[cat][idx][0]}" for cat, idx in self.selected_indices.items()])
        messagebox.showinfo("選擇完成", f"你的選擇如下：\n{result}")
        self.destroy()

if __name__ == "__main__":
    app = GearSelectorApp()
    app.mainloop()
