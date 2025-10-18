#!/usr/bin/env python3

"""Script to enable Redis keyspace notifications for the work queue example"""

import settings

if __name__ == "__main__":
    print("Enabling Redis keyspace notifications...")
    success = settings.enable_redis_notifications(
        settings.REDIS_HOST, 
        settings.REDIS_PORT, 
        settings.REDIS_PASSWORD
    )
    
    if success:
        print("Redis notifications enabled successfully.")
    else:
        print("Failed to enable Redis notifications.")
