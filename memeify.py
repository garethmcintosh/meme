from PIL import Image, ImageDraw, ImageFont, ImageOps

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

# Prompt user for image file
image_file = input("Enter the image file name: ")

# Open image from input folder
img = Image.open(f'input/{image_file}')

# Prompt user for caption
caption = input("Enter the caption for the image: ")

# Prompt user for a watermark
watermark = input("Enter a watermark for the image: ")

# Calculate the size of the caption box (just the width of the image and 15% of its height)
caption_height = int(img.height * 0.15)
caption_box = (img.width, caption_height)

# Create a new image for the caption
caption_img = Image.new('RGB', caption_box, color=(255, 255, 255))

# Draw the caption on the new image
draw = ImageDraw.Draw(caption_img)
font = scale_font(draw, caption, img.width - 20)  # calculate the scaled font size
text_position = (10, (caption_height - font.getsize(caption)[1]) // 2)  # center text vertically with some padding
black = (0, 0, 0)
draw.text(text_position, caption, fill=black, font=font)

# Append the images
final_img = Image.new('RGB', (img.width, img.height + caption_height))
final_img.paste(caption_img, (0, 0))
final_img.paste(img, (0, caption_height))

# Draw the watermark
draw = ImageDraw.Draw(final_img)
font = scale_font(draw, watermark, img.width - 20, max_font_size=20)  # calculate the scaled font size and limit it to 20
text_position = (10, final_img.height - font.getsize(watermark)[1] - 10)  # position it at the bottom left corner of image with some padding
white = (255, 255, 255)
draw.text(text_position, watermark, fill=white, font=font)

# Get original file name and extension
file_name, file_ext = image_file.rsplit('.', 1)
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
