from math import sin,cos,tan,radians

def sind(deg):
    return sin(radians(deg))

def cosd(deg):
    return cos(radians(deg))

def tand(deg):
    return tan(radians(deg))
    
def tand(deg):
    return tan(radians(deg))

def rotatePoint(origin,point,angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.
    The angle should be given in degrees.
    """
    ox, oy = origin
    px, py = point

    qx = ox + cosd(angle) * (px - ox) - sind(angle) * (py - oy)
    qy = oy + sind(angle) * (px - ox) + cosd(angle) * (py - oy)
    return qx, qy

def rotatePointArray(origin,xPointArray,yPointArray,angle):
    """
    Rotate a group of points counterclockwise by a given angle around a given origin.
    The angle should be given in degrees.
    xPointArray = [x1,x2,x3,...]
    yPointArray = [y1,y2,y3,...]
    """
    xPointArrayNew = []
    yPointArrayNew = []

    for x, y in zip(xPointArray,yPointArray):
        newX, newY = rotatePoint(origin,(x,y),angle)
        xPointArrayNew.append(newX)
        yPointArrayNew.append(newY)
    return xPointArrayNew, yPointArrayNew
