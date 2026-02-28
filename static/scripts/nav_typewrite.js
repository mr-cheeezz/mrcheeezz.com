var i = 0;
var elem = document.querySelector('.logo__text');
var text = elem.innerText;
if (isHome) {
  elem.innerText = '';
}

function typeWriter() {
  if (i < text.length) {
    elem.innerHTML += text.charAt(i);
    i++;
    setTimeout(typeWriter, speed); 
  }
}

document.addEventListener('DOMContentLoaded', (event) => {
  if (isHome) {
    typeWriter();
  }
});