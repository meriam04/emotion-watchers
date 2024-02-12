import os
from tkinter import Tk, Canvas, Button, filedialog, Scrollbar, Toplevel, Label
from PIL import Image, ImageTk


class ImageCropper:
    def __init__(self, master, image_path):
        self.master = master
        self.image_path = image_path
        self.img = None
        self.tk_img = None
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        self.images_cropped = 0
        self.total_images = 1
        self.showed_success_message = False

        self.canvas = Canvas(master)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = Scrollbar(master, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.crop_button = Button(master, text="Crop", command=self.crop_image)
        self.crop_button.pack()

        self.crop_all_button = Button(
            master, text="Crop All", command=self.crop_all_images
        )
        self.crop_all_button.pack()

        self.load_image()

        self.canvas.bind("<ButtonPress-1>", self.on_mouse_click)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)

    def load_image(self):
        self.img = Image.open(self.image_path)
        self.tk_img = ImageTk.PhotoImage(self.img)

        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def on_mouse_click(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

    def on_mouse_drag(self, event):
        self.end_x = self.canvas.canvasx(event.x)
        self.end_y = self.canvas.canvasy(event.y)

        width = abs(self.end_x - self.start_x)
        height = abs(self.end_y - self.start_y)

        if width > height:
            if self.end_x < self.start_x:
                self.end_x = self.start_x - height
            else:
                self.end_x = self.start_x + height
        else:
            if self.end_y < self.start_y:
                self.end_y = self.start_y - width
            else:
                self.end_y = self.start_y + width

        self.canvas.delete("crop_rect")
        self.canvas.create_rectangle(
            self.start_x,
            self.start_y,
            self.end_x,
            self.end_y,
            outline="red",
            tags="crop_rect",
        )

    def crop_image(self):
        try:
            crop_box = (
                min(self.start_x, self.end_x),
                min(self.start_y, self.end_y),
                max(self.start_x, self.end_x),
                max(self.start_y, self.end_y),
            )
            cropped_img = self.img.crop(crop_box)

            crop_coordinates_file = os.path.join(
                os.path.dirname(self.image_path), "crop_coordinates.txt"
            )
            with open(crop_coordinates_file, "a") as f:
                f.write(f"{os.path.basename(self.image_path)} {crop_box}\n")

            cropped_folder = os.path.join(os.path.dirname(self.image_path), "cropped")
            if not os.path.exists(cropped_folder):
                os.makedirs(cropped_folder)

            cropped_img.save(
                os.path.join(
                    cropped_folder,
                    f"{os.path.basename(self.image_path).split('.')[0]}_c.{os.path.basename(self.image_path).split('.')[-1]}",
                )
            )

            # Increment the count of images cropped
            self.images_cropped += 1

            # Close the main dialog window after all images are cropped
            if self.images_cropped == self.total_images:
                self.show_success_message()

        except Exception as e:
            print(f"Error cropping image: {e}")

    def crop_all_images(self):
        try:
            folder_path = os.path.dirname(self.image_path)
            image_files = [
                filename
                for filename in os.listdir(folder_path)
                if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))
            ]
            self.total_images = len(image_files)

            for filename in os.listdir(folder_path):
                if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                    image_path = os.path.join(folder_path, filename)
                    self.image_path = image_path
                    self.load_image()
                    self.crop_image()

            # Show success message when done
            if self.images_cropped == self.total_images:
                self.show_success_message()
        except Exception as e:
            print(f"Error cropping images: {e}")

    def show_success_message(self):
        if self.showed_success_message:
            return
        success_dialog = Toplevel(self.master)
        success_dialog.title("Success")
        Label(
            success_dialog, text=f"{self.images_cropped} images cropped successfully!"
        ).pack()
        Button(success_dialog, text="OK", command=self.master.destroy).pack()
        self.showed_success_message = True


def run_image_cropper():
    file_types = [
        ("PNG files", "*.png"),
        ("JPEG files", "*.jpeg"),
        ("JPG files", "*.jpg"),
        ("GIF files", "*.gif"),
        ("All files", "*.*"),
    ]

    image_path = filedialog.askopenfilename(
        title="Select Image File", filetypes=file_types
    )

    if image_path:
        img = Image.open(image_path)
        width, height = img.size

        root = Tk()
        root.title("Image Cropper")
        root.geometry(f"{width}x{height}")

        cropper = ImageCropper(root, image_path)
        root.mainloop()


if __name__ == "__main__":
    run_image_cropper()
