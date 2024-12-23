import cv2
from tkinter import *
from PIL import Image, ImageTk

width = 640
height = 480


# Function to display the webcam feed
def update_frame():
    global cap, canvas, photo
    ret, frame = cap.read()
    if ret:
        # Convert the frame to an image format Tkinter can use
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image=img)
        canvas.create_image(0, 0, anchor=NW, image=photo)

    # Schedule the next frame update
    root.after(10, update_frame)

# Initialize the webcam
cap = cv2.VideoCapture(0)

# Create the main Tkinter window
root = Tk()
root.title("Webcam Viewer")
root.geometry(f"{width}x{height}")

# Create a canvas for displaying the webcam feed
canvas = Canvas(root, width=width, height=height)
canvas.pack()

# Start updating the frames
update_frame()

# Run the Tkinter event loop
root.mainloop()

# Release the webcam when the app is closed
cap.release()
