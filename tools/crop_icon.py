import os
from PIL import Image

def crop_black_borders():
    img_path = r"e:\apps\couple_friendly\app\src\main\res\drawable\custom_app_icon.png"
    if not os.path.exists(img_path):
        print(f"Error: {img_path} not found!")
        return

    # Load the image
    img = Image.open(img_path)
    img = img.convert("RGBA")
    width, height = img.size
    pixels = img.load()

    # Sample a small 15x15 patch in the top-left corner to get the average background color
    bg_sum_r = 0
    bg_sum_g = 0
    bg_sum_b = 0
    sample_size = 15
    for y in range(sample_size):
        for x in range(sample_size):
            r, g, b, _ = pixels[x, y]
            bg_sum_r += r
            bg_sum_g += g
            bg_sum_b += b
    
    bg_r = bg_sum_r / (sample_size * sample_size)
    bg_g = bg_sum_g / (sample_size * sample_size)
    bg_b = bg_sum_b / (sample_size * sample_size)
    print(f"Sampled average background color: R={bg_r:.1f}, G={bg_g:.1f}, B={bg_b:.1f}")

    # Find the bounding box of pixels that are significantly different from the background
    left = width
    right = 0
    top = height
    bottom = 0

    for y in range(height):
        for x in range(width):
            r, g, b, _ = pixels[x, y]
            # Euclidean distance in RGB space
            distance = ((r - bg_r)**2 + (g - bg_g)**2 + (b - bg_b)**2)**0.5
            if distance > 30:
                if x < left:
                    left = x
                if x > right:
                    right = x
                if y < top:
                    top = y
                if y > bottom:
                    bottom = y

    print(f"Detected content box: Left={left}, Top={top}, Right={right}, Bottom={bottom}")

    # Safety margin check
    if left >= right or top >= bottom:
        print("Error: Could not distinguish the borders of the icon!")
        return

    # Step 1: Crop slightly INSIDE the detected bounding box to completely exclude straight black lines
    margin = 12
    new_left = left + margin
    new_top = top + margin
    new_right = right - margin
    new_bottom = bottom - margin

    # Make it a perfect square
    crop_w = new_right - new_left
    crop_h = new_bottom - new_top
    dim = max(crop_w, crop_h)
    
    cx = (new_left + new_right) // 2
    cy = (new_top + new_bottom) // 2
    
    final_left = max(0, cx - dim // 2)
    final_top = max(0, cy - dim // 2)
    final_right = min(width, final_left + dim)
    final_bottom = min(height, final_top + dim)

    # Crop the image to the perfect square bounding box
    cropped = img.crop((final_left, final_top, final_right, final_bottom))
    cropped = cropped.convert("RGBA")
    
    W, H = cropped.size
    ccx, ccy = W // 2, H // 2
    cropped_pixels = cropped.load()

    # Step 2: Mathematically project the inner gradient OUTWARDS to paint over the curved border lines!
    # Corner threshold is C (about 18% of the width, ensuring it covers the curved boundary curve completely)
    C = int(W * 0.18)

    # Top-Left Corner
    for y in range(H):
        for x in range(W):
            if x + y < C:
                # Project onto x + y = C
                diff = C - (x + y)
                px = x + diff // 2
                py = y + diff - diff // 2
                if 0 <= px < W and 0 <= py < H:
                    cropped_pixels[x, y] = cropped_pixels[px, py]

    # Top-Right Corner
    for y in range(H):
        for x in range(W):
            xr = W - 1 - x
            if xr + y < C:
                diff = C - (xr + y)
                pxr = xr + diff // 2
                py = y + diff - diff // 2
                px = W - 1 - pxr
                if 0 <= px < W and 0 <= py < H:
                    cropped_pixels[x, y] = cropped_pixels[px, py]

    # Bottom-Left Corner
    for y in range(H):
        for x in range(W):
            yb = H - 1 - y
            if x + yb < C:
                diff = C - (x + yb)
                px = x + diff // 2
                pyb = yb + diff - diff // 2
                py = H - 1 - pyb
                if 0 <= px < W and 0 <= py < H:
                    cropped_pixels[x, y] = cropped_pixels[px, py]

    # Bottom-Right Corner
    for y in range(H):
        for x in range(W):
            xr = W - 1 - x
            yb = H - 1 - y
            if xr + yb < C:
                diff = C - (xr + yb)
                pxr = xr + diff // 2
                pyb = yb + diff - diff // 2
                px = W - 1 - pxr
                py = H - 1 - pyb
                if 0 <= px < W and 0 <= py < H:
                    cropped_pixels[x, y] = cropped_pixels[px, py]

    # Resize back to high resolution 512x512 using high quality Lanczos filter
    final_img = cropped.resize((512, 512), Image.Resampling.LANCZOS)

    # Save to both target locations
    final_img.save(img_path, "PNG")
    
    brain_path = r"C:\Users\mohan\.gemini\antigravity\brain\9c457dd7-6c8b-494c-a710-34b5edb2b71b\custom_app_icon.png"
    final_img.save(brain_path, "PNG")

    print("Success: Black borders and curved border lines completely painted over! 100% full-bleed square icon created!")

if __name__ == "__main__":
    crop_black_borders()
