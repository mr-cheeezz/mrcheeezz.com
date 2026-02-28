var header = document.querySelector('.header');
var headerHeight = header.offsetHeight;
var menuMoreElement = document.querySelector('.menu__sub-inner-more');

const container = document.querySelector(".container");
const menu = document.querySelector(".menu");
const mobileMenuTrigger = document.querySelector(".menu-trigger");
const desktopMenu = document.querySelector(".menu__inner--desktop");
const desktopMenuTrigger = document.querySelector(".menu__sub-inner-more-trigger");
const menuMore = document.querySelector(".menu__sub-inner-more");
const mobileQueryRaw = getComputedStyle(document.body).getPropertyValue("--phoneWidth").trim();
const mobileQuery = mobileQueryRaw || "(max-width:684px)";
const isMobile = () => window.matchMedia(mobileQuery).matches;
const syncMenuVisibility = () => {
  const mobile = isMobile();
  mobileMenuTrigger && mobileMenuTrigger.classList.toggle("hidden", !mobile);
  if (menu) {
    if (mobile) {
      menu.classList.add("hidden");
    } else {
      menu.classList.remove("hidden");
    }
  }
  menuMore && menuMore.classList.toggle("hidden", true);
};

window.addEventListener('scroll', function() {
  if (window.innerWidth > 768) {
    if (window.scrollY > headerHeight) {
      header.classList.add('sticky');
      if (menuMoreElement) {
        menuMoreElement.classList.add('d_list');
      }
    } else {
      header.classList.remove('sticky');
      if (menuMoreElement) {
        menuMoreElement.classList.remove('d_list');
      }
    }
  }
});

function togglePasswordVisibility(inputId) {
  const passwordInput = document.getElementById(inputId);
  const icon = document.querySelector(`#${inputId} + .password-toggle`);

  if (passwordInput.type === 'password') {
    passwordInput.type = 'text';
    icon.classList.remove('fa-eye');
    icon.classList.add('fa-eye-slash');
  } else {
    passwordInput.type = 'password';
    icon.classList.remove('fa-eye-slash');
    icon.classList.add('fa-eye');
  }
}

menu && menu.addEventListener("click", e => e.stopPropagation());
menuMore && menuMore.addEventListener("click", e => e.stopPropagation());
syncMenuVisibility();
document.body.addEventListener("click", () => {
  if (!isMobile() && menuMore && !menuMore.classList.contains("hidden")) {
    menuMore.classList.add("hidden");
    const icon = document.querySelector('.greater-icon');
    icon && icon.classList.remove('rotate-icon');
  } else if (isMobile() && !menu.classList.contains("hidden")) {
    menu.classList.add("hidden");
  }
});
window.addEventListener("resize", syncMenuVisibility);
mobileMenuTrigger &&
  mobileMenuTrigger.addEventListener("click", e => {
    e.stopPropagation();
    menu && menu.classList.toggle("hidden");
  });
desktopMenuTrigger &&
  desktopMenuTrigger.addEventListener("click", e => {
    e.stopPropagation();
    menuMore && menuMore.classList.toggle("hidden");
    const icon = document.querySelector('.greater-icon');
    icon && icon.classList.toggle('rotate-icon');
    if (menuMore && menuMore.getBoundingClientRect().right > container.getBoundingClientRect().right) {
      menuMore.style.left = "auto";
      menuMore.style.right = 0;
    }
  });
