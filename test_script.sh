#!/bin/bash
event_names=("login" "logout")
API_ENDPOINT_URL="http://0.0.0.0:8000/user/log"

total_requests=0
requests_per_second=1000

while true; do
  start_time=$(date +%s)
  random_index=$((RANDOM % ${#event_names[@]}))
  event_name=${event_names[$random_index]}
  user_id=$(shuf -i 100000-999999 -n 1)
  log_id=$(shuf -i 1000-9999 -n 1)
  REQUEST_DATA='{
    "id": '$log_id',
    "unix_ts": '$start_time',
    "user_id": '$user_id',
    "event_name": "'$event_name'"
  }'
  curl -X POST -H "Content-Type: application/json" -d "$REQUEST_DATA" "$API_ENDPOINT_URL" -w "\n"
  end_time=$(date +%s)
  elapsed_time=$((end_time - start_time))

  sleep_time=$((1 / requests_per_second - elapsed_time))
  if ((sleep_time > 0)); then
    sleep "$sleep_time"
  fi

  total_requests=$((total_requests + 1))

  if ((total_requests % requests_per_second == 0)); then
    echo "Sent $total_requests requests"
  fi
done
