import argparse
import os
from PIL import Image, ImageDraw, ImageFont

# Function to calculate the text size
def scale_font(draw, caption, box_width, max_font_size=None):
    font_size = 1
    font = ImageFont.truetype('arial.ttf', font_size)
    # Increase font size until text width is smaller than box width
    while draw.textsize(caption, font=font)[0] < box_width:
        if max_font_size and font_size >= max_font_size:
            break
        font_size += 1
        font = ImageFont.truetype('arial.ttf', font_size)
    return font

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Create a meme image')
parser.add_argument('image_file', help='input image file')
parser.add_argument('caption', help='caption for the image')
parser.add_argument('watermark', help='watermark for the image')
parser.add_argument('--meme_type', choices=['caption', 'overlay'], help='type of meme to generate')
parser.add_argument('--text_position', choices=['top', 'bottom'], default='top', help='position of the caption text')
args = parser.parse_args()

# Get the full path of the input image file
image_path = os.path.join('input/', args.image_file)

# Open image from input folder
img = Image.open(image_path)

if args.meme_type == "caption":
    # Calculate the size of the caption box (just the width of the image and 15% of its height)
    caption_height = int(img.height * 0.15)
    caption_box = (img.width, caption_height)

    # Create a new image for the caption
    caption_img = Image.new('RGB', caption_box, color=(255, 255, 255))

    # Draw the caption on the new image
    draw = ImageDraw.Draw(caption_img)
    font = scale_font(draw, args.caption, img.width - 20)  # calculate the scaled font size
    text_height = font.getsize(args.caption)[1]
    
    if args.text_position == 'top':
        text_position = (10, (caption_height - text_height) // 2)  # center text vertically with some padding
    elif args.text_position == 'bottom':
        text_position = (10, caption_height - text_height - 25)  # position it at the bottom with some padding
    
    black = (0, 0, 0)
    draw.text(text_position, args.caption, fill=black, font=font)

    # Append the images
    final_img = Image.new('RGB', (img.width, img.height + caption_height))
    
    if args.text_position == 'top':
        final_img.paste(caption_img, (0, 0))
        final_img.paste(img, (0, caption_height))
    elif args.text_position == 'bottom':
        final_img.paste(img, (0, 0))
        final_img.paste(caption_img, (0, img.height))

    # Draw the watermark
    draw = ImageDraw.Draw(final_img)
    font = scale_font(draw, args.watermark, img.width - 20, max_font_size=20)  # calculate the scaled font size and limit it to 20
    text_width, text_height = font.getsize(args.watermark)
    white = (255, 255, 255)
    if args.text_position == 'top':
        watermark_position = (10, final_img.height - text_height - 10)  # position it at the bottom left corner of image with some padding
    elif args.text_position == 'bottom':
        watermark_position = (10, 10)  # position it at the top left corner of image with some padding

    draw.text(watermark_position, args.watermark, fill=white, font=font)

elif args.meme_type == "overlay":
    # Create a copy of the original image
    final_img = img.copy()

    # Draw the caption on top of the image
    draw = ImageDraw.Draw(final_img)
    font_size = min(img.width, img.height) // 10  # Adjust the font size based on the image size
    font = ImageFont.truetype('arial.ttf', font_size)
    text_width, text_height = font.getsize(args.caption)

    if args.text_position == 'top':
        text_position = ((img.width - text_width) // 2, img.height // 8)  # Center text horizontally and position it on the top half of the image
    elif args.text_position == 'bottom':
        text_position = ((img.width - text_width) // 2, img.height - text_height - img.height // 8)  # Center text horizontally and position it on the bottom half of the image

    white = (255, 255, 255)
    black = (0, 0, 0)
    stroke_width = 4
    draw.text(text_position, args.caption, fill=white, font=font, stroke_width=stroke_width, stroke_fill=black)


    # Draw the watermark
    font = scale_font(draw, args.watermark, img.width - 20, max_font_size=20)  # calculate the scaled font size and limit it to 20
    text_width, text_height = font.getsize(args.watermark)
    text_position = (10, img.height - text_height - 10)  # position it at the bottom left corner of image with some padding
    draw.text(text_position, args.watermark, fill=white, font=font, stroke_width=stroke_width, stroke_fill=black)

else:
    print(f"Invalid meme type: {args.meme_type}")
    exit(1)

# Get original file name and extension
file_name, file_ext = args.image_file.rsplit('.', 1)
file_ext = file_ext.upper()

# Check if final image name already exists
try:
    with open(f"output/{file_name}_meme.{file_ext}"):
        print("File already exists!")
        input_val = input("Do you want to overwrite it? (y/n): ")
        if input_val.lower() == "y":
            final_img.save(f"output/{file_name}_meme.{file_ext}", quality=15)
            print("File saved!")
        else:
            print("File not saved!")
except IOError:
    print("File does not exist. Saving...")
    final_img.save(f"output/{file_name}_meme.{file_ext}", quality=15)
