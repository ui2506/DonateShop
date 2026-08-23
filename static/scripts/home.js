document.addEventListener("DOMContentLoaded", () => {
  const button = document.getElementById("emoji-button");
  const container = document.querySelector(".emoji-container");

  if (!button || !container) return;

  const emojis = [...container.querySelectorAll(".emoji")];

  button.addEventListener("mouseenter", () => {
    button.classList.add("hovered");

    emojis.forEach((emoji) => {
      const angle = Math.random() * Math.PI * 2;
      const radius = 100 + Math.random() * 50;
      const x = Math.cos(angle) * radius;
      const y = Math.sin(angle) * radius;

      emoji.style.opacity = "1";
      emoji.style.transform =
        `translate(${x}px, ${y}px) rotate(${Math.random() * 360}deg)`;
    });
  });

  button.addEventListener("mouseleave", () => {
    button.classList.remove("hovered");

    emojis.forEach((emoji) => {
      emoji.style.transform = "translate(-50%, -50%)";
      emoji.style.opacity = "0";
    });
  });
});
