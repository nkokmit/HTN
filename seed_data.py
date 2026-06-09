import tensorflow as tf
from tensorflow.keras.layers import LSTM, Dense, Embedding, Bidirectional

def build_behavior_model(vocab_size, embedding_dim, max_length):
    model = tf.keras.Sequential([
        Embedding(vocab_size, embedding_dim, input_length=max_length),
        Bidirectional(LSTM(64, return_sequences=True)),
        Bidirectional(LSTM(32)),
        Dense(32, activation='relu'),
        Dense(5, activation='softmax') # Giả sử có 5 phân khúc tư vấn
    ])
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model