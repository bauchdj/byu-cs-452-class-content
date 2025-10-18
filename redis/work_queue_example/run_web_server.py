# import the necessary packages
# from keras.preprocessing.image import img_to_array
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
import threading
import logger

# initialize our Flask application and Redis server
app = flask.Flask(__name__)
db = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    db=settings.REDIS_DB,
)


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
    logger.log_action("web_server", "Homepage accessed")
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
            image = prepare_image(image, (settings.IMAGE_WIDTH, settings.IMAGE_HEIGHT))

            # ensure our NumPy array is C-contiguous as well,
            # otherwise we won't be able to serialize it
            image = image.copy(order="C")

            # generate an ID for the classification then add the
            # classification ID + image to the queue
            k = str(uuid.uuid4())
            image = helpers.base64_encode_image(image)
            d = {"id": k, "image": image}

            logger.log_action(
                "web_server", f"Received image for prediction with ID: {k}"
            )

            # Create a pubsub object for this specific request
            pubsub = db.pubsub()

            # Use a threading event to signal when the result is received
            result_event = threading.Event()
            response_data = {"data": data}

            def message_handler(message):
                if message["type"] == "message":
                    response_data["data"]["predictions"] = json.loads(message["data"])
                    response_data["data"]["success"] = True
                    logger.log_action(
                        "web_server", f"Received prediction result for ID: {k}"
                    )
                    result_event.set()

            # Subscribe to the result channel with the callback
            pubsub.subscribe(**{f"result__{k}": message_handler})

            # Start the subscription in a separate thread
            thread = pubsub.run_in_thread(sleep_time=0.001)

            # Add the classification ID + image to the queue
            db.rpush(settings.IMAGE_QUEUE, json.dumps(d))

            # Wait for the result notification with a timeout
            try:
                # Wait for the result event or timeout
                if not result_event.wait(timeout=settings.SERVER_TIMEOUT):
                    response_data["data"]["error"] = "Request timeout"
                    logger.log_action("web_server", f"Request timeout for ID: {k}")
            except Exception as e:
                response_data["data"]["error"] = str(e)
                logger.log_action(
                    "web_server", f"Error processing request for ID {k}: {str(e)}"
                )
            finally:
                # Clean up: stop the thread, unsubscribe and delete the result from database
                try:
                    thread.stop()
                except:
                    pass
                pubsub.unsubscribe(f"result__{k}")
                try:
                    db.delete(k)
                except:
                    pass

            # Return the data dictionary as a JSON response
            return flask.jsonify(response_data["data"])


# for debugging purposes, it's helpful to start the Flask testing
# server (don't use this for production
if __name__ == "__main__":
    logger.log_action("web_server", "Starting web service...")
    app.run(port=settings.SERVER_PORT)
