# import the necessary packages
#from keras.preprocessing.image import img_to_array
from tensorflow.keras.preprocessing.image import img_to_array
from keras.applications import imagenet_utils
from PIL import Image
import numpy as np
import settings
import helpers
import flask
import redis
import uuid
import time
import json
import io

# initialize our Flask application and Redis server
app = flask.Flask(__name__)
db = redis.StrictRedis(host=settings.REDIS_HOST,
	port=settings.REDIS_PORT, password=settings.REDIS_PASSWORD, db=settings.REDIS_DB)

def prepare_image(image, target):
	# if the image mode is not RGB, convert it
	if image.mode != "RGB":
		image = image.convert("RGB")

	# resize the input image and preprocess it
	image = image.resize(target)
	image = img_to_array(image)
	image = np.expand_dims(image, axis=0)
	image = imagenet_utils.preprocess_input(image)

	# return the processed image
	return image

@app.route("/")
def homepage():
	return "Welcome to the PyImageSearch Keras REST API!"

@app.route("/predict", methods=["POST"])
def predict():
	# initialize the data dictionary that will be returned from the
	# view
	data = {"success": False}

	# ensure an image was properly uploaded to our endpoint
	if flask.request.method == "POST":
		if flask.request.files.get("image"):
			# read the image in PIL format and prepare it for
			# classification
			image = flask.request.files["image"].read()
			image = Image.open(io.BytesIO(image))
			image = prepare_image(image,
				(settings.IMAGE_WIDTH, settings.IMAGE_HEIGHT))

			# ensure our NumPy array is C-contiguous as well,
			# otherwise we won't be able to serialize it
			image = image.copy(order="C")

			# generate an ID for the classification then add the
			# classification ID + image to the queue
			k = str(uuid.uuid4())
			image = helpers.base64_encode_image(image)
			d = {"id": k, "image": image}
			
			# Create a pubsub object for this specific request
			pubsub = db.pubsub()
			pubsub.subscribe(f"result__{k}")
			
			# Add the classification ID + image to the queue
			db.rpush(settings.IMAGE_QUEUE, json.dumps(d))

			# Wait for the result notification
			try:
				# Get the message with a timeout
				message = pubsub.get_message(timeout=30.0)
				if message and message['type'] == 'message':
					# Parse the result
					data["predictions"] = json.loads(message['data'])
					# indicate that the request was a success
					data["success"] = True
				else:
					# Timeout occurred
					data["error"] = "Request timeout"
			except Exception as e:
				data["error"] = str(e)
			finally:
				# Clean up: unsubscribe and delete the result from database
				pubsub.unsubscribe(f"result__{k}")
				try:
					db.delete(k)
				except:
					pass

	# return the data dictionary as a JSON response
	return flask.jsonify(data)

# for debugging purposes, it's helpful to start the Flask testing
# server (don't use this for production
if __name__ == "__main__":
	print("* Starting web service...")
	app.run()
