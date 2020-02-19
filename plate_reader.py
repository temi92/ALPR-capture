import requests
import base64
import json
import argparse
import cv2
import os
import progressbar
from collections import namedtuple
from utils import generateImageList, drawBoundingBox, create_directory
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True, help="directory to input images")
ap.add_argument("-o", "--output", required=True, help="directory to results")

args = vars(ap.parse_args())

# Sample image file is available at http://plates.openalpr.com/ea7the.jpg
INPUT_PATH = args["input"]
OUTPUT_PATH = os.path.join(os.getcwd(), args["output"])


SUCCESS_IMAGES = os.path.join(OUTPUT_PATH, "success")
FAILURE_ROI = os.path.join(OUTPUT_PATH, "failure_roi")
MISLABELLED = os.path.join(OUTPUT_PATH, "mislabelled")

create_directory(SUCCESS_IMAGES)
create_directory(FAILURE_ROI)
create_directory(MISLABELLED)


SECRET_KEY = 'sk_DEMODEMODEMODEMODEMODEMO'
url = 'https://api.openalpr.com/v2/recognize_bytes?recognize_vehicle=1&country=us&secret_key=%s' % (
    SECRET_KEY)


vehicleData = namedtuple("Vehicle", "plateNumber confidence coordinates")

#stats on number of images that passed, failed or are mislabelled.
successImages = 0 
failedImages = 0 #cannot detect license plate region
mislabelledImages = 0 #detected license plate but region failed to get vehicle number identification correct
totalImages = 0


def postImage(image_path):
    with open(image_path, 'rb') as image_file:
        img_base64 = base64.b64encode(image_file.read())
        r = requests.post(url, data=img_base64)
    return json.loads(json.dumps(r.json()))


def getVehicleData(jsonData):
    """
    extract plate number and the hightest confidence interval and coordinates from json output
    """
    confidences = []
    plateNumbers = []


	#ensure list is not empty
    if jsonData["results"]:
        candidates = jsonData["results"][0]["candidates"]

        coordinates = jsonData["results"][0]["coordinates"]
        for candidate in candidates:
            confidences.append(candidate["confidence"])
        for candidate in candidates:
            plateNumbers.append(candidate["plate"])

        confidence = max(confidences)
        # extract plate number with highest confidence
        plateNumber = plateNumbers[confidences.index(max(confidences))]
        vehicleData.plateNumber = plateNumber
        vehicleData.confidence = confidence
        vehicleData.coordinates = coordinates
        return True
    else:
        return False


if __name__ == "__main__":
	images = list(generateImageList(INPUT_PATH))

	with progressbar.ProgressBar(max_value=len(images)) as bar:

		for i in range(len(images)):
			#extract filename
			fileName = os.path.split(images[i])[1]
			#file name is appended with jpg or png we need to remove that ..
			fileName = fileName.split(".")[0]
			img = cv2.imread(images[i])
			jsonData = postImage(images[i])

			#ignore images with 2 or more car plate regions..
			if len(jsonData["results"]) >= 2:
				print ("skipped {} ..has 2 or more car regions in it".format(images[i]))
				continue

			if getVehicleData(jsonData):
				#print ("[INFO] License plate - {} and confidence  - {}".format(vehicleData.plateNumber, vehicleData.confidence))
				img = drawBoundingBox(img, vehicleData.coordinates)

				#save images that have correct localisation and plate number in this directory.
				if vehicleData.plateNumber == fileName:
					successImages+=1
					cv2.imwrite("{}/{}.jpg".format(SUCCESS_IMAGES,fileName), img)
				else:
					mislabelledImages+=1
					cv2.imwrite("{}/{}.jpg".format(MISLABELLED,vehicleData.plateNumber), img)
			else:
				failedImages+=1
				cv2.imwrite("{}/{}_FAILED.jpg".format(FAILURE_ROI,fileName), img)

			totalImages+=1

			bar.update(i)

	print ("STATS REPORT #########")
	print ("Total Number of images {}".format(totalImages))
	print ("Number of images passed {}".format(successImages))
	print ("Number of images failed {}".format(failedImages))
	print ("Number of images mislabelled {}".format(mislabelledImages))
	

