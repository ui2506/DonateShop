document.addEventListener("DOMContentLoaded", () => {
  const stars = document.querySelector(".stars-bg");
  if (!stars) return;

  for (let i = 0; i < 26; i++) {
    const star = document.createElement("span");
    const size = Math.random() * 2.7 + 1.3;

    star.style.width = `${size}px`;
    star.style.height = `${size}px`;
    star.style.top = `${Math.random() * 100}%`;
    star.style.left = `${Math.random() * 100}%`;
    star.style.opacity = Math.random() * .3 + .6;
    star.style.animationDuration = `${2.4 + Math.random() * 2.7}s`;

    stars.appendChild(star);
  }
});
