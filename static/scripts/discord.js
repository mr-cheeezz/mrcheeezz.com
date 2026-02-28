document.getElementById('link-animate').addEventListener('click', function(e) {
  e.preventDefault();
  var username = this.getAttribute('data-user');
  var dummy = document.createElement('input');
  document.body.appendChild(dummy);
  dummy.value = username;
  dummy.select();
  document.execCommand('copy');
  document.body.removeChild(dummy);
  window.location.href = this.href;
  alert('Copied discord username to clipboard!\nJust add me or whatever.');
});