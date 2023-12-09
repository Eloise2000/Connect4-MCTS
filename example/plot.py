import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# Function to add images to the plot
def add_image(ax, path, position, zoom=10.0):
    image = plt.imread(path)
    imagebox = OffsetImage(image, zoom=zoom, resample=True)
    ab = AnnotationBbox(imagebox, position, frameon=False, pad=0)
    ax.add_artist(ab)

# Create a subplot with 2 rows and 4 columns (assuming you have 8 images)
fig, ax = plt.subplots(2, 4, figsize=(12, 6))

# Iterate through the image files and add them to the plot
for i in range(1, 9):
    image_path = f"{i}.png"
    row, col = divmod(i - 1, 4)
    add_image(ax[row, col], image_path, (0.5, 0.5), zoom=0.1)

    # Add numbering
    ax[row, col].text(0.5, -0.1, f"Move {i}", ha='center', va='center', transform=ax[row, col].transAxes, fontsize=10)

# Hide axes and show the plot
for a in ax.flatten():
    a.axis('off')

plt.tight_layout()
plt.show()