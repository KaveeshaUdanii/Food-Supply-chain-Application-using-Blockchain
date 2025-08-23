# data_simulation.py
import random
import time
import uuid
import numpy as np
import pandas as pd

PRODUCT_TYPES = ["Bananas", "Tomatoes", "Apples", "Lettuce", "Potatoes"]
LOCATIONS = ["Galle", "Kandy", "Colombo", "Matara", "Anuradhapura"]

def generate_sample_batch(owner_name="farmer"):
    batch_id = str(uuid.uuid4())[:8]
    product_name = random.choice(PRODUCT_TYPES)
    origin = random.choice(LOCATIONS)
    timestamp = time.time()
    # synthetic sensor readings - small random fluctuations
    temp = round(np.random.normal(loc=15 if product_name in ["Apples"] else 22, scale=3), 2)
    humidity = round(np.random.uniform(40, 90), 2)
    notes = "Simulated batch by " + owner_name
    metadata = {'temperature': temp, 'humidity': humidity, 'notes': notes}
    return {
        'batch_id': batch_id,
        'product_name': product_name,
        'origin': origin,
        'timestamp': timestamp,
        'metadata': metadata
    }
