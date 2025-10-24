import requests, time, random, uuid, json

BASE_URL = "http://aggregator:8080"
TOPICS = ["system.logs", "user.activity", "security.alerts"]
BATCH_SIZE = 50  


def generate_event():
    topic = random.choice(TOPICS)
    return {
        "topic": topic,
        "event_id": str(uuid.uuid4()),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),  # ISO UTC
        "source": "publisher-service",
        "payload": {"msg": f"Event from {topic}", "value": random.randint(1, 100)}
    }


def wait_for_aggregator(retries=10, interval=2):
    for i in range(retries):
        try:
            r = requests.get(f"{BASE_URL}/stats", timeout=2)
            if r.status_code == 200:
                print("Aggregator ready.")
                return True
        except requests.exceptions.RequestException:
            print(f"Aggregator not ready. Retrying in {interval}s... ({i+1}/{retries})")
            time.sleep(interval)
    print("Error: Could not connect to aggregator after several retries.")
    return False


def send_events(events):
    """Kirim list events per batch kecil"""
    for i in range(0, len(events), BATCH_SIZE):
        batch = events[i:i + BATCH_SIZE]
        try:
            r = requests.post(f"{BASE_URL}/publish", json=batch, timeout=5)
            print(f"Sent batch {i//BATCH_SIZE + 1}: {len(batch)} events, Response: {r.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending batch {i//BATCH_SIZE + 1}: {e}")
        time.sleep(0.1)  


if __name__ == "__main__":
    if not wait_for_aggregator():
        exit(1)

    print("Generating 120 events (with duplicates)...")
    events = [generate_event() for _ in range(100)]
    duplicates = random.sample(events, 20)
    all_events = events + duplicates
    random.shuffle(all_events)

    send_events(all_events)
    print("All events sent. Waiting 2s for batch consumer to flush...")
    time.sleep(2)
    print("Done.")
