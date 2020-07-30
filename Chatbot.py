import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

import numpy as np
import tflearn
import tensorflow as tf
import random
import json
import pickle

with open("intents.json") as file:
	data = json.load(file)

try:
	with open("data.pickle", "rb") as file:
		words, labels, training, output = pickle.load(file)
except:	
	words = []
	labels = []
	docs_x = []
	docs_y = []

	# nltk.download('punkt')

	for intent in data["intents"]:
		for pattern in intent["patterns"]:
			wrds = nltk.word_tokenize(pattern)
			words.extend(wrds)
			docs_x.append(words)
			docs_y.append(intent["tag"])

		if intent["tag"] not in labels:
			labels.append(intent["tag"])

	words = [stemmer.stem(w.lower()) for w in words if w not in "?"]
	words = sorted(list(set(words)))

	labels = sorted(labels)

	training = []
	output = []

	out_empty = [0 for _ in range(len(labels))]

	for x, doc in enumerate(docs_x):
		bag = []

		wrds = [stemmer.stem(w.lower()) for w in doc]

		for w in words:
			if w in wrds:
				bag.append(1)
			else:
				bag.append(0)

		output_row = out_empty[:]
		output_row[labels.index(docs_y[x])] = 1

		training.append(bag)
		output.append(output_row)

	training = np.array(training)
	output = np.array(output)

	with open("data.pickle", "wb") as file:
		pickle.dump((words, labels, training, output), file )

tf.reset_default_graph()

net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation = 'softmax')
net = tflearn.regression(net)

model = tflearn.DNN(net)


try:
 	model.load("model.tflearn")
except:
	model.fit(training, output, n_epoch = 1000, batch_size = 8, show_metric = True)
	model.save("model.tflearn")

'''
import tensorflow as tf
print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))
'''

def bag_of_words(s, words):
	bag = [0 for _ in range(len(words))] 

	s_words = nltk.word_tokenize(s)
	s_words = [stemmer.stem(word.lower()) for word in s_words]

	for se in s_words:
		for i, w in enumerate(words):
			if w == se:
				bag[i] = 1

	return np.array(bag)

def chat():

	print("Start Talking with Bot!(type quit to exit)")
	while True:
		inp = input("You: ")
		if inp.lower() == "quit":
			break
		results = model.predict([bag_of_words(inp.lower(), words)])
		print(results)

chat()