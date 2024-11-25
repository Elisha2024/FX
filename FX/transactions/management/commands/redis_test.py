import redis

# Create Redis connection
r = redis.Redis(
  host='redis-13028.c276.us-east-1-2.ec2.redns.redis-cloud.com',
  port=13028,
  password='53pK2CGgIguZNNNCUk4itPNUyoDx8IES'
)

# Test connection by pinging Redis
try:
    r.ping()  # This will check if the Redis server is responsive
    print("Connected to Redis")
except redis.exceptions.ConnectionError:
    print("Unable to connect to Redis")
