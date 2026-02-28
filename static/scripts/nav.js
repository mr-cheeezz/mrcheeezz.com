document.addEventListener("DOMContentLoaded", function() {
  const elements = document.querySelectorAll('.nav__href');
  
  elements.forEach(function(element) {
    element.onclick = function() {
      const hrefValue = this.getAttribute('data-href');
      if (hrefValue) {
        window.location.href = hrefValue === 'home' ? '/' : `/${hrefValue}`;
        return false;
      }
    }
  });
});
