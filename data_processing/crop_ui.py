import os
from tkinter import Tk, Canvas, Button, filedialog
from PIL import Image, ImageTk

class ImageCropper:
    def __init__(self, master, folder_path):
        self.master = master
        self.folder_path = folder_path
        self.image_list = [f for f in os.listdir(self.folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        self.current_image_index = 0
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0

        # Load the first image
        self.load_image()

        # Create GUI components
        self.canvas = Canvas(master, width=self.img.width, height=self.img.height)
        self.canvas.pack()

        self.crop_button = Button(master, text="Crop", command=self.crop_image)
        self.crop_button.pack()

        self.next_button = Button(master, text="Next Image", command=self.load_next_image)
        self.next_button.pack()

        # Bind events
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_click)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)

    def load_image(self):
        image_path = os.path.join(self.folder_path, self.image_list[self.current_image_index])
        self.img = Image.open(image_path)
        self.tk_img = ImageTk.PhotoImage(self.img)
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
        crop_box = (min(self.start_x, self.end_x), min(self.start_y, self.end_y), max(self.start_x, self.end_x), max(self.start_y, self.end_y))
        cropped_img = self.img.crop(crop_box)

        # Save the crop coordinates
        crop_coordinates_file = os.path.join(self.folder_path, 'crop_coordinates.txt')
        with open(crop_coordinates_file, 'a') as f:
            f.write(f"{self.image_list[self.current_image_index]} {crop_box}\n")

        # Save the cropped image
        cropped_img.save(os.path.join(self.folder_path, f"cropped_{self.image_list[self.current_image_index]}"))

    def load_next_image(self):
        # Move to the next image
        self.current_image_index = (self.current_image_index + 1) % len(self.image_list)
        self.load_image()

if __name__ == "__main__":
    root = Tk()
    root.title("Image Cropper")

    # Ask user to select a folder containing images
    folder_path = filedialog.askdirectory(title="Select Folder")

    if folder_path:
        cropper = ImageCropper(root, folder_path)
        root.mainloop()
