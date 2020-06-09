from keras_preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense
from keras import backend as k
import numpy as np
from keras_preprocessing import image
from tensorflow.keras.callbacks import TensorBoard

IMG_SIZE = 50

train_data_dir= 'D:/Users/petrofac/Downloads/ProyectoSkinner/ProyectoSkinner/RedCNN/Red2/data/train'
validation_data_dir = 'D:/Users/petrofac/Downloads/ProyectoSkinner/ProyectoSkinner/RedCNN/Red2/data/validation'
nb_train_samples=1000
nb_validation_samples=100
epochs=20
batch_size=20

if k.image_data_format()=='channels_first':
    input_shape= (3, IMG_SIZE, IMG_SIZE)
else:
    input_shape= (IMG_SIZE, IMG_SIZE,3)

train_datagen = ImageDataGenerator(rescale=1. /255, shear_range=0.2, zoom_range=0.2, horizontal_flip=True)

test_datagen=ImageDataGenerator(rescale=1. / 255)

train_generator = train_datagen.flow_from_directory(train_data_dir,target_size=(IMG_SIZE, IMG_SIZE), batch_size=batch_size, class_mode='categorical', shuffle=True)

validation_generator = test_datagen.flow_from_directory(validation_data_dir, target_size=(IMG_SIZE, IMG_SIZE), batch_size=batch_size, class_mode='categorical', shuffle=True)

##########################################################################

model = Sequential()
model.add(Conv2D(32, (3,3), input_shape=input_shape))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2,2)))

model.summary()

model.add(Conv2D(32, (3,3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2,2)))

model.add(Conv2D(64, (3,3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2,2)))

model.add(Flatten())
model.add(Dense(64))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(3))
model.add(Activation('softmax'))

model.summary()

model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])

model.fit_generator(train_generator, steps_per_epoch=nb_train_samples // batch_size, epochs=epochs, validation_data=validation_generator, validation_steps=nb_validation_samples // batch_size)

model.save_weights('first_try.h5')
model.save('modeloCompleto.h5')

img_pred = image.load_img('D:/Users/petrofac/Downloads/ProyectoSkinner/ProyectoSkinner/RedCNN/Red2/vitiligo2.jpeg',target_size=(IMG_SIZE,IMG_SIZE))

img_pred = image.img_to_array(img_pred)
img_pred = np.expand_dims(img_pred, axis=0)

################################
from keras.models import load_model
model = load_model('modeloCompleto.h5')
res = model.predict(img_pred)
print(res)

if res[0][0]==1:
    prediction='gato'
elif res[0][1]==1:
    prediction='melanoma'
else:
    prediction='vitiligo'
print(prediction)

