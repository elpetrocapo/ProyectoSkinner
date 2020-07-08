import cv2
import numpy as np
from PIL import Image
def find_histogram(clt):
    """
    create a histogram with k clusters
    :param: clt
    :return:hist
    """
    numLabels = np.arange(0, len(np.unique(clt.labels_)) + 1)
    (hist, _) = np.histogram(clt.labels_, bins=numLabels)

    hist = hist.astype("float")
    hist /= hist.sum()

    return hist

def plot_colors2(hist, centroids):
    bar = np.zeros((50, 300, 3), dtype="uint8")
    startX = 0

    for (percent, color) in zip(hist, centroids):
        # plot the relative percentage of each cluster
        endX = startX + (percent * 300)
        cv2.rectangle(bar, (int(startX), 0), (int(endX), 50),
                      color.astype("uint8").tolist(), -1)
        startX = endX

    # return the bar chart
    return bar
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# read and scale down image

img = cv2.pyrDown(cv2.imread('niplegastontocado.jpg', cv2.IMREAD_UNCHANGED))
#img = cv2.GaussianBlur(img, (5,5), 0)
img = cv2.resize(img, (800, 600))
imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# threshold image
ret, threshed_img = cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY),
                127, 255, cv2.THRESH_BINARY)
# find contours and get the external one

contours, hier = cv2.findContours(threshed_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
# Now you can finally find contours.


#image, contours, hier = cv2.findContours(threshed_img, cv2.RETR_TREE,
#                cv2.CHAIN_APPROX_SIMPLE)

# with each contour, draw boundingRect in green
# a minAreaRect in red and
# a minEnclosingCircle in blue

final_contours = []
areasDeInteres = []

for contour in contours:
    area = cv2.contourArea(contour)
    if area > 2000:
        final_contours.append(contour)

#for i in range(len(final_contours)):
    #img_bgr = cv2.drawContours(img, final_contours, i, (50,250,50), 3)
for c in contours:
    # get the bounding rect
    x, y, w, h = cv2.boundingRect(c)
    # finally, get the min enclosing circle

    (x, y), radius = cv2.minEnclosingCircle(c)
    # convert all values to int
    center = (int(x), int(y))
    radius = int(radius)

    print(radius)
    if radius>35 and radius<400:
        im=Image.fromarray(imgRGB.astype('uint8'),'RGB')
        x1=int(x-w)
        y1=int(y-h)
        x2=int(x+w)
        y2=int(y+h)
        if(x1<0):
            x1=0
        if(y1<0):
            y1=0
        if(x2>im.width):
            x2=im.width
        if(y2>im.height):
            y2=im.height
        ROI = im.crop((x1,y1,x2,y2))
        ROI.show()
        areasDeInteres.append(ROI)
        img = cv2.circle(img, center, radius, (255, 0, 0), 2)
        contornopiola=c
        #cv2.imshow("A VER", img)
        cv2.waitKey(0)




print("LONGITUD PAPAAAAAA:")
print(len(c))
cv2.drawContours(img, contornopiola, -1, (255, 255, 0), 1)
ellipse = cv2.fitEllipse(contornopiola)
ellipse_pnts = cv2.ellipse2Poly( (int(ellipse[0][0]),int(ellipse[0][1]) ) ,( int(ellipse[1][0]),int(ellipse[1][1]) ),int(ellipse[2]),0,360,1)
comp = cv2.matchShapes(contornopiola,ellipse_pnts,1,0.0)
cv2.drawContours(img, [contornopiola], -1, (255, 255, 0), 1)

mask = np.zeros_like(img) # Create mask where white is what we want, black otherwise

cv2.drawContours(mask, contours, -1, (255, 255, 0), -1) # Draw filled contour in mask
out = np.zeros_like(img) # Extract out the object and place into output image
out[mask == 255] = img[mask == 255]
cv2.imshow('mask', mask)
AND = cv2.bitwise_or(img,mask)
#from PIL import Image
cv2.imshow('Output', out)
cv2.imshow("FINAL", img)

for imagen in areasDeInteres:
    np_im = np.array(imagen)
    imgBGR = cv2.cvtColor(np_im, cv2.COLOR_RGB2BGR)
    cv2.imshow("Analisis",imgBGR)
    np_im = np_im.reshape((np_im.shape[0] * np_im.shape[1],3)) #represent as row*column,channel number
    clt = KMeans(n_clusters=3) #cluster number
    clt.fit(np_im)

    hist = find_histogram(clt)
    bar = plot_colors2(hist, clt.cluster_centers_)

    plt.axis("off")
    plt.imshow(bar)
    plt.show()






# Show the output image
#cv2.imshow('Output', out)
cv2.waitKey(0)
cv2.destroyAllWindows()

if comp < 0.099:
	print("Asymmetric")
else:
	print("Symmetric")
#cv2.imshow("FINAL", img)

while True:
    key = cv2.waitKey(1)
    if key == 27: #ESC key to break
        break

cv2.destroyAllWindows()
