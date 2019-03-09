from __future__ import print_function

import os.path

import densenet
import numpy as np
import sklearn.metrics as metrics
import pickle

from keras.datasets import cifar100
from keras.utils import np_utils
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint
from keras import backend as K

batch_size = 128
nb_classes = 100
nb_epoch = 300

img_rows, img_cols = 32, 32
img_channels = 3

img_dim = (img_channels, img_rows, img_cols) if K.image_dim_ordering() == "th" else (img_rows, img_cols, img_channels)
depth = 40
nb_dense_block = 3
growth_rate = 12
nb_filter = -1
bottleneck = False
reduction = 0
dropout_rate = 0.0 # 0.0 for data augmentation

model = densenet.DenseNet(img_dim, classes=nb_classes, depth=depth, nb_dense_block=nb_dense_block,
                          growth_rate=growth_rate, nb_filter=nb_filter, dropout_rate=dropout_rate, 
                          bottleneck=bottleneck, reduction=reduction, weights=None)

print("Model created")

optimizer = Adam(decay=1e-4) # Using Adam instead of SGD to speed up training
model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=["accuracy"])

(trainX, trainY), (testX, testY) = cifar100.load_data()

trainX = trainX.astype('float32') / 255.
testX = testX.astype('float32') / 255.

trainX_mean = np.mean(trainX, axis=0)
trainX -= trainX_mean
testX -= trainX_mean

Y_train = np_utils.to_categorical(trainY, nb_classes)
Y_test = np_utils.to_categorical(testY, nb_classes)

generator = ImageDataGenerator(width_shift_range=0.1,
                               height_shift_range=0.1,
                               horizontal_flip=True)

generator.fit(trainX)

# Load model
save_dir = "."
model_name = 'epoch-{epoch:03d}.h5'
filepath = os.path.join(save_dir, model_name)

model_checkpoint= ModelCheckpoint(filepath, monitor="val_acc", save_best_only=True,
                                  verbose=1)

callbacks=[model_checkpoint]

model.fit_generator(generator.flow(trainX, Y_train, batch_size=batch_size),
                    steps_per_epoch=len(trainX) // batch_size, epochs=nb_epoch,
                    callbacks=callbacks,
                    validation_data=(testX, Y_test),
                    validation_steps=testX.shape[0] // batch_size, verbose=1)

model.save('epoch-300-densenet-k12.h5')
history_300 = model.history.history
with open('history-noreg.pkl', 'wb') as f:
    pickle.dump(history_300, f)

print('Saved history.')
print("Done.")
