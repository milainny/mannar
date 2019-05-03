import cv2
import copy
import useful as us
import states as st
import time
import networkx as nx
import graph as gr
import transactions as tr
import mannaHap as mh
import csvFile as cf
import jflapFile as jf
import numpy as np

def main(path):
    img = cv2.imread(path,0)
    img = us.resizeImg(img)
    imgOrg = copy.deepcopy(img)
    org = copy.deepcopy(img)
    img = cv2.Canny(img,100,200)

    q = st.possibleCircles(img)
    r = st.selectsTheBest(q)

    circles = st.repeatedRemoval(r)
    circles = st.deletesInnerCircles(circles)
    img1,circles = st.drawCircles(img,circles)
    accept = st.acceptStates(img,circles)

    G=nx.DiGraph()
    lps = []
    withLps = []
    imgOrg = cv2.threshold(imgOrg,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]

    G, img, lps, withlps = st.createGraph(G,circles,imgOrg,org,accept,lps,withLps)

    img, label = us.findObjects(img)
    objects = tr.mapping(G,img,label)
    img = tr.discoverArrows(G,img,label,objects,lps,withLps)

    #gr.printTest(G,accept)
    #gr.printGraph(G)
    mh.createJson(G,org)
    cf.createCsv(G)
    jf.createJFlap(G)

    return "0"
