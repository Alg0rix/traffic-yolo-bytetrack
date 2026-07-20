import cv2
import numpy as np
from supervision.detection.tools.polygon_zone import PolygonZone


def coordinate_extractor(coordinate_data):
    # Extracting the coordinates from the string
    coordinates = []
    parts = coordinate_data.split("L")
    for part in parts:
        if part.startswith("M"):
            part = part[1:]
        part = part.rstrip("Z")  # Remove 'Z' character
        coordinates.append(tuple(map(float, part.split(","))))

    # Create an image to draw the polygon on

    # Convert coordinates to integers
    coordinates = np.array(coordinates, dtype=np.int32)

    return coordinates
