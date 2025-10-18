1. image_queue. Redis show is it a List. The list maps indexes to JSON objects.

2. The web server puts the image in the queue, then the model server periodically checks the queue for new images to process. Once the model server processes the image it puts it in the queue with a unique key (UUID) and the web server pops it from the queue and returns the results as the response to the request.

3. Results:
```sh
1. church: 0.4136 
2. castle: 0.3930 
3. monastery: 0.1733 
4. palace: 0.0041 
5. vault: 0.0034
```

4. The model server pulls batches and does not remove them from the queue until they are done. This will cause race conditions. The web server and model server both poll the queue instead of setting up a socket to receive notifications. 

After updates:
1. Web server receives an image, generates a unique ID, and pushes it to the Redis queue
2. Model servers block-wait on the queue; Redis ensures only one server gets each item
3. When a model server finishes processing, it publishes the result to a dedicated channel
4. The web server receives the notification and immediately returns the result to the client
