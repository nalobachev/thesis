import os.path
from PIL import Image

f = r'bored-ape-kennel-club'
for file in os.listdir(f):
    f_img = f+"/"+file
    img = Image.open(f_img)
    img = img.resize((512, 512))
    img.save(f_img)
