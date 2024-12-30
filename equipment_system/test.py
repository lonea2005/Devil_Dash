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
        self.geometry("1280x960")

        # 加載自定義背景圖片
        self.background_image = Image.open("images/accessory04.png")
        self.background_photo = ImageTk.PhotoImage(self.background_image)

        # 使用 Canvas 作為主背景
        self.background_canvas = tk.Canvas(self, width=1280, height=960)
        self.background_canvas.pack(fill="both", expand=True)

        # 添加背景圖片到 Canvas
        self.background_canvas.create_image(0, 0, image=self.background_photo, anchor="nw")

        # 創建主框架，並添加到背景 Canvas
        self.main_frame = tk.Frame(self.background_canvas)  # 保留單一的 main_frame
        self.background_canvas.create_window(0, 0, window=self.main_frame, anchor="nw")

        # 初始化狀態
        self.categories = list(GEAR_DATA.keys())  # 裝備分類列表
        self.current_category_index = 0  # 當前分類的索引（初始為第一類）
        self.current_item_index = 0  # 當前分類中的焦點索引（初始為第一個項目）
        self.selected_indices = {cat: [] if cat == "配件" else None for cat in self.categories}
        self.on_complete_selection = False

        # 創建左側摘要框架
        self.left_frame = tk.Frame(self.main_frame, width=300, bg="white")
        self.left_frame.pack(side="left", fill="y")
        self.left_frame.pack_propagate(False)

        # 創建可滾動區域
        self.main_canvas = tk.Canvas(self.main_frame, width=700, height=550)
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

        # 創建元件
        self.create_widgets()

        # 綁定鍵盤操作
        self.bind("<Left>", self.navigate_left)
        self.bind("<Right>", self.navigate_right)
        self.bind("<Up>", self.navigate_up)
        self.bind("<Down>", self.navigate_down)
        self.bind("<Return>", self.select_item_or_complete)
        self.bind("q", self.finish_selection)

    def create_widgets(self):
        """
        創建視窗中顯示裝備的元件
        """
        self.gear_frames = {}  # 每個分類的框架
        self.gear_labels = {}  # 每個分類的裝備標籤

        for category_index, category in enumerate(self.categories):
            frame = tk.Frame(self.scrollable_frame)
            frame.grid(row=category_index, column=0, pady=20, sticky="w")
            tk.Label(frame, text=category, font=("Arial", 25)).grid(row=0, column=0, sticky="w")
            self.gear_frames[category] = frame
            self.gear_labels[category] = []

            for i, (name, desc, img_path) in enumerate(GEAR_DATA[category]):
                label = tk.Label(frame, text=name, font=("Arial", 16), borderwidth=2, relief="groove", compound="top")
                label.grid(row=1, column=i, padx=10)

                # 加載圖片
                if os.path.exists(img_path):
                    try:
                        # 調整圖片大小
                        img = Image.open(img_path).resize((200, 200))
                        photo = ImageTk.PhotoImage(img)
                        label.config(image=photo, text=name, compound="top", borderwidth=1, relief="solid")
                        label.image = photo  # 防止垃圾回收
                    except Exception as e:
                        print(f"Error loading image {img_path}: {e}")
                else:
                    print(f"Image path does not exist: {img_path}")
                self.gear_labels[category].append(label)

        # 初始化顯示
        self.update_display()
        self.update_summary()


    # 修改 update_display 方法中的已選擇項目顯示邏輯
    def update_display(self):
        """
        更新右側顯示，包括當前焦點高亮顯示和完成選擇的狀態
        """
        for category_index, category in enumerate(self.categories):
            for i, label in enumerate(self.gear_labels[category]):
                # 當前焦點高亮
                if category_index == self.current_category_index and i == self.current_item_index and not self.on_complete_selection:
                    label.config(bg="lightblue", fg="black")
                elif (category == "配件" and i in self.selected_indices[category]) or (category != "配件" and i == self.selected_indices[category]):
                    label.config(bg="green", fg="white")  # 已選擇項目
                else:
                    label.config(bg="gray", fg="white")  # 其他狀態

        # 確保滾動範圍更新正確
        self.main_canvas.yview_moveto(min(max(self.current_category_index / len(self.categories), 0), 1))

        # 自动滚动到当前选择的位置并居中显示
        current_label = self.gear_labels[self.categories[self.current_category_index]][self.current_item_index]
        label_center_x = current_label.winfo_x() + current_label.winfo_width() / 2
        canvas_width = self.main_canvas.winfo_width()
        self.main_canvas.xview_moveto(max(label_center_x / self.scrollable_frame.winfo_width() - 0.25, 0))

        # 更新左侧摘要
        self.update_summary()

    # 修改 update_summary 方法中的摘要顯示邏輯
    def update_summary(self):
        """
        更新左側摘要區域，顯示當前選擇的裝備
        """
        for widget in self.left_frame.winfo_children():
            widget.destroy()

        tk.Label(self.left_frame, text="選擇摘要", font=("Arial", 25), bg="white", wraplength=280).pack(anchor="n", pady=10)  # 在这里设置 wraplength 以确保文本换行

        for category in self.categories:
            selected_indices = self.selected_indices[category]
            if selected_indices is None or (category == "配件" and not selected_indices):
                summary = "無"
            else:
                if category == "配件":
                    summary = ", ".join([GEAR_DATA[category][idx][0] for idx in selected_indices])
                else:
                    summary = GEAR_DATA[category][selected_indices][0]
            
            # 添加类别标签，并单独设置字体大小
            tk.Label(self.left_frame, text=f"{category}:", bg="white", font=("Arial", 20, "bold"), justify="left", wraplength=280).pack(anchor="w", pady=(20, 0))
            tk.Label(self.left_frame, text=summary, bg="white", font=("Arial", 16), justify="left", wraplength=280).pack(anchor="w", pady=(0, 20))  # 在这里设置 wraplength 以确保文本换行

        # 修改 update_summary 方法中的当前焦点装备的说明部分
        current_category = self.categories[self.current_category_index]
        current_item = GEAR_DATA[current_category][self.current_item_index]
        current_name, current_desc, current_img_path = current_item
        # 添加“裝備說明:”的标签，并单独设置字体大小
        tk.Label(self.left_frame, text="裝備說明:", bg="white", font=("Arial", 20, "bold"), justify="left", wraplength=280).pack(anchor="w", pady=(20, 0))
        current_summary = f"{current_name}\n{current_desc}"
        tk.Label(self.left_frame, text=current_summary, bg="white", font=("Arial", 16), justify="left", wraplength=280).pack(anchor="w", pady=(0, 20))    
    
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
        self.current_category_index = max(self.current_category_index - 1, 0)
        self.current_item_index = 0
        self.update_display()

    def navigate_down(self, event):
        self.current_category_index = min(self.current_category_index + 1, len(self.categories) - 1)
        self.current_item_index = 0
        self.update_display()

    # 修改 select_item_or_complete 方法
    def select_item_or_complete(self, event):
        category = self.categories[self.current_category_index]
        if category == "配件":
            if self.current_item_index in self.selected_indices[category]:
                # 如果当前选择的配件已经被选中，再次按下 Enter 取消选择
                self.selected_indices[category].remove(self.current_item_index)
            else:
                # 否则，选择当前配件
                self.selected_indices[category].append(self.current_item_index)
        else:
            # 对于其他类别，只能选择一个
            if self.selected_indices[category] == self.current_item_index:
                # 如果当前选择的装备已经被选中，再次按下 Enter 取消选择
                self.selected_indices[category] = None
            else:
                # 否则，选择当前装备
                self.selected_indices[category] = self.current_item_index
        self.update_display()
        self.update_summary()

    def finish_selection(self, event=None):
        """
        完成選擇，檢查是否每類裝備都有選擇，並顯示結果
        """
        for category, selected in self.selected_indices.items():
            if category == "配件":
                if not selected:  # 如果配件类别没有选择任何项
                    messagebox.showwarning("未完成", "請選擇每一類裝備！")
                    return
            else:
                if selected is None:  # 如果其他类别没有选择任何项
                    messagebox.showwarning("未完成", "請選擇每一類裝備！")
                    return

        result = ""
        selected_items = {}
        for category, selected in self.selected_indices.items():
            if category == "配件":
                selected_items[category] = [GEAR_DATA[category][idx][0] for idx in selected]
                selected_items_str = ", ".join(selected_items[category])
                result += f"{category}: {selected_items_str}\n"
            else:
                selected_items[category] = GEAR_DATA[category][selected][0]
                result += f"{category}: {selected_items[category]}\n"

        messagebox.showinfo("選擇完成", f"你的選擇如下：\n{result}")
        self.destroy()
        return selected_items


def main():
    app = GearSelectorApp()
    app.mainloop()
    return app.selected_indices

if __name__ == "__main__":
    selected_items = main()
    print("Selected items:", selected_items)