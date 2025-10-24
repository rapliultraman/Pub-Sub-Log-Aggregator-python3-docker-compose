from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
import asyncio, json, os, time
from . import db
from .models import Event

app = FastAPI(title="Pub-Sub Log Aggregator", version="2.0")
db.init_db()

event_queue: asyncio.Queue = asyncio.Queue()
stats = {
    "received": 0,
    "unique_processed": 0,
    "duplicate_dropped": 0,
    "topics": set(),
}

BATCH_SIZE = 100     
FLUSH_INTERVAL = 0.3 

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(batch_consumer())

async def batch_consumer():
    """Consumer optimized pakai batch commit"""
    batch = []
    last_flush = time.time()
    while True:
        try:
            event = await asyncio.wait_for(event_queue.get(), timeout=FLUSH_INTERVAL)
            batch.append(event)
            stats["received"] += 1
            stats["topics"].add(event.topic)
        except asyncio.TimeoutError:
            pass

        
        if batch and (len(batch) >= BATCH_SIZE or time.time() - last_flush >= FLUSH_INTERVAL):
            event_dicts = [e.dict() for e in batch]
            processed = db.try_mark_processed_bulk(event_dicts)
            db.store_events_bulk([
                {**ev, "payload": json.dumps(ev["payload"])} for ev in processed
            ])
            stats["unique_processed"] += len(processed)
            stats["duplicate_dropped"] += len(batch) - len(processed)
            batch.clear()
            last_flush = time.time()

@app.post("/publish")
async def publish_events(events: List[Event]):
    for ev in events:
        await event_queue.put(ev)
    return {"status": "queued", "count": len(events)}

@app.get("/events")
def get_events(topic: Optional[str] = Query(None)):
    try:
        events = db.get_events(topic)
        return {"count": len(events), "events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
def get_stats():
    return {**stats, "topics": list(stats["topics"])}
