import os
import cv2
def generateImageList(path):
    image_types  = (".jpg", ".png")
    for rootDir, dirNames, filenames in os.walk(path):
        for filename in filenames:
            ext = filename[filename.rfind("."):].lower()
            if ext.endswith(image_types):
                image_path = os.path.join(rootDir, filename)
                yield image_path


def create_directory(dirName):
	if not os.path.exists(dirName):
		os.makedirs(dirName)

def drawBoundingBox(img, regions):
	topLeft = []
	bottomRight =[]
	for i, v in enumerate(sorted(regions[0].items())):
		topLeft.append(sorted(regions[0].items())[i][1])
			
	for i, v in enumerate(sorted(regions[2].items())):
		bottomRight.append(sorted(regions[2].items())[i][1])
	
	# Blue color in BGR 
	color = (255, 0, 0) 
  
	# Line thickness of 2 px 
	thickness = 2
	img = cv2.rectangle(img, tuple(topLeft), tuple(bottomRight), color, thickness) 
	return img
