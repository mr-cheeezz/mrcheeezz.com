from datetime import datetime
import pytz

TimeZone = pytz.timezone("America/New_York") 
MyTime = datetime.now(TimeZone)

class Time():
  CurrentTime = MyTime.strftime("%-I:%M %p")
  def __str__(self):
    return self.CurrentTime
    