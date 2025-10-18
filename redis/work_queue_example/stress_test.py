# USAGE
# python stress_test.py

# import the necessary packages
from threading import Thread
import requests
import time
import settings

# initialize the Keras REST API endpoint URL along with the input
# image path
KERAS_REST_API_URL = f"http://localhost:{settings.SERVER_PORT}/predict"
IMAGE_PATH = "jemma.png"

# initialize the number of requests for the stress test along with
# the sleep amount between requests
NUM_REQUESTS = 50
NUM_REQUESTS = 10  # Reduced for testing
SLEEP_COUNT = 0.1


def call_predict_endpoint(n):
    try:
        # load the input image and construct the payload for the request
        with open(IMAGE_PATH, "rb") as f:
            image = f.read()
        payload = {"image": image}

        # submit the request
        response = requests.post(KERAS_REST_API_URL, files=payload, timeout=30)

        # Check if the response is valid JSON
        try:
            r = response.json()

            # ensure the request was successful
            if r.get("success", False):
                print("[INFO] thread {} OK".format(n))

                # loop over the predictions and display them
                for i, result in enumerate(r.get("predictions", [])):
                    print(
                        "{}. {}: {:.4f}".format(
                            i + 1,
                            result.get("label", "Unknown"),
                            result.get("probability", 0.0),
                        )
                    )
            else:
                print("[INFO] thread {} FAILED".format(n))
                if "error" in r:
                    print("  Error: {}".format(r["error"]))
                else:
                    print("  Response: {}".format(response.text[:100]))

        except ValueError:  # JSON decode error
            print("[INFO] thread {} FAILED - Invalid JSON response".format(n))
            print("  Status code: {}".format(response.status_code))
            print("  Response: {}".format(response.text[:100]))

    except requests.exceptions.RequestException as e:
        print("[INFO] thread {} FAILED - Request error: {}".format(n, str(e)))
    except Exception as e:
        print("[INFO] thread {} FAILED - Unexpected error: {}".format(n, str(e)))


# Create a list to hold our threads
threads = []

# loop over the number of threads
for i in range(0, NUM_REQUESTS):
    # start a new thread to call the API
    t = Thread(target=call_predict_endpoint, args=(i,))
    t.daemon = True
    t.start()
    threads.append(t)
    time.sleep(SLEEP_COUNT)

# Wait for all threads to complete
for t in threads:
    t.join()

print("[INFO] All requests completed")
