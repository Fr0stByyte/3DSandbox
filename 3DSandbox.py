import math
import time

app.raySpeed = 8
app.res = 6
app.mode = 1
app.buildingPoints = []
app.tempPoints = Group()
app.isInMenu = True
ground = Rect(0, app.centerY, 400, 200, fill='green')
app.stuff = Group()
sky = Rect(0, 0, 400, 200, fill='skyBlue')
text = Label("0", 25, 25, size=12, fill='black')

app.screen = Group(
    Rect(0, 0, 400, 400, fill=gradient("white", "black", start='bottom')),
    Label("Welcome to 3D Sandbox!", app.centerX, 50, size=18, fill='white', bold=True),
    Label("Press 'return' to enter the sandbox or come back to this menu.", app.centerX, app.centerY, fill='white'),
    Label("In the sandbox, use the arrow keys to turn and move.", app.centerX, app.centerY + 12, fill='white'),
    Label("In the sandbox, press 'space' to switch between 2D and 3D veiws.", app.centerX, app.centerY + 24, fill='white'),
    Label("When in 2D veiw, click the mouse to create points,", app.centerX, app.centerY + 36, fill='white'),
    Label("By pressing ']' the points will become the vertices of a new shape", app.centerX, app.centerY + 48, fill='white'),
    Label("Press 'c' to clear the map of all shapes.", app.centerX, app.centerY + 60, fill='white')
    )
    
app.map = Group(
    Rect(0, 0, 400, 10),
    Rect(0, 0, 10, 400),
    Rect(0, 390, 400, 10),
    Rect(390, 0, 10, 400),
    Rect(175, 0, 50, 150),
    Rect(175, 250, 50, 150),
    Circle(75, 75, 35),
    Rect(60, 300, 50, 50),
    Star(325, 75, 35, 5)
    )


ground.toBack()
sky.toBack()
app.map.toBack()

#creates an empty map for use during clearing
def createEmptyMap():
    emptyMap = Group(
        Rect(0, 0, 400, 10),
        Rect(0, 0, 10, 400),
        Rect(0, 390, 400, 10),
        Rect(390, 0, 10, 400)
    )
    return emptyMap
    pass
    
#moves the player by its xVelocity and yVelocity found using trigonometry
#checks collisions
def tickPlayer(player, dt):
    player.rotateAngle += player.turnVel * dt
    
    player.velX = math.cos(math.radians(player.rotateAngle - 90)) * player.magnitude * dt
    player.velY = math.sin(math.radians(player.rotateAngle - 90)) * player.magnitude * dt
    
    player.centerX += player.velX * dt
    if player.hitsShape(app.map):
        player.centerX -= player.velX * dt
        
    player.centerY += player.velY * dt
    if player.hitsShape(app.map):
        player.centerY -= player.velY * dt
    pass

#creates a player at a given position
def createPlayer(xPos, yPos):
    player = Group(
                Circle(xPos, yPos, 5, fill='black'),
                Circle(xPos, yPos - 5, 2.5, fill='cyan')
                )
    player.velX = 0
    player.velY = 0
    player.turnVel = 0
    player.magnitude = 0
    player.fov = 60
    player.toBack()
    player.tick = tickPlayer
    return player
    pass
    
app.player = createPlayer(300, 200)

#casts ray in a given direction based starting at a certain point
def castRay(xPos, yPos, direction):
    isVertical = False
    rayHit = False
    isRayOut = False
    ray = Circle(xPos, yPos, (1 / 10000000000), fill='yellow')
    while  not rayHit:
        if ray.hitsShape(app.map):
            rayHit = True
            shape = app.map.hitTest(ray.centerX, ray.centerY)
            rDiff = abs(shape.right - ray.centerX)
            lDiff = abs(shape.left - ray.centerX)
            if rDiff < 7 or lDiff < 7:
                isVertical = True
            while not isRayOut:
                if ray.hitsShape(app.map):
                    ray.centerX -= math.cos(math.radians(direction - 90)) * 1
                    ray.centerY -= math.sin(math.radians(direction - 90)) * 1
                else:
                    isRayOut = True
                    ray.visible = False
        else:
            ray.centerX += math.cos(math.radians(direction - 90)) * app.raySpeed
            ray.centerY += math.sin(math.radians(direction - 90)) * app.raySpeed
    return ([[ray.centerX, ray.centerY], isVertical])
    pass

#renders a frame of the 3D view
#takes in a resolution, which determines spacing of lines
#lower res means more lines that are closer together in the fov
def renderStep(resolution):
    app.stuff.clear()
    direction = app.player.rotateAngle - (app.player.fov / 2)
    lines = int(400 / resolution)
    rectXSize = 400 / lines
    drawPos = 0
    
    for i in range(lines):
        data = castRay(app.player.centerX, app.player.centerY, direction)
        point = data[0]
        isVertical = data[1]
        dist = distance(app.player.centerX, app.player.centerY, point[0], point[1]) * math.cos(math.radians(app.player.rotateAngle - direction))
        rectSizeY = 50000 / dist
        brightness = 255 / (dist / 50)
        if brightness > 255:
            brightness = 255
        if isVertical:
            brightness -= brightness/3
        rect = Rect(drawPos, 0, rectXSize, rectSizeY, fill=rgb(0, 0, brightness))
        rect.centerY = app.centerY
        app.stuff.add(rect)
        rect.toFront()
        drawPos += rectXSize
        direction += app.player.fov / lines
    text.toFront()
    pass

#renders a 2D Frame of the map with visible rays
#resolution functions similar to renderStep, but rays are closer instead
def renderTrace(resolution):
    app.stuff.clear()
    direction = app.player.rotateAngle - (app.player.fov / 2)
    lines = int(400 / resolution)
    rectXSize = 400 / lines
    drawPos = 0

    for i in range(lines):
        data = castRay(app.player.centerX, app.player.centerY, direction)
        point = data[0]
        isVertical = data[1]
        color = "red"
        if isVertical == True:
            color = 'darkRed'
        if isVertical == False:
            color = 'red'
        circ = Line(app.player.centerX, app.player.centerY, point[0], point[1], fill=color)
        app.stuff.add(circ)
        
        direction += app.player.fov / lines
    pass

#swicthes between 2D and 3D view
def switchMode(mode):
    if mode == 0:
        app.mode = 0
        app.stuff.clear()
        app.map.toFront()
        ground.visible = False
        sky.visible = False
    if mode == 1:
        app.stuff.clear()
        ground.visible = True
        sky.visible = True
        app.map.toBack()
        app.mode = 1
    pass
#movment keys
#can be pressed at the same time
def onKeyHold(keys):
    for key in keys:
        if key == 'w' or key == 'up':
            app.player.magnitude = 200
        if key == 's' or key == 'down':
            app.player.magnitude = -200
        if key == 'right':
            app.player.turnVel = 35
        if key == "left":
            app.player.turnVel = -35
    pass

#halts player movement once keys are let go
def onKeyRelease(key):
    if key == 'w' or key == 'up':
        app.player.magnitude = 0
    if key == 'right' or key == 'left':
        app.player.turnVel = 0
    if key == 's' or key == 'down':
        app.player.magnitude = 0
    pass

#game loop
#tries to be called once every 30 seconds
def onStep():
    if app.mode == 1:
        oldTime = time.time()
        renderStep(app.res)
        currentTime = time.time()
        dt = currentTime - oldTime
        app.player.tick(app.player, dt)
        text.value = int(1/dt)
    else:
        oldTime = time.time()
        renderTrace(app.res)
        currentTime = time.time()
        dt = currentTime - oldTime
        app.player.tick(app.player, dt)
        text.value = int(1/dt)
    pass

#all keybinds
def onKeyPress(key):
    if app.isInMenu:
        if key == 'enter':
            app.isInMenu = False
            app.screen.visible = False
    else:
        if key == 'space':
            if app.mode == 1:
                switchMode(0)
            else:
                switchMode(1)
        if key == ']':
            if app.mode == 0:
                Shape = Polygon(fill='gray')
                for point in app.buildingPoints:
                    Shape.addPoint(point[0], point[1])
                app.map.add(Shape)
                app.buildingPoints.clear()
                app.tempPoints.clear()
                app.lastShape = Shape
        if key == 'enter':
            app.isInMenu = True
            app.screen.visible = True
        if key == 'c':
            emptyMap = createEmptyMap()
            app.map.clear()
            app.map = emptyMap
            app.map.toBack()
    pass

#creates the points to be used when creating a shape
def mousePressed(x, y):
    if app.mode == 0:
        app.buildingPoints.append([x, y])
        tempPoint = Circle(x, y, 3, fill='green')
        app.tempPoints.add(tempPoint)
    pass

def onMousePress(x, y):
    mousePressed(x,y)
    pass
