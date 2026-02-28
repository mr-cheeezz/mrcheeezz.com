def milliseconds_to_minutes_seconds(ms):
  total_seconds = int(ms / 1000)
  minutes = int(total_seconds / 60)
  seconds = total_seconds % 60
  return f"{minutes}:{str(seconds).zfill(2)}"
