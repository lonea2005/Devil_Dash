# equipment.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from items import get_weapons, get_spell_cards, get_accessories

# 使用导入的函数来填充 GEAR_DATA，并在这里添加图片路径
GEAR_DATA = {
    "武器": [
        (weapon.name, weapon.discription, "images/sword.png") if weapon.name == "七耀魔法書" else
        (weapon.name, weapon.discription, "images/axe.png") if weapon.name == "貪欲的叉勺" else
        (weapon.name, weapon.discription, "images/default_weapon.png")
        for weapon in get_weapons()
    ],
    "符卡": [
        (spell_card.name, spell_card.discription, "images/fireball.png") if spell_card.name == "Fireball" else
        (spell_card.name, spell_card.discription, "images/ice_shard.png") if spell_card.name == "Ice Shard" else
        (spell_card.name, spell_card.discription, "images/default_spell_card.png")
        for spell_card in get_spell_cards()
    ],
    "配件": [
        (accessory.name, accessory.discription, "images/ring.png") if accessory.name == "Ring" else
        (accessory.name, accessory.discription, "images/amulet.png") if accessory.name == "Amulet" else
        (accessory.name, accessory.discription, "images/default_accessory.png")
        for accessory in get_accessories()
    ],
}

class GearSelectorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("裝備選擇介面")
        self.geometry("1000x600")

        # 打印当前工作目录
        print(f"Current working directory: {os.getcwd()}")

        # 初始化狀態
        self.categories = list(GEAR_DATA.keys())  # 裝備分類列表
        self.current_category_index = 0  # 當前分類的索引（初始為第一類）
        self.current_item_index = 0  # 當前分類中的焦點索引（初始為第一個項目）
        self.selected_indices = {cat: None for cat in self.categories}  # 每個分類的選擇結果
        self.on_complete_selection = False  # 是否移動到完成選擇的狀態

        # 建立主視窗框架
        self.left_frame = tk.Frame(self, width=300, bg="white")
        self.left_frame.pack(side="left", fill="y")

        self.main_canvas = tk.Canvas(self, width=700, height=600)
        self.scrollbar_y = tk.Scrollbar(self, orient="vertical", command=self.main_canvas.yview)
        self.scrollbar_x = tk.Scrollbar(self, orient="horizontal", command=self.main_canvas.xview)
        self.scrollable_frame = tk.Frame(self.main_canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )

        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)

        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar_y.pack(side="right", fill="y")
        self.scrollbar_x.pack(side="bottom", fill="x")

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
        self.gear_frames = {}  # 每個分類的框架
        self.gear_labels = {}  # 每個分類的裝備標籤

        for category_index, category in enumerate(self.categories):
            frame = tk.Frame(self.scrollable_frame)
            frame.grid(row=category_index, column=0, pady=20, sticky="w")
            tk.Label(frame, text=category, font=("Arial", 16)).grid(row=0, column=0, sticky="w")
            self.gear_frames[category] = frame
            self.gear_labels[category] = []

            for i, (name, desc, img_path) in enumerate(GEAR_DATA[category]):
                label = tk.Label(frame, text=name, font=("Arial", 12), width=150, height=150, borderwidth=2, relief="groove", compound="top")
                label.grid(row=1, column=i, padx=10)

                # 加載圖片
                if os.path.exists(img_path):
                    try:
                        # 调整图片大小
                        img = Image.open(img_path).resize((150, 150))  # 在这里调整图片大小，上面width=150, height=150調框
                        photo = ImageTk.PhotoImage(img)
                        label.config(image=photo, text=name, compound="top", borderwidth=1, relief="solid")  # 在这里调整图片外框
                        label.image = photo  # 防止垃圾回收
                    except Exception as e:
                        print(f"Error loading image {img_path}: {e}")
                else:
                    print(f"Image path does not exist: {img_path}")
                self.gear_labels[category].append(label)

        # 在最後一行添加 "選擇完成"
        self.complete_label = tk.Label(self.scrollable_frame, text="選擇完成", font=("Arial", 16),
                                       borderwidth=2, relief="groove", width=20, height=2, bg="gray")
        self.complete_label.grid(row=len(self.categories), column=0, pady=20)

        # 初始化顯示
        self.update_display()
        self.update_summary()

    def update_display(self):
        """
        更新右側顯示，包括當前焦點高亮顯示和完成選擇的狀態
        """
        for category_index, category in enumerate(self.categories):
            for i, label in enumerate(self.gear_labels[category]):
                # 當前焦點高亮
                if category_index == self.current_category_index and i == self.current_item_index and not self.on_complete_selection:
                    label.config(bg="lightblue", fg="black")
                elif i == self.selected_indices[category]:
                    label.config(bg="green", fg="white")  # 已選擇項目
                else:
                    label.config(bg="gray", fg="white")  # 其他狀態

        # 更新 "選擇完成" 的顏色
        if self.on_complete_selection:
            self.complete_label.config(bg="lightblue", fg="black")
        else:
            self.complete_label.config(bg="gray", fg="white")

        # 確保滾動範圍更新正確
        self.main_canvas.yview_moveto(min(max(self.current_category_index / len(self.categories), 0), 1))

        # 自动滚动到当前选择的位置并居中显示
        current_label = self.gear_labels[self.categories[self.current_category_index]][self.current_item_index]
        label_center_x = current_label.winfo_x() + current_label.winfo_width() / 2
        canvas_width = self.main_canvas.winfo_width()
        self.main_canvas.xview_moveto(max(label_center_x / self.scrollable_frame.winfo_width() - 0.5, 0))

    def update_summary(self):
        """
        更新左側摘要區域，顯示當前選擇的裝備
        """
        for widget in self.left_frame.winfo_children():
            widget.destroy()

        tk.Label(self.left_frame, text="選擇摘要", font=("Arial", 16), bg="white").pack(anchor="n", pady=10)

        for category in self.categories:
            selected_idx = self.selected_indices[category]
            if selected_idx is None:
                summary = f"{category}: 無"
            else:
                name, desc, img_path = GEAR_DATA[category][selected_idx]
                summary = f"{category}: {name}\n{desc}"
            tk.Label(self.left_frame, text=summary, bg="white", font=("Arial", 12), justify="left").pack(anchor="w", pady=5)

    def navigate_left(self, event):
        """
        左鍵：移動到前一個裝備
        """
        if not self.on_complete_selection:
            self.current_item_index = max(self.current_item_index - 1, 0)
        self.update_display()

    def navigate_right(self, event):
        """
        右鍵：移動到下一個裝備
        """
        if not self.on_complete_selection:
            category = self.categories[self.current_category_index]
            self.current_item_index = min(self.current_item_index + 1, len(GEAR_DATA[category]) - 1)
        self.update_display()

    def navigate_up(self, event):
        """
        上鍵：移動到上一個分類或完成按鈕
        """
        if self.on_complete_selection:
            self.on_complete_selection = False
        else:
            self.current_category_index = max(self.current_category_index - 1, 0)
            self.current_item_index = 0  # 預設回到第一個裝備
        self.update_display()

    def navigate_down(self, event):
        """
        下鍵：移動到下一個分類或完成按鈕
        """
        if self.current_category_index == len(self.categories) - 1:
            self.on_complete_selection = True
        elif self.on_complete_selection:
            self.on_complete_selection = False
        else:
            self.current_category_index = min(self.current_category_index + 1, len(self.categories) - 1)
            self.current_item_index = 0  # 預設回到第一個裝備
        self.update_display()

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
            self.update_summary()

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