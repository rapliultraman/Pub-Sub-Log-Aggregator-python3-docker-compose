#memberikan permission pada folder data agar dapat diakses oleh docker container
sudo chmod -R 777 /Path/to/your/dir/data 


#menjalankan unit test pada docker container aggregator
sudo docker compose run -e MODE=TEST aggregator


#script untuk build dan run docker container dengan skema publiher mesin berbeda
sudo docker compose build --no-cache
sudo docker compose up


#TESTING


#POST EVENTS
curl -X POST http://localhost:8080/publish \
-H "Content-Type: application/json" \
-d '[{"topic":"demo","event_id":"E001","timestamp":"2025-10-24T02:00:00Z","source":"manual","payload":{"msg":"hello"}},
     {"topic":"demo","event_id":"E001","timestamp":"2025-10-24T02:00:00Z","source":"manual","payload":{"msg":"hello"}}]'


#GET STATS
curl -X GET "http://localhost:8080/stats"


#GET EVENTS
curl -X GET "http://localhost:8080/events


#DB CHECK
sqlite3 data/dedub.db
SELECT * FROM processed_events;
SELECT * FROM events;