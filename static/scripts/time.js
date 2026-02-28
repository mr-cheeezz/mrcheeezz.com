window.onload = function() {
  setInterval(function() {
    var d = new Date();
    var time = d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', timeZone: 'America/New_York' });
    document.getElementById('time').textContent = time;

    var nyDate = new Date().toLocaleString('en-US', {timeZone: 'America/New_York'});
    nyDate = new Date(nyDate);

    var userDate = new Date();
    var userTime = userDate.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });

    var diff = nyDate - userDate;

    var diffHours = diff / (1000 * 60 * 60);
    diffHours = Math.round(diffHours);

    if (diffHours === 0) {
      document.getElementById('time-difference').textContent = "none because our clocks tick in unison.";
    } else if (diffHours === 1) {
      document.getElementById('time-difference').textContent = diffHours + " hour behind me, making it " + userTime + " in your time zone.";
    } else if (diffHours > 1) {
      document.getElementById('time-difference').textContent = diffHours + " hours behind me, with a corresponding time of " + userTime + " for you.";
    } else if (diffHours === -1) {
      document.getElementById('time-difference').textContent = (-diffHours) + " hour ahead of me, translating to " + userTime + " in your time zone.";
    } else {
      document.getElementById('time-difference').textContent = (-diffHours) + " hours ahead of me, indicating it is " + userTime + " in your time zone.";
    }
  }, 1000);
}
