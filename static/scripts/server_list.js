const SERVER_IPS = {
  "0": "www.praniksl.com",
  "92172": "nr.praniksl.com",
};

function setOffline(bar) {
  bar.classList.add("offline");
  bar.style.width = "100%";
  bar.textContent = "Сервер отключен";
}

function setLoading(bar) {
  bar.classList.remove("offline");
  bar.style.width = "0%";
  bar.textContent = "Загрузка...";
}

function setOnline(bar, current, max) {
  bar.classList.remove("offline");
  const percent = Math.max(0, Math.min(100, (current / max) * 100));
  bar.style.width = `${percent}%`;
  bar.textContent = `${current}/${max}`;
}

async function updatePlayerCounts(serverId, card) {
  const bar = card.querySelector(".progress-bar");
  if (!bar) return;

  try {
    const response = await fetch(
      `https://www.praniksl.com/api/proxy/server/${serverId}/`,
      { cache: "no-store" }
    );

    if (!response.ok) return setOffline(bar);

    const data = await response.json();

    if (!data?.players || typeof data.players !== "string" || !data.players.includes("/")) {
      return setOffline(bar);
    }

    const [current, max] = data.players.split("/").map(Number);

    if (!Number.isFinite(current) || !Number.isFinite(max) || max <= 0) {
      return setOffline(bar);
    }

    setOnline(bar, current, max);
  } catch {
    setOffline(bar);
  }
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.style.position = "fixed";
    textarea.style.left = "-9999px";
    document.body.appendChild(textarea);
    textarea.select();

    let ok = false;
    try { ok = document.execCommand("copy"); } catch {}

    textarea.remove();
    return ok;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".server-card").forEach((card) => {
    const serverId = card.dataset.serverId;
    const bar = card.querySelector(".progress-bar");
    const button = card.querySelector("[data-copy-ip]");

    if (button) {
      button.addEventListener("click", async () => {
        const ip = SERVER_IPS[String(serverId)];
        const text = button.querySelector("span");

        if (!ip) {
          if (text) text.textContent = "IP не задан";
          setTimeout(() => {
            if (text) text.textContent = "Скопировать IP";
          }, 1200);
          return;
        }

        const ok = await copyText(ip);

        if (text) text.textContent = ok ? "Скопировано!" : "Не удалось";
        setTimeout(() => {
          if (text) text.textContent = "Скопировать IP";
        }, 1200);
      });
    }

    if (!serverId || !bar) return;

    setLoading(bar);
    updatePlayerCounts(serverId, card);
    setInterval(() => updatePlayerCounts(serverId, card), 5000);
  });
});
