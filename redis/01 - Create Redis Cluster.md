# Creating a Redis Cluster

The easiest way to get Redis up and running is to use Redis Cloud:

1. Go to [Redis Cloud](https://redis.com/redis-enterprise-cloud/overview) and click “Try for Free”. Sign up for a free account.  
2. Create a free Redis database instance by choosing a Cloud Platform (I chose Google Cloud Platform) and click “Let's Start Free”.  
3. Click your database in the control panel and look for these settings under configuration (You will need them to connect to your Redis database):  
   - Public Endpoint (this is your URL and port)  
   - Default User 
   - Default User Password

A good client for managing your database is RedisInsight. You can download that here: https://redis.com/redis-enterprise/redis-insight/

4. In RedisInsight, click **“Add Redis Database”** and enter your database settings from earlier.  
5. Click on your database to connect to it. RedisInsight opens in the **Keys** view (notice the highlighted key icon on the left). You can use the refresh button to view keys. Initially, you won’t see any.  
6. Click the Workbench icon (looks like a document) on the left to run Redis commands.  

### Test Your Setup

Run the following command in the Workbench:

```
ping
```

You should get PONG in response.

If that worked, you can now head over to the [readme.md](https://github.com/byu-cs-452/byu-cs-452-class-content/blob/main/redis/work_queue_example/readme.md) in the work_queue_example folder to get started on the rest of the project!
