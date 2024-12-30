import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from items import get_weapons, get_spell_cards, get_accessories

#font
# 使用导入的函数来填充 GEAR_DATA，并在这里添加图片路径
GEAR_DATA = {
    "武器": [
        (weapon.name, weapon.discription, "images/weapon01.png") if weapon.name == "七耀魔法書" else
        (weapon.name, weapon.discription, "images/weapon02.png") if weapon.name == "貪欲的叉勺" else
        (weapon.name, weapon.discription, "images/default_weapon.png")
        for weapon in get_weapons()
    ],
    "符卡": [
        (spell_card.name, spell_card.discription, "images/spell_card01.png") if spell_card.name == "彩符「彩光亂舞」" else
        (spell_card.name, spell_card.discription, "images/spell_card02.png") if spell_card.name == "逆符「階級反轉」" else
        (spell_card.name, spell_card.discription, "images/spell_card03.png") if spell_card.name == "戀符「極限火花」" else
        (spell_card.name, spell_card.discription, "images/default_spell_card.png")
        for spell_card in get_spell_cards()
    ],
    "配件": [
        (accessory.name, accessory.discription, "images/水晶吊墜.png") if accessory.name == "水晶吊墜" else
        (accessory.name, accessory.discription, "images/心型吊墜.png") if accessory.name == "心型吊墜" else
        (accessory.name, accessory.discription, "images/亡靈提燈.png") if accessory.name == "亡靈提燈" else
        (accessory.name, accessory.discription, "images/accessory04.png") if accessory.name == "蝙蝠吊墜" else
        (accessory.name, accessory.discription, "images/銀製匕首.png") if accessory.name == "銀製匕首" else
        (accessory.name, accessory.discription, "images/斷線的人偶.png") if accessory.name == "斷線的人偶" else
        (accessory.name, accessory.discription, "images/神社的符咒.png") if accessory.name == "神社的符咒" else
        (accessory.name, accessory.discription, "images/巫女的御幣.png") if accessory.name == "巫女的御幣" else
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
        # 在 __init__ 方法中，调整布局
        self.bottom_frame = tk.Frame(self, height=50, bg="white")  # 创建底部框架
        self.bottom_frame.pack(side="bottom", fill="x")

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(side="top", fill="both", expand=True)

        self.left_frame = tk.Frame(self.main_frame, width=300, bg="white")  # 在这里设置选择摘要栏的宽度
        self.left_frame.pack(side="left", fill="y")
        self.left_frame.pack_propagate(False)  # 防止框架根据内容自动调整大小

        self.main_canvas = tk.Canvas(self.main_frame, width=700, height=550)  # 调整高度以留出底部空间
        self.scrollbar_y = tk.Scrollbar(self.main_frame, orient="vertical", command=self.main_canvas.yview)
        self.scrollbar_x = tk.Scrollbar(self.main_frame, orient="horizontal", command=self.main_canvas.xview)
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

        # 窗口大小调整时更新“選擇完成”按钮的位置
        self.bind("<Configure>", self.update_complete_button_position)

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
                label = tk.Label(frame, text=name, font=("Arial", 12), borderwidth=2, relief="groove", compound="top")
                label.grid(row=1, column=i, padx=10)

                # 加載圖片
                if os.path.exists(img_path):
                    try:
                        # 调整图片大小
                        img = Image.open(img_path).resize((150, 150))  # 在这里调整图片大小
                        photo = ImageTk.PhotoImage(img)
                        label.config(image=photo, text=name, compound="top", borderwidth=1, relief="solid")  # 在这里调整图片外框
                        label.image = photo  # 防止垃圾回收
                    except Exception as e:
                        print(f"Error loading image {img_path}: {e}")
                else:
                    print(f"Image path does not exist: {img_path}")
                self.gear_labels[category].append(label)

        # 在最後一行添加 "選擇完成"
        self.complete_label = tk.Label(self.bottom_frame, text="選擇完成", font=("Arial", 20),
                               borderwidth=2, relief="groove", width=20, height=2, bg="gray")
        self.complete_label.pack(pady=10)  # 将按钮放置在底部框架中

        # 初始化顯示
        self.update_display()
        self.update_summary()

    def update_complete_button_position(self, event=None):
        """
        更新“選擇完成”按钮的位置，使其始终位于窗口底部的中间
        """
        self.complete_label.place(relx=0.5, rely=1.0, anchor="s")

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
        self.main_canvas.xview_moveto(max(label_center_x / self.scrollable_frame.winfo_width() - 0.25, 0))

        # 更新左侧摘要
        self.update_summary()

    def update_summary(self):
        """
        更新左側摘要區域，顯示當前選擇的裝備
        """
        for widget in self.left_frame.winfo_children():
            widget.destroy()

        tk.Label(self.left_frame, text="選擇摘要", font=("Arial", 20), bg="white", wraplength=280).pack(anchor="n", pady=10)  # 在这里设置 wraplength 以确保文本换行

        for category in self.categories:
            selected_idx = self.selected_indices[category]
            if selected_idx is None:
                summary = f"{category}: 無"
            else:
                name, desc, img_path = GEAR_DATA[category][selected_idx]
                summary = f"{category}: {name}\n{desc}"
            tk.Label(self.left_frame, text=summary, bg="white", font=("Arial", 16), justify="left", wraplength=280).pack(anchor="w", pady=20)  # 在这里设置 wraplength 以确保文本换行

        # 添加当前焦点装备的说明
        current_category = self.categories[self.current_category_index]
        current_item = GEAR_DATA[current_category][self.current_item_index]
        current_name, current_desc, current_img_path = current_item
        current_summary = f"裝備說明: {current_name}\n{current_desc}"
        tk.Label(self.left_frame, text=current_summary, bg="white", font=("Arial", 16), justify="left", wraplength=280).pack(anchor="w", pady=40)  # 在这里设置 wraplength 以确保文本换行            

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