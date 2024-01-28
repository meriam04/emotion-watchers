import os
from tkinter import Tk, Canvas, Button, filedialog
from PIL import Image, ImageTk

class ImageCropper:
    def __init__(self, master, image_path):
        self.master = master
        self.image_path = image_path
        self.img = None
        self.tk_img = None  # Keep a reference to the PhotoImage
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0

        # Create GUI components
        self.canvas = Canvas(master)
        self.canvas.pack()

        self.crop_button = Button(master, text="Crop", command=self.crop_image)
        self.crop_button.pack()

        self.crop_all_button = Button(master, text="Crop All", command=self.crop_all_images)
        self.crop_all_button.pack()

        # Load the selected image
        self.load_image()

        # Bind events
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_click)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)

    def load_image(self):
        self.img = Image.open(self.image_path)
        self.tk_img = ImageTk.PhotoImage(self.img)

        # Set canvas size to match the image size
        self.canvas.config(width=self.img.width, height=self.img.height)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

    def on_mouse_click(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def on_mouse_drag(self, event):
        self.end_x = event.x
        self.end_y = event.y
        self.canvas.delete("crop_rect")
        self.canvas.create_rectangle(self.start_x, self.start_y, self.end_x, self.end_y, outline="red", tags="crop_rect")

    def crop_image(self):
        try:
            crop_box = (min(self.start_x, self.end_x), min(self.start_y, self.end_y), max(self.start_x, self.end_x), max(self.start_y, self.end_y))
            cropped_img = self.img.crop(crop_box)

            # Save the crop coordinates
            crop_coordinates_file = os.path.join(os.path.dirname(self.image_path), 'crop_coordinates.txt')
            with open(crop_coordinates_file, 'a') as f:
                f.write(f"{os.path.basename(self.image_path)} {crop_box}\n")

            # Save the cropped image
            cropped_img.save(os.path.join(os.path.dirname(self.image_path), f"cropped_{os.path.basename(self.image_path)}"))
        except Exception as e:
            print(f"Error cropping image: {e}")

    def crop_all_images(self):
        folder_path = os.path.dirname(self.image_path)
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                image_path = os.path.join(folder_path, filename)
                self.image_path = image_path
                self.load_image()
                self.crop_image()

if __name__ == "__main__":
    root = Tk()
    root.title("Image Cropper")

    # Ask user to select an image file
    image_path = filedialog.askopenfilename(title="Select Image File")

    if image_path:
        cropper = ImageCropper(root, image_path)
        root.mainloop()
