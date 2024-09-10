from io import BytesIO
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from tkinterdnd2 import TkinterDnD, DND_FILES


def resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class ImageCompressorGUI(TkinterDnD.Tk):  # Use TkinterDnD for drag and drop support
    def __init__(self):
        super().__init__()
        self.title("Image Compressor")
        # self.geometry("400x500")  # Adjust window size as needed

        self.geometry("350x160")
        self.resizable(False, False)  # Disable window resizing

        # Main container
        self.main_frame = tk.Frame(self, padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Input image label and entry
        self.input_label = tk.Label(self.main_frame, text="Input Image Path:")
        self.input_label.grid(row=0, column=0, sticky="w")
        self.input_entry = tk.Entry(self.main_frame, width=30)
        self.input_entry.grid(row=0, column=1, sticky="w")

        # Browse button
        self.browse_button = tk.Button(
            self.main_frame, text="Browse", command=self.browse_image
        )
        self.browse_button.grid(row=0, column=2, sticky="w")

        # Drop target for image files
        self.drop_target = tk.Label(
            self.main_frame,
            text="Drag and Drop image here",
            bg="lightblue",
            relief="sunken",
            height=2,
        )
        self.drop_target.grid(row=1, columnspan=3, sticky="ew", pady=10)

        # Enable drop on the drop_target
        self.drop_target.drop_target_register(DND_FILES)
        self.drop_target.dnd_bind("<<Drop>>", self.drop_image)

        # Compression target size label and entry
        self.size_label = tk.Label(self.main_frame, text="Target Size (KB):")
        self.size_label.grid(row=2, column=0, sticky="w", pady=5)
        self.size_entry = tk.Entry(self.main_frame, width=10)
        self.size_entry.grid(row=2, column=1, sticky="w")

        # Compress and save button
        self.save_button = tk.Button(
            self.main_frame, text="Compress & Save", command=self.compress_image_to_size
        )
        self.save_button.grid(row=4, columnspan=3, sticky="ew", pady=5)

        # Image label to display the selected image
        self.image_label = tk.Label(self.main_frame)
        self.image_label.grid(row=5, columnspan=3, pady=10)  # Adjust grid as needed

        # Bind window resize event
        # self.bind("<Configure>", self.on_resize)
        self.update_idletasks()

    def browse_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")]
        )
        if file_path:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, file_path)
            self.display_image(file_path)

    def display_image(self, image_path):
        try:
            img = Image.open(image_path)
            img.thumbnail((200, 200))  # Resize the image to fit in the label
            tk_image = ImageTk.PhotoImage(img)
            self.image_label.config(image=tk_image)
            self.image_label.image = (
                tk_image  # Keep reference to avoid garbage collection
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

    def compress_image_to_size(self):
        input_path = self.input_entry.get()
        target_size_kb = self.size_entry.get()

        if not os.path.exists(input_path):
            messagebox.showerror("Error", "Please select a valid image.")
            return

        if not target_size_kb.isdigit():
            messagebox.showerror("Error", "Please enter a valid target size.")
            return

        target_size_kb = int(target_size_kb)
        target_size_bytes = target_size_kb * 1024  # Convert KB to bytes

        try:
            with Image.open(input_path) as img:
                if img.format != "JPEG":
                    img = img.convert("RGB")

                # Perform binary search to find the correct compression quality
                low, high = 1, 95  # JPEG quality range
                best_quality = high
                while low <= high:
                    mid = (low + high) // 2
                    output = BytesIO()
                    img.save(output, format="JPEG", quality=mid)
                    compressed_size = output.tell()

                    if compressed_size <= target_size_bytes:
                        best_quality = mid
                        low = mid + 1  # Try a higher quality (larger size)
                    else:
                        high = mid - 1  # Try a lower quality (smaller size)

                # Save compressed image with the best quality found
                output_path = filedialog.asksaveasfilename(defaultextension=".jpg")
                if output_path:
                    img.save(output_path, format="JPEG", quality=best_quality)
                    messagebox.showinfo(
                        "Success",
                        f"Image compressed and saved at quality {best_quality}!",
                    )
                else:
                    messagebox.showinfo("Cancelled", "Saving operation cancelled.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def drop_image(self, event):
        # Get the dropped file path and load the image
        file_path = event.data
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, file_path.strip("{}"))  # Remove curly braces
        self.display_image(file_path.strip("{}"))

    def format_size(self, size):
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} GB"

    def on_resize(self, event):
        self.update()


if __name__ == "__main__":
    app = ImageCompressorGUI()
    app.mainloop()
