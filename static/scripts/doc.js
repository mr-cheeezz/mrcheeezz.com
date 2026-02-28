$(document).ready(function() {
  let toc = $("#table-of-contents");
  let currentList = $("<ul>").appendTo(toc);
  let nestedList = null;
  let nestedListLevel3 = null;
  let isFirefox = navigator.userAgent.toLowerCase().indexOf('firefox') > -0;

  $("h2:not(:first), h3, h4").each(function() {
    let level = parseInt(this.tagName[1]);
    let text = $(this).text();
    
    if (isFirefox) {
      if (text.endsWith("#")) {
        text = text.slice(0, -1);
      }
    }

    let link = $("<a>", {
      text: text,
      href: "#" + $(this).attr("id"),
      class: $(this).prop("tagName").toLowerCase()
    });

    let listItem = $("<li>").append(link);

    if (level === 2) {
      if (nestedList) {
        nestedList = null;
      }
      if (nestedListLevel3) {
        nestedListLevel3 = null;
      }
      currentList.append(listItem);
    } else if (level === 3) {
      if (!nestedListLevel3) {
        nestedListLevel3 = $("<ul>").appendTo(currentList);
      }
      if (nestedList) {
        nestedList = null;
      }
      nestedListLevel3.append(listItem);
    } else if (level === 4) {
      if (!nestedList) {
        nestedList = $("<ul>").appendTo(nestedListLevel3 || currentList);
      }
      nestedList.append(listItem);
    }
  });
});

window.onload = function() {
  var headers = document.querySelectorAll('h1, h2, h3, h4');
  for(var i = 0; i < headers.length; i++) {
    var id = headers[i].getAttribute('id');
    if(id) {
      var link = document.createElement('a');
      link.setAttribute('href', '#' + id);
      link.setAttribute('class', 'h-anchor');
      link.setAttribute('aria-hidden', 'true');
      link.innerHTML = '#';
      headers[i].appendChild(link);
    }
  }
  var modal = document.getElementById("Modal");
  var img = document.getElementsByClassName('Images');
  var modalImg = document.getElementById("img");
  var captionText = document.getElementById("caption");
  for (var i = 0; i < img.length; i++) {
    img[i].onclick = function() {
      modal.style.display = "block";
      modalImg.src = this.src;
      console.log(this.src);
      console.log(modalImg.src);
      captionText.innerHTML = this.alt;
    }
  }
  var span = document.getElementsByClassName("close")[0];
  span.onclick = function() {
    modal.style.display = "none";
  }
};