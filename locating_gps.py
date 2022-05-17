from dronekit import *
from pymavlink import mavutil
from math import *
from config import Settings

"GPS"


def gpsDistance(lat):
  # Returns approximate distance in meters of 1 degree of latitude and longitude at certain latitude, correct to a few centimetres, using WGS84 spheroid model
  # Also known as length of a degree
  latLength = 111132.92 - 559.82 * cos(radians(lat)) + 1.175 * cos(4 * radians(lat)) - 0.0023 * cos(6 * radians(lat))
  longLength = 111412.84 * cos(radians(lat)) - 93.5 * cos(3 * radians(lat)) + 0.118 * cos(5 * radians(lat))

  return [latLength, longLength]


def GPS(targetPos, heading, lat, long, alt, img_dimensions):
  # Gets gps coordinates of target
  # Takes a targetPos array of the centre of the target's position in frame [y,x]
  # takes heading and 3d position of plane at time of image capture
  # outputs array with [lat, lon] of target

  # get image dimensions and centre of image for aircraft position
  imgDimensions = [img_dimensions[1], img_dimensions[0]]
  imgCentre = [imgDimensions[0] / 2, imgDimensions[1] / 2]

  # Create array for position of plane in 3D space, [lat, long, altitude]
  plane3DPos = [lat, long, alt]

  #Get difference between image centre and target image y,x axis
  targetFromPlane = []
  for i in range(2):
    targetFromPlane.append(abs(targetPos[i] - imgCentre[i]))

    # get (b) 'bearing' of target relative to plane's heading vector
    if targetPos[0] > imgCentre[0]:
      if targetPos[1] > imgCentre[1]:
        b = degrees(atan(targetFromPlane[0] / targetFromPlane[1])) + 90
      elif targetPos[1] < imgCentre[1]:
        b = degrees(atan(targetFromPlane[1] / targetFromPlane[0])) + 180
    if targetPos[0] < imgCentre[0]:
      if targetPos[1] > imgCentre[1]:
        b = degrees(atan(targetFromPlane[1] / targetFromPlane[0]))
      elif targetPos[1] < imgCentre[1]:
        b = degrees(atan(targetFromPlane[0] / targetFromPlane[1])) + 270

    # Get bearing of target from aircraft (relative to North)
    if b < 360 - heading:
      targetBearing = b + heading
    elif b > 360 - heading:
      targetBearing = (b + heading - 360) / 2

    # conversion between pixels and actual distance in meters, based on height and lens
    # meters in 1 pixel in image at altitude during image capture
    pixToMeters = (alt * cos(radians(Settings.camera_angle/2)) * 2) / (sqrt(imgDimensions[0] ** 2 + imgDimensions[1] ** 2))

    # Get distance of target from aircraft in meters, in y,x frame components
    distanceComp = []
    for i in range(2):
      distanceComp.append(targetFromPlane[i] * pixToMeters)
    distanceFromTarget = sqrt(distanceComp[1] ** 2 + distanceComp[0] ** 2)

    # Get components of distance to target in m in Lat and Long axis
    alignedDist = [distanceFromTarget * cos(radians(targetBearing)), distanceFromTarget * sin(radians(targetBearing))]

    # Get distance in meters of 1 degree of lat and long at image capture altitude
    gpsDist = gpsDistance(plane3DPos[0])

    # Get distance between target and rover in degrees latitude and longitude (conversion)
    gpsTargetOffset = []
    for i in range(2):
      gpsTargetOffset.append(alignedDist[i] / gpsDist[i])

    # Get gps coords of target
    targetCoords = []
    for i in range(2):
      targetCoords.append(plane3DPos[i] + gpsTargetOffset[i])

    return targetCoords
