from PIL import Image, ImageDraw, ImageFont

# Create a white image
img = Image.new('RGB', (600, 200), color='white')
d = ImageDraw.Draw(img)

# Write some text that Tesseract can easily read
d.text((50, 50), "KMRL Safety Inspection Report", fill='black')
d.text((50, 100), "All systems operational. No issues found.", fill='black')

# Save it as PNG
img.save('sample_image.png')
print("✅ Created sample_image.png in your backend folder!")