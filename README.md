**Cartoonify Image Using Computer Vision**

This project transforms any user-uploaded image into a cartoon-style version using Python and OpenCV. It applies intelligent face detection to ensure the input image contains a human face before applying the cartoon filter. The application features a user-friendly graphical interface built with Tkinter and EasyGUI, making it accessible for non-technical users as well.

Once an image is uploaded, the system uses a Haar Cascade classifier to detect a face. If no face is found, the user receives an error message. If a face is detected, OpenCV’s stylization() function is applied to generate a cartoon-like effect. The final image is displayed inside the app, and users can save the cartoonified version with a single click.

This project is ideal for users who want to create cartoon avatars or artistic versions of their photos without needing professional software or manual editing.

**Features:**

Face detection to validate image input

Cartoon effect using OpenCV’s stylization filter

Clean, modern GUI for uploading, viewing, and saving images

Error handling for images without faces

**Technologies Used:**

Python 3

OpenCV

Tkinter

EasyGUI

Pillow (PIL)

**How to Run:**

Install required libraries with 'pip install opencv-python pillow easygui'

Run the script: python cartoonify.py

Use the GUI to upload an image and view/save the cartoonified result
