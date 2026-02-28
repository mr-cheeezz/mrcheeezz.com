const localTheme = window.localStorage && window.localStorage.getItem("theme");
const themeToggle = document.querySelector(".theme-toggle");

const tooltip = document.querySelector('.tooltip.fade');
const sunIcon = document.getElementById('sun-icon');
const moonIcon = document.getElementById('moon-icon');
const halfCircleIcon = document.getElementById('half-circle-icon');

function setTooltipAndIcon() {
  const themeIcon = document.getElementById("theme");
  
  if (themeIcon) {
    const isDarkTheme = document.body.classList.contains("dark-theme");
    const isLightTheme = document.body.classList.contains("light-theme");

    sunIcon.style.display = isLightTheme ? 'block' : 'none';
    moonIcon.style.display = isDarkTheme ? 'block' : 'none';
    halfCircleIcon.style.display = isLightTheme || isDarkTheme ? 'none' : 'block';

    if (isLightTheme) {
      themeIcon.setAttribute("data-title", "Set Theme to Dark");
    } else if (isDarkTheme) {
      themeIcon.setAttribute("data-title", "Set Theme to Light");
    } else {
      themeIcon.setAttribute("data-title", "Toggle Theme");
    }
  }
}

if (localTheme) {
  document.body.classList.remove("light-theme", "dark-theme");
  document.body.classList.add(localTheme);
}

setTooltipAndIcon();

themeToggle.addEventListener("click", () => {
  const themeUndefined = !new RegExp("(dark|light)-theme").test(document.body.className);
  const isOSDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

  if (themeUndefined) {
    if (isOSDark) {
      document.body.classList.add("light-theme");
    } else {
      document.body.classList.add("dark-theme");
    }
  } else {
    document.body.classList.toggle("light-theme");
    document.body.classList.toggle("dark-theme");
  }

  setTooltipAndIcon();

  window.localStorage &&
    window.localStorage.setItem(
      "theme",
      document.body.classList.contains("dark-theme") ? "dark-theme" : "light-theme",
    );
});