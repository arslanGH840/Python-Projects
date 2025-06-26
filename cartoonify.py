import cv2
import numpy as np
import easygui
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import os

# Load Haar cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def cartoonify_image(img_path):
    img = cv2.imread(img_path)
    img = cv2.resize(img, (640, 480))

    # Detect face
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    if len(faces) == 0:
        raise ValueError("No face detected in the image.")

    # Apply stylization
    cartoon = cv2.stylization(img, sigma_s=100, sigma_r=0.25)
    return cartoon

def save_image(cartoon, original_path):
    filename = "cartoonified_Image"
    extension = os.path.splitext(original_path)[1]
    dir_path = os.path.dirname(original_path)
    save_path = os.path.join(dir_path, filename + extension)
    cv2.imwrite(save_path, cartoon)
    messagebox.showinfo("Image Saved", f"Image saved as {save_path}")

def show_image(img):
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    imgtk = ImageTk.PhotoImage(Image.fromarray(rgb))
    display_label.configure(image=imgtk)
    display_label.image = imgtk

def upload_image():
    img_path = easygui.fileopenbox()
    if img_path:
        try:
            cartoon = cartoonify_image(img_path)
            show_image(cartoon)
            save_btn.config(state=NORMAL)
            save_btn.config(command=lambda: save_image(cartoon, img_path))
        except Exception as e:
            messagebox.showerror("Error", str(e))

# =================== GUI ===================

top = Tk()
top.geometry('800x800')
top.title('Cartoonify Your Image')
top.configure(bg='#f0f2f5')

# Fonts and colors
font_heading = ('Segoe UI', 24, 'bold')
font_button = ('Segoe UI', 11, 'bold')
btn_bg = '#5865F2'
btn_fg = 'white'
hover_bg = '#4752c4'

# Header
header = Label(top, text="Cartoonify Your Image!", font=font_heading,
               bg='#f0f2f5', fg='#222222')
header.pack(pady=30)

# Image Display Frame
display_frame = Frame(top, bg='white', bd=2, relief=RIDGE)
display_frame.pack(pady=20)
display_label = Label(display_frame, bg='white')
display_label.pack()

# Buttons Frame
btn_frame = Frame(top, bg='#f0f2f5')
btn_frame.pack(pady=20)

def on_enter(e): e.widget.config(bg=hover_bg)
def on_leave(e): e.widget.config(bg=btn_bg)

upload_btn = Button(btn_frame, text="Upload Image", font=font_button,
                    bg=btn_bg, fg=btn_fg, padx=20, pady=10, bd=0,
                    activebackground=hover_bg, cursor="hand2", command=upload_image)
upload_btn.grid(row=0, column=0, padx=10)
upload_btn.bind("<Enter>", on_enter)
upload_btn.bind("<Leave>", on_leave)

save_btn = Button(btn_frame, text="Save Cartoon Image", font=font_button,
                  bg=btn_bg, fg=btn_fg, padx=20, pady=10, bd=0,
                  activebackground=hover_bg, cursor="hand2", state=DISABLED)
save_btn.grid(row=0, column=1, padx=10)
save_btn.bind("<Enter>", on_enter)
save_btn.bind("<Leave>", on_leave)

top.mainloop()
