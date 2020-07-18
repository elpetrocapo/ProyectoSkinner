import cv2
import numpy as np
from PIL import Image
import argparse
import tensorflow.compat.v1 as tf
import sys

parser = argparse.ArgumentParser()
parser.add_argument(
    '--image', required=True, type=str, help='Absolute path to image file.')
    
class AreaInteres:
    """ Clase que representa el area de interes """

    def __init__(self):
        """ instancia la clase de area interes con sus caracteristicas """
        self.asimetria = 0
        self.borde = 0
        self.color =0
        self.contornoInteres=0
        self.diametro= 0
        self.imagen=0

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
def run_char(image_data):
    img = cv2.pyrDown(cv2.imread(image_data+".jpg", cv2.IMREAD_UNCHANGED))
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
        areas = cv2.contourArea(contour)
        if areas > 2000:
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

        if radius>35 and radius<400:
            area = AreaInteres()
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
            img = cv2.circle(img, center, radius, (255, 0, 0), 2)
            contornopiola=c
            ROI = im.crop((x1,y1,x2,y2))
            #ROI.show()
            area.imagen=ROI
            area.diametro=2*radius
            areasDeInteres.append(area)
            area.contornoInteres=contornopiola
            cv2.waitKey(0)


    cv2.drawContours(img, contornopiola, -1, (255, 255, 0), 1)

    mask = np.zeros_like(img) # Create mask where white is what we want, black otherwise

    cv2.drawContours(mask, contours, -1, (255, 255, 0), -1) # Draw filled contour in mask
    out = np.zeros_like(img) # Extract out the object and place into output image
    out[mask == 255] = img[mask == 255]
    #cv2.imshow('mask', mask)
    AND = cv2.bitwise_or(img,mask)
    #from PIL import Image
    #cv2.imshow('Output', out)
    #cv2.imshow("FINAL", img)

    for area in areasDeInteres:
        np_im = np.array(area.imagen)
        imgBGR = cv2.cvtColor(np_im, cv2.COLOR_RGB2BGR)
        ret, threshed_img2 = cv2.threshold(cv2.cvtColor(imgBGR, cv2.COLOR_BGR2GRAY),
                                          127, 255, cv2.THRESH_BINARY)
        # find contours and get the external one

        contours, hier = cv2.findContours(threshed_img2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            # get the bounding rect
            x, y, w, h = cv2.boundingRect(c)
            # finally, get the min enclosing circle

            (x, y), radius = cv2.minEnclosingCircle(c)
            # convert all values to int
            center = (int(x), int(y))
            radius = int(radius)

            if radius > 35 and radius < 400:
                contornopiola = c
                area.contornoInteres = contornopiola
                area.borde = imgBGR
                cv2.waitKey(0)
        cv2.drawContours(imgBGR, contornopiola, -1, (255, 255, 0), 4)
        area.borde = imgBGR
        np_im = np_im.reshape((np_im.shape[0] * np_im.shape[1],3)) #represent as row*column,channel number
        clt = KMeans(n_clusters=3) #cluster number
        clt.fit(np_im)

        hist = find_histogram(clt)
        bar = plot_colors2(hist, clt.cluster_centers_)
        plt.axis("off")
        # plt.imshow(bar)
        # plt.show()
        area.color=bar
        ellipse = cv2.fitEllipse(area.contornoInteres)
        ellipse_pnts = cv2.ellipse2Poly((int(ellipse[0][0]), int(ellipse[0][1])), (int(ellipse[1][0]), int(ellipse[1][1])),
                                        int(ellipse[2]), 0, 360, 1)
        comp = cv2.matchShapes(area.contornoInteres, ellipse_pnts, 1, 0.0)
        if comp < 0.099:
            area.asimetria="Asimetrico"
            #print("Asymmetric")
        else:
            area.asimetria="Simetrico"
            #print("Symmetric")

    # Show the output image
    #cv2.imshow('Output', out)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    #cv2.imshow("FINAL", img)
    n=1
    # for objeto in areasDeInteres:
    #     print("ESTOY EN OBJETO IN AREADEINTERES")
    #     print("OBJETO: %d" %n)
    #     print("ASIMETRIA: "+ objeto.asimetria)
    #     print("DIAMETRO: %d" %objeto.diametro)
    #     plt.imshow(objeto.color)
    #     # plt.imshow(bar)
    #     plt.show()
    #     cv2.imshow("BORDES",objeto.borde)
    #     cv2.waitKey(0)
    #     n=n+1

    jsonFinal=[]
    n=1

    for objeto in areasDeInteres:
        imgBGR = cv2.cvtColor(objeto.borde, cv2.COLOR_RGB2BGR)
        jsonItem = {}
        pathImagen = image_data+ " %d " %n
        jsonItem['pathImagen'] = pathImagen
        jsonItem['contenido']= {}
        jsonItem['contenido']['asimetria'] = objeto.asimetria
        jsonItem['contenido']['diametro'] = objeto.diametro
        plt.savefig(pathImagen+"Color.png")
        plt.imshow(objeto.color)
        
        objeto.imagen.save(pathImagen+"Recortada.png")

        imagenColor=Image.fromarray(objeto.color, 'RGB')
        imagenColor.save(pathImagen+"Color.png")
        
        imagenBorde=Image.fromarray(imgBGR, 'RGB')
        imagenBorde.save(pathImagen+"Borde.png")
        
        n=n+1
        jsonFinal.append(jsonItem)

    print(jsonFinal)
    cv2.destroyAllWindows()


def main(argv):
  """Runs inference on an image."""
  if argv[1:]:
    raise ValueError('Unused Command Line Args: %s' % argv[1:])

  if not tf.gfile.Exists(FLAGS.image):
    a = 1#tf.logging.fatal('image file does not exist %s', FLAGS.image)
  
  # load image
  image_data = FLAGS.image
  
  run_char(image_data)


if __name__ == '__main__':
  FLAGS, unparsed = parser.parse_known_args()
  tf.app.run(main=main, argv=sys.argv[:1]+unparsed)