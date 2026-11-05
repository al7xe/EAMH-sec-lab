const form = document.querySelector("#scan-form");
const scanButton = document.querySelector("#scan-button");
const refreshButton = document.querySelector("#refresh-button");
const message = document.querySelector("#message");
const deviceList = document.querySelector("#device-list");
let discoveredHosts = [];
let monitorTimer = null;

function setMessage(text, type = "") {
  message.textContent = text;
  message.className = "message" + (type ? " " + type : "");
}

function renderHosts(hosts) {
  if (!hosts.length) {
    deviceList.innerHTML = '<tr class="empty-row"><td colspan="4">لم يتم العثور على عناوين ضمن النطاق.</td></tr>';
    return;
  }
  deviceList.replaceChildren();
  for (const host of hosts) {
    const row = document.createElement("tr");
    const values = [
      ["ip-cell", host.ip],
      ["mac-cell", host.mac || "غير متاح"],
    ];
    for (const [className, value] of values) {
      const cell = document.createElement("td");
      cell.className = className;
      cell.textContent = value;
      row.appendChild(cell);
    }
    const statusCell = document.createElement("td");
    const badge = document.createElement("span");
    badge.className = "status-badge " + (host.status === "online" ? "is-online" : "is-offline");
    badge.textContent = host.status === "online" ? "متصل" : "غير مستجيب";
    statusCell.appendChild(badge);
    row.appendChild(statusCell);

    const latencyCell = document.createElement("td");
    latencyCell.textContent = host.latency_ms === null ? "—" : host.latency_ms + " ms";
    row.appendChild(latencyCell);
    deviceList.appendChild(row);
  }
}

function updateStats(hosts) {
  const online = hosts.filter(host => host.status === "online");
  const offline = hosts.length - online.length;
  const values = online.map(host => host.latency_ms).filter(value => Number.isFinite(value));
  document.querySelector("#stat-total").textContent = hosts.length;
  document.querySelector("#stat-online").textContent = online.length;
  document.querySelector("#stat-offline").textContent = offline;
  document.querySelector("#stat-latency").textContent = values.length
    ? (values.reduce((sum, value) => sum + value, 0) / values.length).toFixed(1) + " ms"
    : "—";
}

async function monitorNow() {
  if (!discoveredHosts.length) return;
  refreshButton.disabled = true;
  try {
    const response = await fetch("/api/monitor", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ addresses: discoveredHosts.map(host => host.ip) }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "تعذر تحديث حالة الأجهزة.");
    const updates = new Map(data.results.map(host => [host.ip, host]));
    discoveredHosts = discoveredHosts.map(host => ({ ...host, ...updates.get(host.ip) }));
    renderHosts(discoveredHosts);
    updateStats(discoveredHosts);
    setMessage("تم تحديث حالة " + discoveredHosts.length + " جهازًا.", "success");
  } catch (error) {
    setMessage(error.message, "error");
  } finally {
    refreshButton.disabled = false;
  }
}

form.addEventListener("submit", async event => {
  event.preventDefault();
  if (monitorTimer) clearInterval(monitorTimer);
  scanButton.disabled = true;
  refreshButton.disabled = true;
  scanButton.textContent = "جارٍ الفحص…";
  setMessage("يجري فحص نطاق الشبكة. قد تستغرق العملية بعض الوقت…");
  try {
    const response = await fetch("/api/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ network: document.querySelector("#network-input").value.trim() }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "فشل فحص الشبكة.");
    discoveredHosts = data.hosts;
    renderHosts(discoveredHosts);
    updateStats(discoveredHosts);
    refreshButton.disabled = discoveredHosts.length === 0;
    document.querySelector("#last-scan").textContent = "النطاق: " + data.network;
    setMessage("اكتمل الفحص: " + data.online + " متصل، " + data.offline + " غير مستجيب.", "success");
    monitorTimer = setInterval(monitorNow, 15000);
  } catch (error) {
    setMessage(error.message, "error");
  } finally {
    scanButton.disabled = false;
    scanButton.innerHTML = '<span class="button-icon">⌕</span> ابدأ الفحص';
  }
});

refreshButton.addEventListener("click", monitorNow);
