# quick_extract.py
import os

folder = r"/Users/dipak/Downloads/archive (10)/images"
classes = sorted([d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))])

# Print
for i, c in enumerate(classes):
    print(f"{i}: {c}")

# Save
with open('classes.txt', 'w') as f:
    f.write('\n'.join(classes))
    
print(f"\n✅ Saved {len(classes)} classes to 'classes.txt'")