# Meme

Meme is a Python script that allows you to create two types of memes through cli: Caption and Overlay. The Caption meme type adds a caption above or below the image. The Overlay meme type overlays the caption on top or bottom of the image. Both types allow you to add a watermark as well.

## Requirements
- Python
- Pillow Python library

## Usage

Here's how to use the script:

```python memeify.py <image_file> <caption> <watermark> --meme_type <meme_type> --text_position <text_position>```


Parameters:

- `image_file`: This is the path to the image file you want to memeify. The image should be placed in the `input/` directory.
- `caption`: The caption text you want to add to the image.
- `watermark`: The watermark text you want to add to the image.
- `meme_type`: This is an optional argument. The type of meme you want to generate. It can be either `caption` or `overlay`. If not provided, the script will generate a `caption` type meme.
- `text_position`: This is an optional argument. The position of the text. It can be either `top` or `bottom`. If not provided, the script will put the text at the `top`.

Example usage:

```python memeify.py input\test.jpg "This is a caption" "watermark" --meme_type overlay --text_position bottom```


## Output

The output will be an image file with the same extension as the original, but the filename will be suffixed with `_meme`. The script will save the output file in the `output/` directory.

## Note

- If an output file with the same name already exists, the script will ask you if you want to overwrite it.
- The script will scale the caption and watermark text to fit the width of the image, but the maximum font size for the watermark is 20.
