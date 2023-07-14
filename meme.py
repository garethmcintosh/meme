import argparse
import os
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import imageio


# Function to calculate the text size
def scale_font(draw, caption, box_width, box_height, max_font_size=None):
    font_size = 1
    font = ImageFont.truetype("arial.ttf", font_size)
    # Increase font size until text width is smaller than box width
    while True:
        w, h = draw.textsize(caption, font=font)
        if (w < box_width and h < box_height) and (
            not max_font_size or font_size < max_font_size
        ):
            font_size += 1
            font = ImageFont.truetype("arial.ttf", font_size)
        else:
            return font


def process_frame(img, args):
    if args.meme_type == "caption":
        caption_height = int(img.height * 0.15)
        caption_box = (img.width, caption_height)
        caption_img = Image.new("RGB", caption_box, color=(255, 255, 255))
        draw = ImageDraw.Draw(caption_img)
        font = scale_font(draw, args.caption, img.width - 20, caption_height)
        text_height = font.getsize(args.caption)[1]
        if args.text_position == "top":
            text_position = (10, (caption_height - text_height) // 2)
        elif args.text_position == "bottom":
            text_position = (10, caption_height - text_height - 25)
        black = (0, 0, 0)
        draw.text(text_position, args.caption, fill=black, font=font)
        final_img = Image.new("RGB", (img.width, img.height + caption_height))
        if args.text_position == "top":
            final_img.paste(caption_img, (0, 0))
            final_img.paste(img, (0, caption_height))
        elif args.text_position == "bottom":
            final_img.paste(img, (0, 0))
            final_img.paste(caption_img, (0, img.height))
        draw = ImageDraw.Draw(final_img)
        font = scale_font(
            draw, args.watermark, img.width - 20, img.height // 8, max_font_size=10
        )
        text_width, text_height = font.getsize(args.watermark)
        white = (255, 255, 255)
        if args.text_position == "top":
            watermark_position = (10, final_img.height - text_height - 10)
        elif args.text_position == "bottom":
            watermark_position = (10, 10)
        draw.text(watermark_position, args.watermark, fill=white, font=font)
    elif args.meme_type == "overlay":
        final_img = img.copy()
        draw = ImageDraw.Draw(final_img)
        font = scale_font(draw, args.caption, img.width / 1.25, img.height // 2)
        text_width, text_height = font.getsize(args.caption)
        if args.text_position == "top":
            text_position = ((img.width - text_width) // 2, img.height // 15)
        elif args.text_position == "bottom":
            text_position = (
                (img.width - text_width) // 2,
                img.height - text_height - img.height // 8,
            )
        white = (255, 255, 255)
        black = (0, 0, 0)
        stroke_width = 2
        draw.text(
            text_position,
            args.caption,
            fill=white,
            font=font,
            stroke_width=stroke_width,
            stroke_fill=black,
        )
        font = scale_font(
            draw, args.watermark, img.width - 20, img.height // 8, max_font_size=10
        )
        text_width, text_height = font.getsize(args.watermark)
        text_position = (10, img.height - text_height - 10)
        draw.text(
            text_position,
            args.watermark,
            fill=white,
            font=font,
            stroke_width=stroke_width,
            stroke_fill=black,
        )
    else:
        print(f"Invalid meme type: {args.meme_type}")
        exit(1)
    return final_img


# Parse command-line arguments
parser = argparse.ArgumentParser(description="Create a meme image or video")
parser.add_argument("input_file", help="input image or video file")
parser.add_argument("caption", help="caption for the image/video")
parser.add_argument("watermark", help="watermark for the image/video")
parser.add_argument(
    "--meme_type", choices=["caption", "overlay"], help="type of meme to generate"
)
parser.add_argument(
    "--text_position",
    choices=["top", "bottom"],
    default="top",
    help="position of the caption text",
)
parser.add_argument(
    "--output_format",
    choices=["mp4", "gif"],
    default="mp4",
    help="output format for video files",
)

args = parser.parse_args()
input_path = os.path.join("input/", args.input_file)
file_name, file_ext = args.input_file.rsplit(".", 1)
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
    if args.meme_type == "caption":
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
    if args.output_format == "mp4":
        out = cv2.VideoWriter(
            os.path.join(output_dir, f"{file_name}_meme.mp4"),
            fourcc,
            fps,
            (width, height),
        )
        for frame in frames:
            out.write(cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR))
        out.release()
    elif args.output_format == "gif":
        imageio.mimsave(
            os.path.join(output_dir, f"{file_name}_meme.gif"),
            frames,
            duration=1.0 / fps,
        )
else:
    print(f"Invalid file extension: {file_ext}")
    exit(1)
