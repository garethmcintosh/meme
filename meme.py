import argparse
import os
import random
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import imageio


# Function to calculate the text size
def scale_font(draw, text, box_width, box_height, max_font_size=None):
    font_size = 1
    font = ImageFont.truetype("arial.ttf", font_size)
    while True:
        w, h = draw.textsize(text, font=font)
        if (w < box_width and h < box_height) and (
            not max_font_size or font_size < max_font_size
        ):
            font_size += 1
            font = ImageFont.truetype("arial.ttf", font_size)
        else:
            return font


def process_frame(img, args):
    if args.type == "caption":
        caption_height = int(img.height * 0.15)
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
        font = scale_font(draw, args.text, img.width / 1.25, img.height // 2)
        text_width, text_height = font.getsize(args.text)
        if args.position == "top":
            text_position = ((img.width - text_width) // 2, img.height // 15)
        elif args.position == "bottom":
            text_position = (
                (img.width - text_width) // 2,
                img.height - text_height - img.height // 8,
            )
        white = (255, 255, 255)
        black = (0, 0, 0)
        stroke_width = 2
        draw.text(
            text_position,
            args.text,
            fill=white,
            font=font,
            stroke_width=stroke_width,
            stroke_fill=black,
        )
    else:
        print(f"Invalid meme type: {args.type}")
        exit(1)

    draw = ImageDraw.Draw(final_img)
    font = scale_font(draw, args.mark, img.width // 4, img.height // 4, max_font_size=15)
    text_width, text_height = font.getsize(args.mark)

    # Create a centered box and then calculate a random position for watermark inside it
    center_x, center_y = final_img.width // 2, final_img.height // 2
    box_width, box_height = img.width // 4, img.height // 4
    min_x = center_x - box_width // 2
    min_y = center_y - box_height // 2

    random_x = random.randint(min_x, min_x + box_width - text_width)
    random_y = random.randint(min_y, min_y + box_height - text_height)
    watermark_position = (random_x, random_y)
    white = (255, 255, 255)
    draw.text(watermark_position, args.mark, fill=white, font=font)

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
    choices=["top", "bottom"],
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
