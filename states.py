import numpy as np
import queue as qu
import random
import itertools as it
import math as m
import cv2
import copy
import useful as us
import ocr
import pandas as pd
import graph as gr

def possibleCircles(img):
    mat = []
    for c in range(0,img.shape[1]):
        column = []
        for l in range(0,img.shape[0]):
            if (img[l][c] == 255):
                column.append(l)
        mat.append((c,column))

    minDist = 20
    q = qu.PriorityQueue()
    for m in mat:
        if(len(m[1])>1):
            dist = m[1][len(m[1])-1] - (m[1][0])
            if(dist > minDist):
                for i in range(len(m[1])):
                    for j in range(i+1,len(m[1])):
                        ndist = m[1][j] - m[1][i]
                        if(ndist > minDist):
                            r = ndist // 2
                            y0 = m[0]
                            x0 = m[1][i] + r
                            circle = (x0,y0,r)
                            if(y0+r < img.shape[1]):
                                beta,pontos = reinforcementSignal(img,circle)
                                beta = 1 - beta
                                q.put((beta,circle,pontos))
    return q

def reinforcementSignal(img, circle):
    x0 = int(circle[0])
    y0 = int(circle[1])
    radius = int(circle[2])
    f = 1 - radius
    ddf_x = 1
    ddf_y = -2 * radius
    x = 0
    xx,yy = img.shape
    if(y0 + radius >= yy):
        radius = yy-y0 -1

    if(x0 + radius >= xx):
        radius = xx - x0 -1
    y = radius
    couter = 0
    beta = 0
    points = []
    if(img[x0][y0 + radius] == 255):
        beta = beta + 1
    if(img[x0][y0 - radius] == 255):
        beta = beta + 1
    if(img[x0 + radius][y0] == 255):
        beta = beta + 1
    if(img[x0 - radius][y0] == 255):
        beta = beta + 1
    cont = 4
    points.append((x0,y0+radius))
    points.append((x0,y0-radius))
    points.append((x0+radius,y0))
    points.append((x0-radius,y0))
    while x < y:
        if f >= 0:
            y -= 1
            ddf_y += 2
            f += ddf_y
        x += 1
        ddf_x += 2
        f += ddf_x
        if(img[x0 + x][y0 + y] == 255):
            beta = beta + 1
        if(img[x0 - x][y0 + y] == 255):
            beta = beta + 1
        if(img[x0 + x][y0 - y] == 255):
            beta = beta + 1
        if(img[x0 - x][y0 - y] == 255):
            beta = beta + 1
        if(img[x0 + y][y0 + x] == 255):
            beta = beta + 1
        if(img[x0 - y][y0 + x] == 255):
            beta = beta + 1
        if(img[x0 + y][y0 - x] == 255):
            beta = beta + 1
        if(img[x0 - y][y0 - x] == 255):
            beta = beta + 1
        couter = couter + 8
        points.append((x0+x,y0+y))
        points.append((x0-x,y0+y))
        points.append((x0+x,y0-y))
        points.append((x0-x,y0-y))
        points.append((x0+y,y0+x))
        points.append((x0-y,y0+x))
        points.append((x0+y,y0-x))
        points.append((x0-y,y0-x))
    beta = beta/couter
    return beta,points

def selectsTheBest(q):
    beta = 0.0
    result = []
    while(beta <= 0.5):
        g=q.get()
        beta = g[0]
        circle = g[1]
        points = g[2]
        result.append((beta, circle, True, points))
    return result

def repeatedRemoval(r):
    dist = 10
    circles = qu.PriorityQueue()
    i = 0
    k = len(r)
    while (i<k):
        circle = r[i]
        if(circle[2]):
            circles.put((circle[0],circle[1],circle[3]))
            for j in range(i+1,k):
                x0 = circle[1][0]
                y0 = circle[1][1]
                x1 = r[j][1][0]
                y1 = r[j][1][1]
                if(x0 == x1):
                    if(abs(y0-y1)<=dist):
                        cir = (x1,y1,r[j][1][2])
                        r[j] =((circle[0],cir,False))
                elif(y0 == y1):
                    if(abs(x0-x1)<=dist):
                        cir = (x1,y1,r[j][1][2])
                        r[j] =((circle[0],cir,False))
                elif(abs(x0-x1)<=dist and abs(y0-y1)<=dist):
                        cir = (x1,y1,r[j][1][2])
                        r[j] =((circle[0],cir,False))
        i = i +1
    return circles

def drawCircles(img,circles):
    allCircles = np.ones_like(img)*255
    #img1 = cv2.cvtColor(img1,cv2.COLOR_GRAY2BGR)
    q = []
    while(not circles.empty()):
        g = circles.get()
        q.append(g)
        x0 = g[1][0]
        y0 = g[1][1]
        r = g[1][2]

        allCircles = drawCircle(allCircles,x0,y0,r)
    return allCircles,q

def drawCircle(img, x0, y0, radius, colour=0):
    f = 1 - radius
    ddf_x = 1
    ddf_y = -2 * radius
    x = 0
    xx,yy = img.shape
    if(y0 + radius >= yy):
        radius = yy-y0 -1

    if(x0 + radius >= xx):
        radius = xx - x0 -1

    y = radius
    img[x0][y0 + radius] = colour
    img[x0][y0 - radius] = colour
    img[x0 + radius][y0] = colour
    img[x0 - radius][y0] = colour

    while x < y:
        if f >= 0:
            y -= 1
            ddf_y += 2
            f += ddf_y
        x += 1
        ddf_x += 2
        f += ddf_x
        img[x0 + x][y0 + y] = colour
        img[x0 - x][y0 + y] = colour
        img[x0 + x][y0 - y] = colour
        img[x0 - x][y0 - y] = colour
        img[x0 + y][y0 + x] = colour
        img[x0 - y][y0 + x] = colour
        img[x0 + y][y0 - x] = colour
        img[x0 - y][y0 - x] = colour
    return img

def deletesInnerCircles(circles):
    cir = []
    while(not circles.empty()):
        c = circles.get()
        cir.append(c)
    circles = qu.PriorityQueue()
    add = True
    for i in range(len(cir)):
        xa = cir[i][1][0]
        ya = cir[i][1][1]
        ra = cir[i][1][2]
        for j in range(len(cir)):
            xb = cir[j][1][0]
            yb = cir[j][1][1]
            rb = cir[j][1][2]
            if(i != j and ra<rb):
                d = (xb-xa)**2 + (yb-ya)**2
                d = m.sqrt(d)
                if(d<rb):
                    add=False

        if(add):
            circles.put(cir[i])
        add = True

    return circles

def acceptStates(img,circles):
    acc = []
    ix,iy = img.shape
    for n in circles:
        x0 = n[1][0]
        y0 = n[1][1]
        radius = n[1][2]
        per = int(radius*0.3) +1
        if (per < 10):
            per = 10
        radius = n[1][2] + per
        a = (x0 - radius) if(x0-radius > 0) else 0
        b = (x0 + radius) if(x0+radius < ix) else ix-1
        c = (y0 - radius) if(y0-radius > 0) else 0
        d = (y0 + radius) if(y0+radius < iy) else iy-1
        ta = abs((b-a) * (d-c))
        c_img = np.zeros(ta).reshape(((abs(b-a)),(abs(d-c))))
        c_img = img[a:b,c:d]
        n = str(x0) +str(y0)
        
        sides = []
        points=[]
        for i in range(c,y0,1):
            if(img[x0][i] == 255):
                points.append(i)
        sides.append(points)
        points=[]
        for i in range(d,y0,-1):
            if(img[x0][i] == 255):
                points.append(i)
        sides.append(points)
        points=[]
        for i in range(a,x0,1):
            if(img[i][y0] == 255):
                points.append(i)
        sides.append(points)
        points=[]
        for i in range(b,x0,-1):
            if(img[i][y0] == 255):
                points.append(i)
        sides.append(points)
        sum = 0
        for l in sides:
            bigger = []
            if (len(l) >=4):
                prev = l[0]
                counter = 0
                for j in range(1,len(l)):
                    x = abs(prev-l[j])
                    y = prev
                    prev = l[j]
                    if(x>=2 and x <= 4): # distancia entre bordas 2 a 2
                        counter = counter + 1
                        if (y > l[j]):
                            bigger.append(y)
                        else:
                            bigger.append(l[j])
                if(counter>=2):
                    s = False
                    for i in range(len(bigger)):
                        for j in range(i+1,len(bigger)):
                            if(abs(bigger[i]-bigger[j])<=per): # distancia entre todas bordas
                                s = True
                    if(s):
                        sum = sum + 1
        if(sum>=3 and sum <=5):
            name = str(x0)+str(y0)
            acc.append(name)
    return acc

def createGraph(G,circles,imgOrg,org,accept,lps,withLps):
    circles,imgOrg = newCircles(imgOrg, org, circles, accept)
    G = gr.addNodes(G,accept,circles,imgOrg)
    G, imgOrg, lps,withLps = discoverLoops(G,circles,imgOrg)
    return G, imgOrg, lps,withLps

def newCircles(imgOrg, org, circles,accept):
    newCircles = []
    cir = []
    accept = set(accept)
    imgRes = copy.deepcopy(imgOrg)
    for i in range(len(circles)):
        x0 = circles[i][1][0]
        y0 = circles[i][1][1]
        radius = circles[i][1][2]
        name = (str(x0) + str(y0))
        acc = False
        if (name in accept):
            acc = True
        nimg = np.ones_like(imgOrg)*255
        nimg = np.where(imgOrg == 0, 0, nimg)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        nimg = cv2.morphologyEx(nimg, cv2.MORPH_ERODE, kernel)

        lin = 1
        if(nimg[x0][y0] == 0):
            lin +=10
            while True:
                if(lin > radius):
                    lin -= 1
                else:
                    break
            while True:
                if(nimg[x0+lin][y0] == 255):
                    break
                else:
                    lin -= 1
        else:
            per = radius*50//100
            while True:
                lin +=1
                r = x0 + lin
                if(nimg[r][y0] == 0):
                    break
                if(r >= (x0+radius-per)):
                    lin = 0
                    break
            while True and lin >0:
                lin +=1
                r = x0 + lin
                if(nimg[r][y0] == 255):
                    break
                if(r >= (x0+radius-per)):
                    lin = 0
                    break

        point = (x0+lin,y0)
        label = 100

        nimg, counter = us.bfs4neig(nimg,point,label)
        imgcir = np.ones_like(imgOrg)*255

        img = np.ones_like(imgOrg)*0
        img = np.where(nimg==label,255,img)
        minX = np.min(np.where(nimg == label)[0])
        maxX = np.max(np.where(nimg == label)[0])
        minY = np.min(np.where(nimg == label)[1])
        maxY = np.max(np.where(nimg == label)[1])
        radX = (maxX - minX) // 2
        radY = (maxY - minY) // 2
        medX = radX + minX
        medY = radY + minY
        if (radX > radY):
            rad = radX
        else:
            rad = radY
        orgAr = radius**2 * 3.14
        newAr = rad**2 * 3.14

        imgRealSize = np.ones_like(imgOrg)*255

        imgRealSize = drawCircle(imgRealSize,medX,medY,rad)
        imgRealSize, counter = us.bfs4neig(imgRealSize,(medX,medY),label)
        sizeEll = us.sizeEllipse(newAr)

        sizeImg = imgOrg.shape[0]* imgOrg.shape[1]

        loop = False
        if (sizeImg < newAr):
            loop = True
        if (not loop):
            imgcir = np.where(nimg == label, 0, imgcir)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(sizeEll,sizeEll))
            imgcir = cv2.morphologyEx(imgcir, cv2.MORPH_OPEN, kernel)

            imglabel = np.ones_like(imgOrg)*255
            imglabel = np.where(imgcir==0,org,imglabel)
            imglabel = np.where(imglabel >= 245, 255, imglabel)
            imglabel = cv2.threshold(imglabel,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
            text = ocr.labelToText(imglabel)

            sizeEdge,acc = discoverEdge(imgOrg,acc,minX,maxX,minY,maxY,medX,medY)

            rad = (sizeEdge//3) + rad
            imgcir = cv2.threshold(imgcir,0,255,cv2.THRESH_BINARY_INV)[1]
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(sizeEdge,sizeEdge))
            imgcir = cv2.morphologyEx(imgcir, cv2.MORPH_DILATE, kernel)
            imgRes = imgRes + imgcir

            imgcir = cv2.Canny(imgcir,100,200)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(sizeEdge//3,sizeEdge//3))
            imgcir = cv2.morphologyEx(imgcir, cv2.MORPH_DILATE, kernel)
            label = 255
            minX = np.min(np.where(imgcir == label)[0])
            maxX = np.max(np.where(imgcir == label)[0])
            minY = np.min(np.where(imgcir == label)[1])
            maxY = np.max(np.where(imgcir == label)[1])
            point = (minX,minY)

            cir = set(cir)
            if(str(medX)+str(medY) not in cir):
                newCircles.append((circles[0],(medX,medY,rad),loop,acc,text,point,imgcir[minX:maxX,minY:maxY]))
            cir = list(cir)
            cir.append(str(medX)+str(medY))
            name = 'img'+str(x0)+str(y0)

        else:
            newCircles.append((circles[0],(x0,y0,radius),loop,acc,'',(0,0),[]))

    return newCircles,imgRes

def discoverEdge(img,acc,minX,maxX,minY,maxY,medX,medY):
    x,y = img.shape
    cont = 0
    total = 1
    contMinX = 0
    contMaxX = 0
    contMinY = 0
    contMaxY = 0
    radius = max([maxX-minX,maxY-minY]) //2
    iMinX = 0 if (minX - 2 < 0) else minX - 2
    iMaxX = x - 1 if (maxX + 2 > x - 1) else maxX + 2
    iMinY = 0 if (minY - 2 < 0) else minY - 2
    iMaxY = y - 1 if (maxY + 2 > y - 1) else maxY + 2

    if acc:
        go = True
        while go:
            go = False
            if(img[iMinX][medY] == 0 and iMinX != 0):
                contMinX = contMinX + 1
                go = True
                iMinX = 0 if iMinX - 1 < 0 else iMinX - 1
            if(img[iMaxX][medY] == 0 and iMaxX != x - 1):
                contMaxX = contMaxX + 1
                go = True
                iMaxX = x - 1 if iMaxX + 1 > x - 1 else iMaxX + 1
            if(img[medX][iMinY] == 0 and iMinY != 0):
                contMinY = contMinY + 1
                go = True
                iMinY = 0 if iMinY - 1 < 0 else iMinY - 1
            if(img[medX][iMaxY] == 0 and iMaxY != y - 1):
                contMaxY = contMaxY + 1
                go = True
                iMaxY = y - 1 if iMaxY + 1 > y - 1 else iMaxY + 1

        conts = pd.Series([contMinX,contMaxX,contMinY,contMaxY])

        total = int(conts.median()) + 2
        acc = checkFinal(contMinX,contMaxX,contMinY,contMaxY, int(conts.median()),radius)

        if(acc):
            contMinX = 0
            contMaxX = 0
            contMinY = 0
            contMaxY = 0

            go = True
            while go:
                go = False
                if(img[iMinX][medY] == 255 and iMinX != 0):
                    contMinX = contMinX + 1
                    go = True
                    iMinX = 0 if iMinX - 1 < 0 else iMinX - 1
                if(img[iMaxX][medY] == 255 and iMaxX != x - 1):
                    contMaxX = contMaxX + 1
                    go = True
                    iMaxX = x - 1 if iMaxX + 1 > x - 1 else iMaxX + 1
                if(img[medX][iMinY] == 255 and iMinY != 0):
                    contMinY = contMinY + 1
                    go = True
                    iMinY = 0 if iMinY - 1 < 0 else iMinY - 1
                if(img[medX][iMaxY] == 255 and iMaxY != y - 1):
                    contMaxY = contMaxY + 1
                    go = True
                    iMaxY = y - 1 if iMaxY + 1 > y - 1 else iMaxY + 1
            conts = pd.Series([contMinX,contMaxX,contMinY,contMaxY])
            acc = checkFinal(contMinX,contMaxX,contMinY,contMaxY, int(conts.median()),radius)
            if(acc):
                total += max(conts)
            else:
                if(int(conts.median()) < 3*radius):
                    total +=int(conts.median())
    else:

        go = True
        while go:
            go = False
            if(img[iMinX][medY] == 0 and iMinX != 0):
                contMinX = contMinX + 1
                go = True
                iMinX = 0 if iMinX - 1 < 0 else iMinX - 1
            if(img[iMaxX][medY] == 0 and iMaxX != x - 1):
                contMaxX = contMaxX + 1
                go = True
                iMaxX = x - 1 if iMaxX + 1 > x - 1 else iMaxX + 1
            if(img[medX][iMinY] == 0 and iMinY != 0):
                contMinY = contMinY + 1
                go = True
                iMinY = 0 if iMinY - 1 < 0 else iMinY - 1
            if(img[medX][iMaxY] == 0 and iMaxY != y - 1):
                contMaxY = contMaxY + 1
                go = True
                iMaxY = y - 1 if iMaxY + 1 > y - 1 else iMaxY + 1


        conts = pd.Series([contMinX,contMaxX,contMinY,contMaxY])
        mode = conts.mode()
        if(len(mode) > 1):
            if(max(mode) < (radius//2)):
                mode = max(mode)
            else:
                mode = min(mode)
        else:
            mode = mode.item() + 1 - 1
            if(mode > (radius*3)):
                mode = min(conts)
        total = mode + 2

    return ((total)*3), acc

def checkFinal(a,b,c,d,m,radius):
    m = m + 10
    if(a > m):
        return False
    if(b > m):
        return False
    if(c > m):
        return False
    if(d > m):
        return False
    if(m > radius*3):
        return False
    return True

def discoverLoops(G,circles,imgOrg):
    lps = []
    withLps = []
    for i in range(len(circles)):
        cirA = circles[i][1]
        x0A = cirA[0]
        y0A = cirA[1]
        rA = cirA[2]
        queA = []
        queA.append((x0A,(y0A+rA)))
        queA.append((x0A,(y0A-rA)))
        queA.append(((x0A+rA),y0A))
        queA.append(((x0A-rA),y0A))
        for j in range(i+1,(len(circles))):
            cirB = circles[j][1]
            x0B = cirB[0]
            y0B = cirB[1]
            rB = cirB[2]
            loopB = circles[j][2]
            queB = []
            queB.append((x0B,(y0B+rB)))
            queB.append((x0B,(y0B-rB)))
            queB.append(((x0B+rB),y0B))
            queB.append(((x0B-rB),y0B))
            loop = False
            if(x0B > x0A-rA) and (x0B < x0A+rA) and (y0B+rB > y0A-rA) and (y0B+rB < y0A + rA):
                loop = True
            if(x0B > x0A-rA) and (x0B < x0A+rA) and (y0B-rB > y0A-rA) and (y0B-rB < y0A + rA):
                loop = True
            if(x0B+rB > x0A-rA) and (x0B+rB < x0A+rA) and (y0B > y0A-rA) and (y0B < y0A + rA):
                loop = True
            if(x0B-rB > x0A-rA) and (x0B-rB < x0A+rA) and (y0B > y0A-rA) and (y0B < y0A + rA):
                loop = True

            if(x0A > x0B-rB) and (x0A < x0B+rB) and (y0A+rA > y0B-rB) and (y0A+rA < y0B + rB):
                loop = True
            if(x0A > x0B-rB) and (x0A < x0B+rB) and (y0A-rA > y0B-rB) and (y0A-rA < y0B + rB):
                loop = True
            if(x0A+rA > x0B-rB) and (x0A+rA < x0B+rB) and (y0A > y0B-rB) and (y0A < y0B + rB):
                loop = True
            if(x0A-rA > x0B-rB) and (x0A-rA < x0B+rB) and (y0A > y0B-rB) and (y0A < y0B + rB):
                loop = True

            #quando o circulo encontrado para o loop esta muito próximo, mas nao tem interseção com o circulo do estado
            if(not loop):
                for k in range(0,4):
                    for l in range(0,4):
                        d = np.sqrt(pow(queA[k][0]-queB[l][0],2) + pow(queA[k][1]-queB[l][1],2))
                        if(d < 10):
                            loop = True

            nCirA = str(x0A)+str(y0A)
            nCirB = str(x0B)+str(y0B)
            if (nCirA in lps):
                loop = False
            if (loop):
                pointA = 0
                pointB = 0
                num = []
                num.append(-1)
                if (circles[i][2]):
                    if(G.has_edge(nCirB,nCirB)):
                        num = gr.getEdgeNum(G,nCirB,nCirB)
                        num.append(-1)
                        gr.setEdgeNum(G,nCirB,nCirB,num)
                        poi = gr.getEdgePoint(G,nCirB,nCirB)
                        poi.append(circles[j][5])
                        gr.setEdgePoint(G,nCirB,nCirB, poi)
                        ims = gr.getEdgeImg(G,nCirB,nCirB)
                        ims.append(circles[j][6])
                        gr.setEdgeImg(G,nCirB,nCirB,ims)
                    else:
                        gr.addEdge(G,nCirB,nCirB,'',num,[],[])
                elif(circles[j][2]):
                    if(G.has_edge(nCirA,nCirA)):
                        num = gr.getEdgeNum(G,nCirA,nCirA)
                        num.append(-1)
                        gr.setEdgeNum(G,nCirA,nCirA,num)
                        poi = gr.getEdgePoint(G,nCirA,nCirA)
                        poi.append(circles[j][5])
                        gr.setEdgePoint(G,nCirA,nCirA, poi)
                        ims = gr.getEdgeImg(G,nCirA,nCirA)
                        ims.append(circles[j][6])
                        gr.setEdgeImg(G,nCirA,nCirA,ims)
                    else:
                        gr.addEdge(G,nCirA,nCirA,'',num,[],[])
                else:
                    if (circles[i][3]):
                        pointA += 2
                    if (circles[j][3]):
                        pointB += 2
                    if (circles[i][4] == '' and circles[j][4] != ''):
                        pointB += 1
                    if (circles[i][4] != '' and circles[j][4] == ''):
                        pointA += 1
                    if (nCirA in withLps):
                        pointA += 1
                    if (nCirB in withLps):
                        pointB += 1
                    if (pointA >= pointB):
                        G.remove_node(nCirB)
                        poi = []
                        poi.append(circles[j][5])
                        img = []
                        img.append(circles[j][6])
                        num = []
                        num.append(-1)
                        if(G.has_edge(nCirA,nCirA)):
                            num = gr.getEdgeNum(G,nCirA,nCirA)
                            num.append(-1)
                            gr.setEdgeNum(G,nCirA,nCirA,num)
                            poi = gr.getEdgePoint(G,nCirA,nCirA)
                            poi.append(circles[j][5])
                            gr.setEdgePoint(G,nCirA,nCirA, poi)
                            ims = gr.getEdgeImg(G,nCirA,nCirA)
                            ims.append(circles[j][6])
                            gr.setEdgeImg(G,nCirA,nCirA,ims)
                        else:
                            gr.addEdge(G,nCirA,nCirA,'',num,poi,img)
                            gr.addNodeLoop(G,nCirA,cirB)

                        lps.append(nCirB)
                        if(nCirA not in withLps):
                            withLps.append(nCirA)
                    else:
                        G.remove_node(nCirA)
                        poi = []
                        poi.append(circles[i][5])
                        img = []
                        img.append(circles[i][6])
                        num = []
                        num.append(-1)

                        if(G.has_edge(nCirB,nCirB)):
                            num = gr.getEdgeNum(G,nCirB,nCirB)
                            num.append(-1)
                            gr.setEdgeNum(G,nCirB,nCirB,num)
                            poi = gr.getEdgePoint(G,nCirB,nCirB)
                            poi.append(circles[i][5])
                            gr.setEdgePoint(G,nCirB,nCirB, poi)
                            ims = gr.getEdgeImg(G,nCirB,nCirB)
                            ims.append(circles[i][6])
                            gr.setEdgeImg(G,nCirB,nCirB,ims)
                        else:
                            gr.addEdge(G,nCirB,nCirB,'',num,poi,img)
                            gr.addNodeLoop(G,nCirB,cirA)

                        lps.append(nCirA)
                        if(nCirB not in withLps):
                            withLps.append(nCirB)

    return G, imgOrg, lps, withLps
