# Meme

Create two types of memes through CLI: Caption and Overlay. Caption adds a caption above or below the image. Overlay type overlays the caption on the top or bottom of the image.

## Requirements
- Python
- Pillow Python library

## Usage

```python
meme.py <image_file> <caption> <watermark> --type <meme_type> --position <text_position>
```
- `type`: This is an optional argument. The type of meme you want to generate. It can be either `caption` or `overlay`. If not provided, the script will generate a `caption` type meme.
- `position`: This is an optional argument. The position of the text. It can be either `top` or `bottom`. If not provided, the script will put the text at the `top`.
