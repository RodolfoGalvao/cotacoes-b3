function updateCards(quotes) {
  for (const [code, q] of Object.entries(quotes)) {
    if (q.error) continue;

    const priceEl = document.getElementById("price-" + code);
    const changeEl = document.getElementById("change-" + code);

    if (priceEl) {
      priceEl.textContent = "R$ " + q.price.toFixed(2);
    }

    if (changeEl) {
      const sign = q.change >= 0 ? "+" : "";
      changeEl.textContent =
        sign + q.change.toFixed(2) + " (" + sign + q.change_pct.toFixed(2) + "%)";
      changeEl.className = "change " + (q.change >= 0 ? "positive" : "negative");
    }
  }

  const el = document.getElementById("last-updated");
  if (el) {
    el.textContent = "Última atualização: " + new Date().toLocaleTimeString("pt-BR");
  }
}

async function pollQuotes() {
  try {
    const resp = await fetch("/api/quotes");
    if (!resp.ok) throw new Error("HTTP " + resp.status);
    const data = await resp.json();
    updateCards(data);
  } catch (err) {
    console.warn("Falha ao buscar cotações:", err);
  }
}

setInterval(pollQuotes, REFRESH_INTERVAL);

async function loadChart(code) {
  const canvas = document.getElementById("chart-" + code);
  if (!canvas) return;

  try {
    const resp = await fetch("/api/history/" + code);
    const data = await resp.json();
    if (data.error || !data.closes.length) return;

    const color = (typeof TICKER_COLORS !== "undefined" && TICKER_COLORS[code]) || "#666";

    new Chart(canvas, {
      type: "line",
      data: {
        labels: data.dates,
        datasets: [{
          data: data.closes,
          borderColor: color,
          borderWidth: 2,
          pointRadius: 0,
          fill: true,
          backgroundColor: color + "18",
          tension: 0.3,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false }, tooltip: {
          callbacks: { label: ctx => "R$ " + ctx.parsed.y.toFixed(2) }
        }},
        scales: {
          x: { ticks: { maxTicksLimit: 5, font: { size: 10 } }, grid: { display: false } },
          y: { ticks: { font: { size: 10 }, callback: v => "R$" + v }, grid: { color: "#f0f0f0" } },
        },
      },
    });
  } catch (e) {
    console.warn("Erro ao carregar gráfico de " + code, e);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const el = document.getElementById("last-updated");
  if (el) {
    el.textContent = "Última atualização: " + new Date().toLocaleTimeString("pt-BR");
  }

  if (typeof TICKER_COLORS !== "undefined") {
    Object.keys(TICKER_COLORS).forEach(loadChart);
  }
});
