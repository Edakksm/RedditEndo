
import numpy as np
import pandas as pd
from keras.preprocessing import text, sequence
from keras.preprocessing.text import Tokenizer
from keras.utils import to_categorical
from keras.models import Model, Input
from keras.layers import LSTM, Embedding, Dense, TimeDistributed, Bidirectional
from sklearn.model_selection import train_test_split
from keras.metrics import categorical_accuracy
from keras import backend as K
import tensorflow as tf

def accuracy(y_true, y_pred):
    y = tf.argmax(y_true, axis =- 1)
    y_ = tf.argmax(y_pred, axis =- 1)
    mask = tf.greater(y, 0)
    return K.cast(K.equal(tf.boolean_mask(y, mask), tf.boolean_mask(y_, mask)), K.floatx())

train_df = pd.read_csv('data/train.csv')
test_df = pd.read_csv('data/test.csv')

maxlen_seq = 512

# Loading and converting the inputs to trigrams
x_train, y_train = train_df[['Message', 'Status']].values.T

# Same for test
x_test, y_test = test_df[['Message', 'Status']].values.T

# Initializing and defining the tokenizer encoders and decoders based on the train set
tokenizer_encoder = Tokenizer(num_words=1000)
tokenizer_encoder.fit_on_texts(x_train)

# Using the tokenizer to encode and decode the sequences for use in training
# Inputs
train_input_data = tokenizer_encoder.texts_to_sequences(x_train)

train_input_data = sequence.pad_sequences(train_input_data, maxlen = maxlen_seq, padding = 'post')

# Use the same tokenizer defined on train for tokenization of test
test_input_data = tokenizer_encoder.texts_to_sequences(x_test)
test_input_data = sequence.pad_sequences(test_input_data, maxlen = maxlen_seq, padding = 'post')

# Computing the number of words and number of tags to be passed as parameters to the keras model
n_words = len(tokenizer_encoder.word_index) + 1

input = Input(shape = (maxlen_seq,))

# Defining an embedding layer mapping from the words (n_words) to a vector of len 128
x = Embedding(input_dim = n_words, output_dim = 128, input_length = maxlen_seq)(input)

# Defining a bidirectional LSTM using the embedded representation of the inputs
x = LSTM(units = 64, return_sequences = False, recurrent_dropout = 0.1)(x)

# A dense layer to output from the LSTM's64 units to the appropriate number of tags to be fed into the decoder
y = (Dense(1, activation = "sigmoid"))(x)

# Defining the model as a whole and printing the summary
model = Model(input, y)
model.summary()
"""
_________________________________________________________________
Layer (type)                 Output Shape              Param #   
=================================================================
input_1 (InputLayer)         (None, 512)               0         
_________________________________________________________________
embedding_1 (Embedding)      (None, 512, 128)          1225984   
_________________________________________________________________
bidirectional_1 (Bidirection (None, 512, 128)          98816     
_________________________________________________________________
time_distributed_1 (TimeDist (None, 512, 9)            1161      
=================================================================
Total params: 1,325,961
Trainable params: 1,325,961
Non-trainable params: 0

"""

# Setting up the model with categorical x-entropy loss and the custom accuracy function as accuracy
model.compile(optimizer = "rmsprop", loss = "binary_crossentropy", metrics = ["accuracy"])

# Splitting the data for train and validation sets
X_train, X_val, y_train, y_val = train_test_split(train_input_data, y_train, test_size = .1, random_state = 0)

# Training the model on the training data and validating using the validation set
model.fit(X_train, y_train, batch_size = 128, epochs = 5, validation_data = (X_val, y_val), verbose = 1)


y_test_pred = model.predict(test_input_data[:])
print(y_test_pred)
print(len(test_input_data))
