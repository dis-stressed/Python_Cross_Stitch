import sys
from PIL import Image
from DMC import DMC
from SVG import SVG

#Function for Smoothing
def get_neighbours(pos, matrix):
    rows = len(matrix)
    cols = len(matrix[0]) if rows else 0
    width = 1
    for i in range(max(0, pos[0] - width), min(rows, pos[0] + width + 1)):
        for j in range(max(0, pos[1] - width), min(cols, pos[1] + width + 1)):
            if not (i == pos[0] and j == pos[1]):
                yield matrix[i][j]
    
# Command Line Arguments

if len(sys.argv) < 4:
    print("Usage: python script.py <input_file> <num_colours> <stitch_width>")
    sys.exit(0)

input_file_name = sys.argv[1]
num_colours = int(sys.argv[2])
stitch_width = int(sys.argv[3])  # number of stitches across (width)

# Prepare SVG Outputs
col_sym = SVG(False, True, True)
blw_nsy = SVG(True, True, True)
col_nsy = SVG(False, False, False)
key = SVG(False, True, True)

#Open Image
im = Image.open(input_file_name)

#Resize Image to Target Width(stitch count)
aspect_ratio = im.size[1] / im.size[0]
stitch_height = int(stitch_width * aspect_ratio)
im_resized = im.resize((stitch_width, stitch_height), Image.NEAREST)

#Quantize Image to num_colours 
dmc_image = im_resized.convert('P', palette=Image.ADAPTIVE, colors=num_colours)
x_count, y_count = dmc_image.size
svg_pattern = [[dmc_image.getpixel((x, y)) for x in range(x_count)] for y in range(y_count)]

#Map Quantized Palette to DMC Threads
palette = dmc_image.getpalette()
d = DMC()
svg_palette = [
    d.get_colour_code_corrected((palette[i*3], palette[i*3+1], palette[i*3+2]))
    for i in range(num_colours)

#Draw SVGs
svg_cell_size = 10
width = x_count * svg_cell_size
height = y_count * svg_cell_size

col_sym.prep_for_drawing(width, height)
col_sym.mid_arrows(svg_cell_size, width, height)
blw_nsy.prep_for_drawing(width, height)
blw_nsy.mid_arrows(svg_cell_size, width, height)
col_nsy.prep_for_drawing(width, height)

x = y = svg_cell_size
for row in svg_pattern:
    for colour_index in row:
        col_sym.add_rect(svg_palette, colour_index, x, y, svg_cell_size)
        blw_nsy.add_rect(svg_palette, colour_index, x, y, svg_cell_size)
        col_nsy.add_rect(svg_palette, colour_index, x, y, svg_cell_size)
        x += svg_cell_size
    y += svg_cell_size
    x = svg_cell_size

blw_nsy.major_gridlines(svg_cell_size, width, height)
col_sym.major_gridlines(svg_cell_size, width, height)

# Generate the Key Table
key_size = 40
key.prep_for_drawing(key_size * 13, key_size * len(svg_palette))
x = y = 0
for i, colour in enumerate(svg_palette):
    key.add_key_colour(x, y, key_size, i, colour)
    y += key_size

#Save SVGs
col_sym.save('col_sym.svg')
blw_nsy.save('blw_sym.svg')
col_nsy.save('col_nsy.svg')
key.save('key.svg')
