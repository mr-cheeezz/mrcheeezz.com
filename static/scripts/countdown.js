var countdown = {
  christmas: '',
  newYears: '',
  halloween: '',
  thanksgiving: ''
};

function countdownFunction() {
  var now = new Date();
  var year = now.getFullYear();

  var christmas = new Date(year, 11, 25);
  if (now > christmas) {
    christmas.setFullYear(year + 1);
  }

  var newYears = new Date(year + 1, 0, 1);
  if (now > newYears) {
    newYears.setFullYear(year + 2);
  }

  var halloween = new Date(year, 9, 31);
  if (now > halloween) {
     halloween.setFullYear(year + 1);
  }

  var thanksgiving = new Date(year, 10, 1);
  thanksgiving.setDate(1 + (11 + 7 - thanksgiving.getDay()) % 7 + 21);
  if (now > thanksgiving) {
    thanksgiving.setFullYear(year + 1);
  }

  var diffChristmas = christmas.getTime() - now.getTime();
  var diffNewYears = newYears.getTime() - now.getTime();
  var diffHalloween = halloween.getTime() - now.getTime();
  var diffThanksgiving = thanksgiving.getTime() - now.getTime();

  countdown.christmas = getTimeString(diffChristmas, 'christmas', year);
  countdown.newYears = getTimeString(diffNewYears, 'newYears', year + 1);
  countdown.halloween = getTimeString(diffHalloween, 'halloween');
  countdown.thanksgiving = getTimeString(diffThanksgiving, 'thanksgiving');

  updateCountdownHTML();
}

function getTimeString(diff, event, year) {
  var oneDay = 1000 * 60 * 60 * 24;
  var oneMonth = oneDay * 30.44;
  var oneHour = 1000 * 60 * 60;
  var oneMinute = 1000 * 60;

  if (diff < oneDay) {
    switch (event) {
      case 'christmas':
        return "🎄 Merry Christmas! ☃️";
      case 'newYears':
        return "🎉 Happy New Year! It's " + year;
      case 'halloween':
        return "🎃 Happy Halloween! 👻";
      case 'thanksgiving':
        return "🦃 Happy Thanksgiving!";
      default:
       return "Today is the day!";
    }
  }

  var months = Math.floor(diff / oneMonth);
  diff -= months * oneMonth;
  var days = Math.floor(diff / oneDay);
  diff -= days * oneDay;
  var hours = Math.floor(diff / oneHour);
  diff -= hours * oneHour;
  var minutes = Math.floor(diff / oneMinute);
  diff -= minutes * oneMinute;

  var timeString = "";
  if (months > 0) timeString += months + (months === 1 ? " Month, " : " Months, ");
  if (days > 0) timeString += days + (days === 1 ? " Day, " : " Days, ");
  if (hours > 0) timeString += hours + (hours === 1 ? " Hour, " : " Hours, ");
  if (minutes > 0) timeString += "and " + minutes + (minutes === 1 ? " Minute" : " Minutes");

  return timeString;
}

function updateCountdownHTML() {
  var elements = document.querySelectorAll('.countdown');
  elements.forEach(function(element) {
    var html = element.innerHTML;
    html = html.replace('{countdown.christmas}', countdown.christmas);
    html = html.replace('{countdown.newYears}', countdown.newYears);
    html = html.replace('{countdown.halloween}', countdown.halloween);
    html = html.replace('{countdown.thanksgiving}', countdown.thanksgiving);
    element.innerHTML = html;
  });
}

var interval = setInterval(countdownFunction, 1000);