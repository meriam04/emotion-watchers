import os
from tkinter import Tk, Canvas, Button, filedialog, Scrollbar, Toplevel, Label
from PIL import Image, ImageTk
import logging


class ImageCropper:
    """A class for cropping images using a Tkinter GUI."""

    def __init__(self, master, image_path):
        """Initialize the ImageCropper object.

        Args:
            master (Tk): The main Tkinter window.
            image_path (str): The path of the image to be cropped.
        """

        logging.debug(f"ImageCropper: __init__ called with image_path: {image_path}")

        # Main Tkinter window
        self.master = master
        # Path of the image to be cropped
        self.image_path = image_path
        # Attributes to store the loaded image, its dimensions, and cropping coordinates
        self.img = None
        self.tk_img = None
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        # Attributes to keep track of cropping progress
        self.images_cropped = 0
        self.total_images = 1
        # Flag to prevent multiple success message dialogs
        self.showed_success_message = False

        # Create a canvas for displaying the image
        self.canvas = Canvas(master)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Add a vertical scrollbar to the canvas
        self.scrollbar = Scrollbar(master, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Add buttons for cropping the selected image and cropping all images
        self.crop_button = Button(master, text="Crop", command=self.crop_image)
        self.crop_button.pack()
        self.crop_all_button = Button(
            master, text="Crop All", command=self.crop_all_images
        )
        self.crop_all_button.pack()

        # Load and display the selected image
        self.load_image()

        # Bind mouse events for cropping
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_click)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)

    def load_image(self):
        """Load and display the selected image on the canvas."""

        # Open the image using PIL
        self.img = Image.open(self.image_path)
        # Convert the image to a Tkinter-compatible format
        self.tk_img = ImageTk.PhotoImage(self.img)

        # Display the image on the canvas
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
        # Configure the canvas to allow scrolling
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def on_mouse_click(self, event):
        """Record the starting point of the cropping rectangle"""

        # Get the x and y coordinates of the mouse click relative to the canvas
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

    def on_mouse_drag(self, event):
        """Update the cropping rectangle as the mouse is dragged"""

        # Get the current x and y coordinates of the mouse drag relative to the canvas
        self.end_x = self.canvas.canvasx(event.x)
        self.end_y = self.canvas.canvasy(event.y)

        # Adjust the cropping rectangle to ensure it remains square
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

        # Update the cropping rectangle on the canvas
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
        """Crop the selected region of the image"""

        try:
            # Define the cropping box based on the selected region
            crop_box = (
                min(self.start_x, self.end_x),
                min(self.start_y, self.end_y),
                max(self.start_x, self.end_x),
                max(self.start_y, self.end_y),
            )
            # Crop the image using the defined box
            cropped_img = self.img.crop(crop_box)

            # Save the cropped image in a new cropped folder
            cropped_folder = os.path.join(os.path.dirname(self.image_path), "cropped")
            if not os.path.exists(cropped_folder):
                os.makedirs(cropped_folder)

            base_name = os.path.basename(self.image_path)
            file_name_without_extension, file_extension = os.path.splitext(base_name)

            cropped_file_name = f"{file_name_without_extension}_c{file_extension}"
            cropped_file_path = os.path.join(cropped_folder, cropped_file_name)

            cropped_img.save(cropped_file_path)

            # Increment the count of images cropped
            self.images_cropped += 1

            # Close the main dialog window after all images are cropped
            if self.images_cropped == self.total_images:
                self.show_success_message()

        except Exception as e:
            print(f"Error cropping image: {e}")

    def crop_all_images(self):
        """Crop all images in the same directory as the selected image"""

        try:
            # Get the directory containing the selected image
            folder_path = os.path.dirname(self.image_path)
            # Filter the image files in the directory
            image_files = [
                filename
                for filename in os.listdir(folder_path)
                if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))
            ]
            # Set the total number of images to be cropped
            self.total_images = len(image_files)

            # Crop each image in the directory
            for filename in image_files:
                # Construct the path to the image file
                image_path = os.path.join(folder_path, filename)
                # Load and display the image
                self.image_path = image_path
                self.load_image()
                self.crop_image()

            # Show success message when done
            if self.images_cropped == self.total_images:
                self.show_success_message()
        except Exception as e:
            print(f"Error cropping images: {e}")

    def show_success_message(self):
        """Display a success message after cropping all images."""

        # Check if the success message has already been displayed
        if self.showed_success_message:
            return

        # Create a new top-level window for the success message
        success_dialog = Toplevel(self.master)
        success_dialog.title("Success")

        # Display the number of images cropped successfully
        Label(
            success_dialog, text=f"{self.images_cropped} image(s) cropped successfully!"
        ).pack()

        # Add a button to close the success message and exit the application
        Button(success_dialog, text="OK", command=self.master.destroy).pack()

        # Set the flag to indicate that the success message has been displayed
        self.showed_success_message = True


def run_image_cropper(initial_dir=os.getcwd()):
    """Run the image cropper application."""

    if not os.path.exists(initial_dir):
        initial_dir = os.getcwd()

    cropped_directory = None

    # Define the supported file types for image selection
    file_types = [
        ("PNG files", "*.png"),
        ("JPEG files", "*.jpeg"),
        ("JPG files", "*.jpg"),
        ("GIF files", "*.gif"),
        ("All files", "*.*"),
    ]

    # Prompt the user to select an image file
    image_path = filedialog.askopenfilename(
        title="Select Image File", filetypes=file_types, initialdir=initial_dir
    )

    # If an image is selected, run the image cropper application
    if not image_path:
        logging.debug("ImageCropper: no image selected")
        return

    # Create the main Tkinter window for the image cropper
    root = Tk()
    root.title("Image Cropper")

    logging.debug("ImageCropper: main Tkinter window created")

    # Open the selected image file and get its dimensions
    img = Image.open(image_path)
    width, height = img.size

    root.geometry(f"{width}x{height}")

    # Initialize the ImageCropper object with the selected image
    ImageCropper(root, image_path)

    # Bind the on_window_close function to execute when the window is closed
    # def on_window_close():
    #     """Function to execute when the Tkinter window is closed."""
    #     nonlocal cropped_directory
    #     if cropped_directory:
    #         root.destroy()

    # root.protocol("WM_DELETE_WINDOW", on_window_close)

    logging.debug("ImageCropper: on_window_close function bound to window close event")

    # Start the Tkinter event loop
    root.mainloop()

    logging.debug("ImageCropper: Tkinter event loop started")
    # return

    # Once the Tkinter window is closed, get the directory where cropped images are saved
    # cropped_directory = os.path.join(os.path.dirname(image_path), "cropped")

    return cropped_directory


def run_image_cropper_with_image(image_path):
    """Run the image cropper application with a specified image file."""

    if not os.path.exists(image_path):
        logging.error("Error: Image file does not exist")
        return
    # Open the selected image file and get its dimensions
    img = Image.open(image_path)
    width, height = img.size

    # Create the main Tkinter window for the image cropper
    root = Tk()
    root.title("Image Cropper")
    root.geometry(f"{width}x{height}")

    # Initialize the ImageCropper object with the selected image
    image_cropper = ImageCropper(root, image_path)

    # Start the Tkinter event loop
    root.mainloop()


if __name__ == "__main__":
    initial_directory = os.getcwd()
    logging.basicConfig(level=logging.DEBUG)
    image_paths = [
        "/Users/meriam/Coding/emotion-watchers/data/meriam-test-videos/2_cs_anger/2_cs_anger_0.0.png",
        "/Users/meriam/Coding/emotion-watchers/data/meriam-test-videos/1_cs_joy/1_cs_joy_2.0.png",
    ]
    run_image_cropper_with_image(image_paths)
