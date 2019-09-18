import keras
from keras.datasets import cifar10
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
import os
import numpy as np
import time
# import optimus.board.server.app as optboard
import pickle
import json
import socketio
import base64
from PIL import Image
from io import BytesIO

sio = socketio.Client()
import cv2

sio.connect('http://localhost:5000')
# sio.wait()
print('zz')

arguments = {
    'batch_size': 32,
    'num_classes': 10,
    'epochs': 100,
    'data_augmentation': True,
    'num_predictions': 20,
    'optimizer': keras.optimizers.rmsprop(lr=0.0001, decay=1e-6),
    'input_shape': (32, 32, 3)
}


def inputs(args):
    (x_train, y_train), (x_test, y_test) = cifar10.load_data()
    y_train = keras.utils.to_categorical(y_train, args['num_classes'])
    y_test = keras.utils.to_categorical(y_test, args['num_classes'])

    datagen = ImageDataGenerator(
        featurewise_center=False,  # set input mean to 0 over the dataset
        samplewise_center=False,  # set each sample mean to 0
        featurewise_std_normalization=False,  # divide inputs by std of the dataset
        samplewise_std_normalization=False,  # divide each input by its std
        zca_whitening=False,  # apply ZCA whitening
        zca_epsilon=1e-06,  # epsilon for ZCA whitening
        rotation_range=0,  # randomly rotate images in the range (degrees, 0 to 180)
        # randomly shift images horizontally (fraction of total width)
        width_shift_range=0.1,
        # randomly shift images vertically (fraction of total height)
        height_shift_range=0.1,
        shear_range=0.,  # set range for random shear
        zoom_range=0.,  # set range for random zoom
        channel_shift_range=0.,  # set range for random channel shifts
        # set mode for filling points outside the input boundaries
        fill_mode='nearest',
        cval=0.,  # value used for fill_mode = "constant"
        horizontal_flip=True,  # randomly flip images
        vertical_flip=False,  # randomly flip images
        # set rescaling factor (applied before any other transformation)
        rescale=None,
        # set function that will be applied on each input
        preprocessing_function=None,
        # image data format, either "channels_first" or "channels_last"
        data_format=None,
        # fraction of images reserved for validation (strictly between 0 and 1)
        validation_split=0.0)
    return datagen.flow(x_train, y_train,
                        batch_size=args['batch_size'])


def model(args):
    model = Sequential()
    model.add(Conv2D(32, (3, 3), padding='same', input_shape=args['input_shape']))
    model.add(Activation('relu'))
    model.add(Conv2D(32, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Conv2D(64, (3, 3), padding='same'))
    model.add(Activation('relu'))
    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(512))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(args['num_classes']))
    model.add(Activation('softmax'))

    return model


# def optimize_step():
def im2json(im):
    # print(i)
    # """Convert a Numpy array to JSON string"""
    # imdata = pickle.dumps(im)
    # jstr = 'bytes("data:image/jpeg;base64,", encoding="utf-8")' + base64.b64encode(imdata)
    # cv2.imshow('asd', im.astype(np.uint8))
    # cv2.waitKey(0)
    # print(np.shape(im), np.max(im), np.min(ime))
    # buffer = BytesIO()
    # img = Image.fromarray(im, 'RGB')  # Crée une image à partir de la matrice
    # img.save(buffer, format="PNG")  # Enregistre l'image dans le buffer
    # buffer.seek(0)

    print(type(im), np.shape(im))
    is_success, buffer = cv2.imencode(".png", im.astype(np.uint8))
    io_buf = BytesIO(buffer)

    # data = buffer.read().encode("base64").replace("\n", "")
    data = base64.b64encode(io_buf.read()).decode('utf-8')
    myimage = 'data:image/png;base64,{0}'.format(data)
    return myimage


def optimize(model, input, args):
    model.compile(loss='categorical_crossentropy',
                  optimizer=args['optimizer'],
                  metrics=['accuracy'])

    n_epochs = args['epochs']
    for _ in range(n_epochs):
        for __ in range(32):
            batch_x, batch_y = next(input)
            loss, accuracy = model.train_on_batch(batch_x, batch_y)
            pred_y = model.predict_on_batch(batch_x)
            # print(loss, np.shape(batch_x)[0])

            # for layer in model.layers:
            #     weights = layer.get_weights()
            #     for filter in weights:
            #         print('-> ', type(filter))

            im_x = [im2json(batch_x[i]) for i in range(np.shape(batch_x)[0])]
            lw = [[im2json(w) for w in layer.get_weights()] for layer in model.layers]
            # print(np.shape(pred_y)[0], im2json(im_x[0]) )
            # print('----')
            time.sleep(1)
            # sio.emit('push data', {'loss': str(loss)})
            sio.emit('push data', {'predictions': im_x})
            sio.emit('push data', {'weights': lw})

    # model.fit_generator(input,
    #                     epochs=args['epochs'],
    #                     steps_per_epoch=32,
    #                     # validation_data=(x_test, y_test),
    #                     workers=4
    #                     )

    # model.fit_generator(datagen.flow(x_train, y_train,
    #                                  batch_size=batch_size),
    #                     epochs=epochs,
    #                     validation_data=(x_test, y_test),
    #                     workers=4)


# def on_heartbit():
#     optimize_step()


optimize(model(arguments), inputs(arguments), arguments)
