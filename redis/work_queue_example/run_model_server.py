# import the necessary packages
from tensorflow.keras.applications import ResNet50
from keras.applications import imagenet_utils
import numpy as np
import settings
import helpers
import redis
import time
import json

import os

os.environ['KMP_DUPLICATE_LIB_OK']='True'

# connect to Redis server
db = redis.StrictRedis(host=settings.REDIS_HOST,
	port=settings.REDIS_PORT, password=settings.REDIS_PASSWORD, db=settings.REDIS_DB)

def classify_process():
	# load the pre-trained Keras model (here we are using a model
	# pre-trained on ImageNet and provided by Keras, but you can
	# substitute in your own networks just as easily)
	print("* Loading model...")
	model = ResNet50(weights="imagenet")
	print("* Model loaded")

	# Process images one at a time as they arrive in the queue
	while True:
		try:
			# Blocking pop from the queue (timeout after 1 second)
			queue_item = db.blpop(settings.IMAGE_QUEUE, timeout=1)
			
			if queue_item:
				# deserialize the object and obtain the input image
				_, data = queue_item  # blpop returns (key, value) tuple
				q = json.loads(data.decode("utf-8"))
				image = helpers.base64_decode_image(q["image"],
					settings.IMAGE_DTYPE,
					(1, settings.IMAGE_HEIGHT, settings.IMAGE_WIDTH,
						settings.IMAGE_CHANS))

				# classify the image
				print("* Processing image ID: {}".format(q["id"]))
				preds = model.predict(image)
				results = imagenet_utils.decode_predictions(preds)

				# initialize the list of output predictions
				output = []

				# loop over the results and add them to the list of
				# output predictions
				for (imagenetID, label, prob) in results[0]:
					r = {"label": label, "probability": float(prob)}
					output.append(r)

				# store the output predictions in the database, using
				# the image ID as the key so we can fetch the results
				# Also publish a notification that the result is ready
				db.set(q["id"], json.dumps(output))
				db.publish(f"result__{q['id']}", json.dumps(output))

				print("* Processed image ID: {}".format(q["id"]))
		except Exception as e:
			print("Error processing image: {}".format(str(e)))

# if this is the main thread of execution start the model server
# process
if __name__ == "__main__":
	classify_process()
