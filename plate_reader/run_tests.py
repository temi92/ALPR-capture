import requests
import base64
import json
import argparse
from collections import namedtuple
from pathlib import Path
import glob
import os
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--image", required=True, help="path to image")
# args = vars(ap.parse_args())

# Sample image file is available at http://plates.openalpr.com/ea7the.jpg
# IMAGE_PATH = args["image"]
SECRET_KEY = 'sk_DEMODEMODEMODEMODEMODEMO'
url = 'https://api.openalpr.com/v2/recognize_bytes?recognize_vehicle=1&country=us&secret_key=%s' % SECRET_KEY

confidences = []
plateNumbers = []

vehicleData = namedtuple("Vehicle", "plateNumber confidence")


def postImage(image_path):
    with open(image_path, 'rb') as image_file:
        img_base64 = base64.b64encode(image_file.read())
        r = requests.post(url, data=img_base64)
    return json.loads(json.dumps(r.json()))


def getVehicleData(jsonData):
    """
    Extract plate number and the hightest confidence interval from json output
    """
    for candidate in jsonData:
        confidences.append(candidate["confidence"])
    for candidate in jsonData:
        plateNumbers.append(candidate["plate"])

    confidence = max(confidences)
    # extract plate number with highest confidence
    plateNumber = plateNumbers[confidences.index(max(confidences))]
    vehicleData.plateNumber = plateNumber
    vehicleData.confidence = confidence


def show_image_and_regions(image, regions, prediction):
    img = Image.open(image)
    # For now it appears that we always get 4 x and 4 y values in a list of dicts
    xs = [r['x'] for r in regions]
    ys = [r['y'] for r in regions]

    xs = np.array(xs)
    ys = np.array(ys)

    f, ax = plt.subplots()
    ax.imshow(img)
    ax.plot(xs, ys, '-*r')

    plt.title("Plate number is {} and confidence is {}".format(prediction.plateNumber, prediction.confidence))

    plt.show()




def main():
    # Use pathlib to get the os agnostic path to the images
    path_to_images = Path('/home/parallels/Documents/Python/ALPR-capture/data_sets/dataset4_done')
    # Build a list of images in the directory
    imagepath = [path_to_images/f for f in path_to_images.iterdir()]
    # Sort them by time modified, so that we can find easily when looking at the file explorer
    imagepath.sort(key=lambda x: os.path.getmtime(x))

    filename = str(imagepath[3])
    try:
        jsonData = postImage(filename)
        # We want to get these coordinates to see what they mean on the image
        coordinates = jsonData['results'][0]['coordinates']
        candidates = jsonData["results"][0]["candidates"]
        getVehicleData(candidates)
        show_image_and_regions(filename, coordinates, vehicleData)
        # print("[INFO] License plate - {} and confidence  - {}".format(vehicleData.plateNumber, vehicleData.confidence))
    except IndexError:
        print("[INFO] cannot detect car plates")


if __name__ == '__main__':
    main()