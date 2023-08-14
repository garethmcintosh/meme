import argparse
import os
import random
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import imageio
import textwrap
import warnings
import shutil

warnings.filterwarnings("ignore")


# Function to calculate the text size and wrap it
def fit_text_to_box(draw, text, box_width, box_height, max_font_size=None):
    font_size = max_font_size or 100  # Start with a larger font size
    min_font_size = 10  # Don't go below this font size
    step_size = 10  # Adjust font size by this step size
    font = ImageFont.truetype("impact.ttf", font_size)

    while font_size >= min_font_size:
        text_lines = textwrap.wrap(
            text, width=int(box_width / (font_size * 0.35))
        )  # Adjusted divisor for wider lines
        line_heights = [draw.textsize(line, font=font)[1] for line in text_lines]
        line_widths = [draw.textsize(line, font=font)[0] for line in text_lines]
        max_line_width = max(line_widths)
        total_height = sum(line_heights)

        if max_line_width <= box_width and total_height <= box_height:
            # If the text fits, we're done
            return font, text_lines

        # If the text doesn't fit, decrease the font size
        font_size -= step_size
        font = ImageFont.truetype("impact.ttf", font_size)

    print("Text can't fit into the box, even at the smallest font size.")
    return font, text_lines


# Function to calculate the text size for caption
def scale_font(draw, text, box_width, box_height, max_font_size=None):
    font_size = 1
    font = ImageFont.truetype("impact.ttf", font_size)
    while True:
        w, h = draw.textsize(text, font=font)
        if (w < box_width and h < box_height) and (
            not max_font_size or font_size < max_font_size
        ):
            font_size += 1
            font = ImageFont.truetype("impact.ttf", font_size)
        else:
            return font


# Function to get custom position on image for test through ascii-graphical preview with instant input feedback
def get_custom_position(img_width, text_height):
    position = {"x": 10, "y": 0}  # Initialize y position to 0
    position_confirmed = False
    step = 10

    # Get the terminal height (number of rows)
    terminal_height = shutil.get_terminal_size().lines

    # If the terminal height is smaller than the desired height, adjust it
    if terminal_height < text_height // step:
        text_height = (terminal_height - 3) * step  # Leaving some space for other lines

    while position_confirmed is False:
        # Clear the console
        os.system("cls" if os.name == "nt" else "clear")

        print("+", "-" * (img_width // step - 2), "+")
        for _ in range(position["y"] // step):  # Add empty lines before the text
            print("|", " " * (img_width // step - 3), "|")
        spaces_before_text = position["x"] // step
        text_space_before = " " * spaces_before_text
        text_space_after = " " * (
            img_width // step - spaces_before_text - len("TEXT") - 1
        )
        print("|" + text_space_before + "TEXT" + text_space_after + "|")
        for _ in range(
            (text_height - position["y"]) // step
        ):  # Add empty lines after the text
            print("|", " " * (img_width // step - 3), "|")
        print("+", "-" * (img_width // step - 2), "+")

        user_input = input(
            "Move text with 'w', 'a' 's', 'd', or confirm position with 'x': "
        )

        if user_input == "w":
            position["y"] = max(0, position["y"] - step)
        elif user_input == "a":
            position["x"] = max(0, position["x"] - step)
        elif user_input == "s":
            position["y"] = min(
                text_height - step, position["y"] + step
            )  # Change to text_height
        elif user_input == "d":
            position["x"] = min(img_width - len("TEXT") * step, position["x"] + step)
        elif user_input == "x":
            position_confirmed = True

    return position


def process_frame(img, args):
    if args.type == "caption":
        caption_height = int(img.height * 0.075)
        caption_box = (img.width, caption_height)
        caption_img = Image.new("RGB", caption_box, color=(255, 255, 255))
        draw = ImageDraw.Draw(caption_img)
        font = scale_font(draw, args.text, img.width - 20, caption_height)
        text_height = font.getsize(args.text)[1]
        if args.position == "top":
            text_position = (10, (caption_height - text_height) // 2)
        elif args.position == "bottom":
            text_position = (10, caption_height - text_height - 25)
        black = (0, 0, 0)
        draw.text(text_position, args.text, fill=black, font=font)
        final_img = Image.new("RGB", (img.width, img.height + caption_height))
        if args.position == "top":
            final_img.paste(caption_img, (0, 0))
            final_img.paste(img, (0, caption_height))
        elif args.position == "bottom":
            final_img.paste(img, (0, 0))
            final_img.paste(caption_img, (0, img.height))

    elif args.type == "overlay":
        final_img = img.copy()
        draw = ImageDraw.Draw(final_img)
        font, text_lines = fit_text_to_box(
            draw, args.text, img.width, img.height // 2, max_font_size=150
        )
        white = (255, 255, 255)
        black = (0, 0, 0)
        stroke_width = 8

        for i, line in enumerate(text_lines):
            text_width, text_height = draw.textsize(line, font=font)
            if args.position == "top":
                text_position = (
                    (img.width - text_width) // 2,
                    img.height // 15 + i * text_height,
                )
            elif args.position == "bottom":
                text_position = (
                    (img.width - text_width) // 2,
                    img.height - text_height * (len(text_lines) - i) - img.height // 8,
                )
            elif args.position == "custom":
                position_dict = get_custom_position(img.width, text_height)
                text_position = (position_dict["x"], position_dict["y"])
            draw.text(
                text_position,
                line,
                fill=white,
                font=font,
                stroke_width=stroke_width,
                stroke_fill=black,
            )

    else:
        print(f"Invalid meme type: {args.type}")
        exit(1)

    draw = ImageDraw.Draw(final_img)
    font, watermark_lines = fit_text_to_box(
        draw, args.mark, img.width // 2, img.height // 2, max_font_size=25
    )

    # Create a centered box and then calculate a random position for watermark inside it
    center_x, center_y = final_img.width // 2, final_img.height // 2
    box_width, box_height = img.width // 2, img.height // 2  # Increased box size
    min_x = center_x - box_width // 2
    min_y = center_y - box_height // 2

    for i, line in enumerate(watermark_lines):
        text_width, text_height = font.getsize(line)
        random_x = random.randint(min_x, min_x + box_width - text_width)
        random_y = random.randint(min_y, min_y + box_height - text_height)
        watermark_position = (
            random_x,
            random_y + i * text_height,
        )  # Adjust y position based on line number
        white = (255, 255, 255)
        draw.text(watermark_position, line, fill=white, font=font)

    return final_img


# Parse command-line arguments
parser = argparse.ArgumentParser(description="Create a meme image or video")
parser.add_argument("file", help="Input image or video file")
parser.add_argument("text", help="Caption for the image/video")
parser.add_argument("mark", help="Watermark for the image/video")
parser.add_argument(
    "--type", choices=["caption", "overlay"], help="Type of meme to generate"
)
parser.add_argument(
    "--position",
    choices=["top", "bottom", "custom"],
    default="top",
    help="Position of the caption text",
)
parser.add_argument(
    "--format",
    choices=["mp4", "gif"],
    default="mp4",
    help="Output format for video files",
)

args = parser.parse_args()
input_path = os.path.join("input/", args.file)
file_name, file_ext = args.file.rsplit(".", 1)
file_ext = file_ext.lower()

frames = []

output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

if file_ext in ["jpg", "jpeg", "png", "bmp", "gif"]:
    img = Image.open(input_path)
    final_img = process_frame(img, args)
    final_img.save(os.path.join(output_dir, f"{file_name}_meme.{file_ext}"), quality=15)
elif file_ext in ["mp4", "avi", "mov", "mkv"]:
    video = cv2.VideoCapture(input_path)
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    fps = video.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    if args.type == "caption":
        height += int(height * 0.15)  # Adjust height for caption
    while True:
        ret, frame = video.read()
        if not ret:
            break
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        final_img = process_frame(img, args)
        final_frame = cv2.cvtColor(np.array(final_img), cv2.COLOR_RGB2BGR)
        frames.append(final_img)
    video.release()
