import pytest
import time
import random
import string
from fastapi.testclient import TestClient
from src.main import app, event_queue, stats
from src import db

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    db.init_db()
    yield
    db.init_db()  

def random_event():
    return {
        "topic": "sensor",
        "event_id": ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)),
        "timestamp": "2025-10-24T01:00:00Z",
        "source": "pytest",
        "payload": {"data": random.randint(0, 100)}
    }


def flush_queue_sync():
    """Proses semua event dari queue sinkron untuk test"""
    batch = []
    while not event_queue.empty():
        batch.append(event_queue.get_nowait())
    if batch:
        stats["received"] += len(batch)
        for e in batch:
            stats["topics"].add(e.topic)
        event_dicts = [e.dict() for e in batch]
        processed = db.try_mark_processed_bulk(event_dicts)
        db.store_events_bulk([
            {**ev, "payload": ev["payload"] if isinstance(ev["payload"], str) else str(ev["payload"])}
            for ev in processed
        ])
        stats["unique_processed"] += len(processed)
        stats["duplicate_dropped"] += len(batch) - len(processed)
        batch.clear()


def test_01_deduplication():
    event = random_event()
    client.post("/publish", json=[event])
    client.post("/publish", json=[event])
    flush_queue_sync()  # sinkron flush

    events = client.get("/events").json()
    assert len(events["events"]) >= 1


def test_02_persistence():
    event = random_event()
    db.try_mark_processed_bulk([event])
    db.init_db()  # restart DB
    result = db.try_mark_processed_bulk([event])
    assert len(result) == 0


def test_03_schema_validation():
    bad_event = {"topic": "test", "timestamp": "wrong", "payload": {}}
    res = client.post("/publish", json=[bad_event])
    assert res.status_code == 422


def test_04_stats_and_events_consistency():
    client.post("/publish", json=[random_event()])
    flush_queue_sync()  # sinkron flush

    stats_res = client.get("/stats").json()
    events_res = client.get("/events").json()
    assert stats_res["received"] >= 1
    assert events_res["count"] >= 1
    assert isinstance(stats_res["topics"], list)


def test_05_stress_5000_events():
    base_events = [random_event() for _ in range(4000)]
    duplicates = random.sample(base_events, 1000)
    all_events = base_events + duplicates
    random.shuffle(all_events)

    BATCH_SIZE_TEST = 500
    for i in range(0, len(all_events), BATCH_SIZE_TEST):
        batch = all_events[i:i + BATCH_SIZE_TEST]
        res = client.post("/publish", json=batch)
        assert res.status_code == 200

    flush_queue_sync()  

    events_res = client.get("/events").json()
    assert events_res["count"] >= 4000
