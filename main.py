from io import BytesIO
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from tkinterdnd2 import (
    TkinterDnD,
    DND_FILES,
)  # Import TkinterDnD for drag-and-drop functionality


class ImageCompressorGUI(TkinterDnD.Tk):  # Inherit from TkinterDnD.Tk
    def __init__(self):
        super().__init__()
        self.title("Image Compressor")
        self.geometry("400x300")  # Adjust window size as needed

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
            self.main_frame, text="Drop image here", bg="lightblue", relief="ridge"
        )
        self.drop_target.grid(row=1, columnspan=3, sticky="ew")
        self.drop_target.drop_target_register(DND_FILES)  # Register as a drop target
        self.drop_target.dnd_bind("<<Drop>>", self.drop_image)  # Bind the drop event

        # Compression quality label and dropdown
        self.quality_label = tk.Label(self.main_frame, text="Compression Quality:")
        self.quality_label.grid(row=2, column=0, sticky="w")
        self.quality_var = tk.StringVar(value="85")  # Default value
        self.quality_dropdown = tk.OptionMenu(
            self.main_frame, self.quality_var, *range(10, 101, 10)
        )
        self.quality_dropdown.grid(row=2, column=1, sticky="w")

        # Compress button
        self.compress_button = tk.Button(
            self.main_frame, text="Compress Image", command=self.compress_image
        )
        self.compress_button.grid(row=3, columnspan=3, sticky="ew")

        # Image display label
        self.image_label = tk.Label(self)
        self.image_label.pack()

        # Bind window resize event
        self.bind("<Configure>", self.on_resize)

    def browse_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")]
        )
        if file_path:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, file_path)
            self.display_image(file_path)

    def compress_image(self):
        input_path = self.input_entry.get()
        quality_value = self.quality_var.get()

        try:
            if not quality_value:
                quality_value = 85  # Default quality if not specified
            quality = int(quality_value)

            with Image.open(input_path) as img:
                # Convert to JPEG if necessary
                if img.format != "JPEG":
                    img = img.convert("RGB")

                # Compress
                output = BytesIO()
                img.save(output, format="JPEG", quality=quality)

                # Save compressed image
                output_path = filedialog.asksaveasfilename(defaultextension=".jpg")
                if output_path:
                    with open(output_path, "wb") as f:
                        f.write(output.getvalue())
                    messagebox.showinfo("Success", "Image compressed and saved!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def drop_image(self, event):
        file_path = event.data.strip(
            "{}"
        )  # Get the file path from the drop event and clean up
        if file_path:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, file_path)
            self.display_image(file_path)
        self.drop_target.config(bg="lightgreen")  # Indicate successful drop

    def on_resize(self, event):
        # Adjust the image display when the window is resized
        if self.input_entry.get():
            self.display_image(self.input_entry.get())

    def display_image(self, file_path):
        try:
            with Image.open(file_path) as img:
                # Resize image to fit window while keeping aspect ratio
                img.thumbnail((self.winfo_width() - 20, self.winfo_height() - 100))
                tk_image = ImageTk.PhotoImage(img)
                self.image_label.config(image=tk_image)
                self.image_label.image = tk_image
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display image: {e}")


if __name__ == "__main__":
    app = ImageCompressorGUI()
    app.mainloop()
