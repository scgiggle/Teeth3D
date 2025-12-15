import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import os

class ImageProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("智能图片处理工具")
        self.root.geometry("800x600") # 界面高度调小了一些，因为去掉了中间的选项
        
        self.image_files = []
        
        # 创建界面元素
        self.create_widgets()
    
    def create_widgets(self):
        # 标题
        title_label = tk.Label(self.root, text="图片智能处理工具", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # 选择文件按钮
        select_btn = tk.Button(self.root, text="选择图片文件", command=self.select_files, 
                               width=20, height=2, bg="#4CAF50", fg="white", font=("Arial", 10))
        select_btn.pack(pady=10)
        
        # 显示已选择文件数量
        self.file_count_label = tk.Label(self.root, text="未选择文件", font=("Arial", 10))
        self.file_count_label.pack(pady=5)
        
        # 说明文字 (替代原来的选项框)
        info_text = "自动处理规则：\n所有图片均裁剪\n文件名结尾为 _0 或 _1 的图片自动进行上下镜像"
        info_label = tk.Label(self.root, text=info_text, font=("Arial", 9), fg="gray", justify="center")
        info_label.pack(pady=10)
        
        # 处理按钮
        process_btn = tk.Button(self.root, text="开始智能处理", command=self.process_images,
                                width=20, height=2, bg="#2196F3", fg="white", font=("Arial", 10, "bold"))
        process_btn.pack(pady=10)
        
        # 状态标签
        self.status_label = tk.Label(self.root, text="", font=("Arial", 9), fg="green")
        self.status_label.pack(pady=5)
    
    def select_files(self):
        """选择图片文件"""
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
                ("所有文件", "*.*")
            ]
        )
        
        if files:
            self.image_files = list(files)
            self.file_count_label.config(text=f"已选择 {len(self.image_files)} 个文件")
            self.status_label.config(text="")
    
    def crop_image(self, img):
        """裁剪图片到指定尺寸 (4:3)"""
        target_width, target_height = 2677, 2008
        width, height = img.size
        
        # 从中心裁剪
        left = (width - target_width) // 2
        top = (height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        
        # 如果图片小于目标尺寸,则调整裁剪区域
        if width < target_width or height < target_height:
            left = max(0, left)
            top = max(0, top)
            right = min(width, right)
            bottom = min(height, bottom)
        
        return img.crop((left, top, right, bottom))
    
    def mirror_image(self, img):
        """垂直镜像图片 (上下翻转)"""
        return img.transpose(Image.FLIP_TOP_BOTTOM)
    
    def process_images(self):
        """根据文件名自动处理图片"""
        if not self.image_files:
            messagebox.showwarning("警告", "请先选择图片文件!")
            return
        
        # 选择输出文件夹
        output_folder = filedialog.askdirectory(title="选择输出文件夹")
        if not output_folder:
            return
        
        success_count = 0
        error_count = 0
        
        for file_path in self.image_files:
            try:
                # 1. 打开图片
                img = Image.open(file_path)
                
                # 获取文件名和扩展名
                filename = os.path.basename(file_path)
                name, ext = os.path.splitext(filename)
                
                # 2. 所有图片统一执行：裁剪
                img = self.crop_image(img)
                
                # 3. 条件判断：如果文件名以 _0 或 _1 结尾，则执行镜像
                # 例如：TEE_06_0.jpg 会被匹配，image123.jpg 不会
                if name.endswith("_0") or name.endswith("_1"):
                    # print(f"正在对 {filename} 进行镜像处理...") # 调试用
                    img = self.mirror_image(img)
                
                # 4. 保存 (保持原文件名)
                output_filename = filename
                output_path = os.path.join(output_folder, output_filename)
                
                img.save(output_path)
                success_count += 1
                
            except Exception as e:
                error_count += 1
                print(f"处理文件 {file_path} 时出错: {str(e)}")
        
        # 显示处理结果
        result_msg = f"处理完成!\n成功: {success_count} 个\n失败: {error_count} 个"
        messagebox.showinfo("处理结果", result_msg)
        self.status_label.config(text=f"已处理 {success_count} 个文件")

def main():
    root = tk.Tk()
    app = ImageProcessorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()