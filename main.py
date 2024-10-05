import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
from tkinter import ttk
import requests
import sv_ttk
import os
import json
import pygetwindow as gw
from PIL import ImageGrab
import time

DEFAULT_USERNAME = "WebhookBot"
DEFAULT_AVATAR_URL = None


class DiscordWebhookUtility:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_message(self, content, username=DEFAULT_USERNAME, avatar_url=DEFAULT_AVATAR_URL):
        data = {
            "content": content,
            "username": username,
        }
        if avatar_url:
            data["avatar_url"] = avatar_url

        result = requests.post(self.webhook_url, json=data)
        return result.ok

    def send_embed(self, title, description, color=0x7289DA, image_path=None, username=DEFAULT_USERNAME,
                   avatar_url=DEFAULT_AVATAR_URL):
        embed = {
            "title": title,
            "description": description,
            "color": color
        }

        data = {
            "username": username,
            "embeds": [embed],
        }
        if avatar_url:
            data["avatar_url"] = avatar_url

        files = None
        if image_path and os.path.exists(image_path):
            with open(image_path, 'rb') as image_file:
                files = {
                    'file': (os.path.basename(image_path), image_file, 'application/octet-stream')
                }
                data["embeds"][0]["image"] = {"url": f"attachment://{os.path.basename(image_path)}"}

                result = requests.post(
                    self.webhook_url,
                    data={"payload_json": json.dumps(data)},
                    files=files
                )
        else:
            result = requests.post(self.webhook_url, json=data)

        return result.ok

    def send_file(self, file_path, username=DEFAULT_USERNAME, content=""):
        with open(file_path, 'rb') as file:
            files = {'file': file}
            data = {
                "content": content,
                "username": username,
            }

            result = requests.post(self.webhook_url, data=data, files=files)
            return result.ok

    def send_screenshot(self, save_to_pc=False, username=DEFAULT_USERNAME, content="Screenshot captured"):
        window = gw.getWindowsWithTitle('Discord Webhook Utility')[0]
        window.minimize()

        time.sleep(1)

        screenshot = ImageGrab.grab()
        screenshot_path = "screenshot.png"
        screenshot.save(screenshot_path)

        window.restore()

        if save_to_pc:
            save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG Files", "*.png")])
            if save_path:
                screenshot.save(save_path)

        return self.send_file(screenshot_path, username=username, content=content)


class DiscordWebhookApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Discord Webhook Utility")
        self.geometry("500x900")

        sv_ttk.set_theme("dark")

        self.webhook_url = tk.StringVar()
        self.embed_color = 0x7289DA
        self.image_path = None
        self.save_screenshot = tk.BooleanVar(value=False)

        ttk.Label(self, text="Webhook URL:").pack(pady=5)
        self.webhook_url_entry = ttk.Entry(self, textvariable=self.webhook_url, width=50)
        self.webhook_url_entry.pack(pady=5)

        self.message_frame = ttk.LabelFrame(self, text="Send Message", padding=(10, 10))
        self.message_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(self.message_frame, text="Message:").pack(anchor="w")
        self.message_content = ttk.Entry(self.message_frame, width=50)
        self.message_content.pack(pady=5)

        ttk.Button(self.message_frame, text="Send Message", command=self.send_message).pack(pady=5)

        self.embed_frame = ttk.LabelFrame(self, text="Send Embed", padding=(10, 10))
        self.embed_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(self.embed_frame, text="Embed Title:").pack(anchor="w")
        self.embed_title = ttk.Entry(self.embed_frame, width=50)
        self.embed_title.pack(pady=5)

        ttk.Label(self.embed_frame, text="Embed Description:").pack(anchor="w")
        self.embed_description = ttk.Entry(self.embed_frame, width=50)
        self.embed_description.pack(pady=5)

        ttk.Button(self.embed_frame, text="Select Embed Color", command=self.select_color).pack(pady=5)

        ttk.Button(self.embed_frame, text="Attach Image", command=self.select_image).pack(pady=5)
        self.image_label = ttk.Label(self.embed_frame, text="No image selected.")
        self.image_label.pack(pady=5)

        ttk.Button(self.embed_frame, text="Send Embed", command=self.send_embed).pack(pady=5)

        self.file_frame = ttk.LabelFrame(self, text="Send File", padding=(10, 10))
        self.file_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Button(self.file_frame, text="Select File", command=self.select_file).pack(pady=5)
        self.selected_file_label = ttk.Label(self.file_frame, text="No file selected.")
        self.selected_file_label.pack()

        ttk.Button(self.file_frame, text="Send File", command=self.send_file).pack(pady=5)

        self.screenshot_frame = ttk.LabelFrame(self, text="Send Screenshot", padding=(10, 10))
        self.screenshot_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Checkbutton(self.screenshot_frame, text="Save screenshot to PC", variable=self.save_screenshot).pack(pady=5)

        ttk.Button(self.screenshot_frame, text="Send Screenshot", command=self.send_screenshot).pack(pady=5)

        self.selected_file = None

    def send_message(self):
        if not self.webhook_url.get():
            messagebox.showerror("Error", "Please provide a webhook URL.")
            return

        content = self.message_content.get()
        if not content:
            messagebox.showerror("Error", "Message content cannot be empty.")
            return

        self.webhook_utility = DiscordWebhookUtility(self.webhook_url.get())
        success = self.webhook_utility.send_message(content)

        if success:
            messagebox.showinfo("Success", "Message sent successfully!")
        else:
            messagebox.showerror("Error", "Failed to send the message.")

    def send_embed(self):
        if not self.webhook_url.get():
            messagebox.showerror("Error", "Please provide a webhook URL.")
            return

        title = self.embed_title.get()
        description = self.embed_description.get()

        if not title or not description:
            messagebox.showerror("Error", "Embed title and description cannot be empty.")
            return

        self.webhook_utility = DiscordWebhookUtility(self.webhook_url.get())
        success = self.webhook_utility.send_embed(title, description, color=self.embed_color,
                                                  image_path=self.image_path)

        if success:
            messagebox.showinfo("Success", "Embed sent successfully!")
        else:
            messagebox.showerror("Error", "Failed to send the embed.")

    def select_file(self):
        self.selected_file = filedialog.askopenfilename()
        if self.selected_file:
            self.selected_file_label.config(text=self.selected_file)

    def send_file(self):
        if not self.webhook_url.get():
            messagebox.showerror("Error", "Please provide a webhook URL.")
            return

        if not self.selected_file:
            messagebox.showerror("Error", "No file selected.")
            return

        self.webhook_utility = DiscordWebhookUtility(self.webhook_url.get())
        success = self.webhook_utility.send_file(self.selected_file)

        if success:
            messagebox.showinfo("Success", "File sent successfully!")
        else:
            messagebox.showerror("Error", "Failed to send the file.")

    def send_screenshot(self):
        if not self.webhook_url.get():
            messagebox.showerror("Error", "Please provide a webhook URL.")
            return

        save_to_pc = self.save_screenshot.get()
        self.webhook_utility = DiscordWebhookUtility(self.webhook_url.get())
        success = self.webhook_utility.send_screenshot(save_to_pc)

        if success:
            messagebox.showinfo("Success", "Screenshot sent successfully!")
        else:
            messagebox.showerror("Error", "Failed to send the screenshot.")

    def select_color(self):
        color_code = colorchooser.askcolor(title="Choose Embed Color")[1]
        if color_code:
            self.embed_color = int(color_code[1:], 16)

    def select_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if self.image_path:
            self.image_label.config(text=os.path.basename(self.image_path))


if __name__ == "__main__":
    app = DiscordWebhookApp()
    app.mainloop()
