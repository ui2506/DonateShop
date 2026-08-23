document.addEventListener('DOMContentLoaded', function () {
  const navbar = document.querySelector('.navbar');
  const copy_right = document.querySelector('.copy_right');
  const startYear = 2025;
  const currentYear = new Date().getFullYear();
  const yearString = currentYear > startYear ? `${startYear} - ${currentYear}` : `${startYear}`;

  copy_right.innerHTML = `\u00A9 ${yearString} <b>${window.location.hostname}</b>`;

  let lastScrollTop = 0;

  window.addEventListener('scroll', function () {
    const scrollTop = window.scrollY;

    if (scrollTop > 10) {
      navbar.classList.add('navbar-scrolled');
      navbar.classList.remove('navbar-none-scrolled');
    } 
    else {
      navbar.classList.add('navbar-none-scrolled');
      navbar.classList.remove('navbar-scrolled');
    }

    lastScrollTop = scrollTop;
  });
});