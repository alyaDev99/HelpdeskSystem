import tkinter as tk
from login_screen import LoginScreen

class FullscreenApp:
    def __init__(self, root):
        self.root = root

        # Get screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.rooPt.winfo_screenheight()
P
        # Set window to full screen
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")  # Fullscreen size
        self.root.attributes('-fullscreen', True)  # Set fullscreen mode

        # Disable resizing
        self.root.resizable(False, False)

        # Bind the Escape key to toggle fullscreen mode
        self.root.bind("<Escape>", self.toggle_fullscreen)

    def toggle_fullscreen(self, event=None):
        """ Toggle fullscreen on and off """
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)

    def run(self):
        # Initialize and display the login screen
        login_screen = LoginScreen(self.root)
        login_screen.run()

def main():
    # Create the root window
    root = tk.Tk()

    # Initialize the fullscreen functionality
    app = FullscreenApp(root)

    # Run the app
    app.run()

    # Prevent the root window from closing until the app finishes
    root.mainloop()

if __name__ == "__main__":
    main()