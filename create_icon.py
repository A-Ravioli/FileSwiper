from PIL import Image, ImageDraw

# Create a new image with a white background
size = (256, 256)
image = Image.new('RGB', size, 'white')
draw = ImageDraw.Draw(image)

# Draw a simple swipe arrow
arrow_points = [
    (50, 128),  # Left point
    (156, 50),  # Top point
    (156, 90),  # Top rectangle left
    (206, 90),  # Top rectangle right
    (206, 166), # Bottom rectangle right
    (156, 166), # Bottom rectangle left
    (156, 206), # Bottom point
]

# Draw the arrow in blue
draw.polygon(arrow_points, fill='#4CAF50')

# Save as ICO file
image.save('app_icon.ico', format='ICO', sizes=[(256, 256)]) 