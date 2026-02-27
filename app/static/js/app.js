const currency = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });

const monthFilter = document.getElementById("monthFilter");
const yearFilter = document.getElementById("yearFilter");
const applyFiltersBtn = document.getElementById("applyFilters");
const form = document.getElementById("transactionForm");
const tableBody = document.getElementById("transactionTableBody");

// Inicializa mês/ano atual para o dashboard.
(function initializeFilters() {
  const now = new Date();
  for (let m = 1; m <= 12; m += 1) {
    const option = document.createElement("option");
    option.value = m;
    option.textContent = String(m).padStart(2, "0");
    if (m === now.getMonth() + 1) option.selected = true;
    monthFilter.appendChild(option);
  }
  yearFilter.value = now.getFullYear();
})();

function normalizePaymentMethod(value) {
  return (
    {
      pix: "Pix",
      cartao_credito: "Cartão de crédito",
      debito: "Débito",
      dinheiro: "Dinheiro",
    }[value] || value
  );
}

function listTemplate(item) {
  return `
    <li class="list-item ${item.vencida ? "vencida" : ""}">
      <strong>${currency.format(item.valor)}</strong> - ${item.categoria}<br/>
      <small>${item.data} • ${normalizePaymentMethod(item.forma_pagamento)}</small>
      ${item.descricao ? `<br/><small>${item.descricao}</small>` : ""}
      ${item.vencida ? `<br/><span class="tag warn">VENCIDA</span>` : ""}
    </li>
  `;
}

async function loadDashboard() {
  const month = monthFilter.value;
  const year = yearFilter.value;
  const response = await fetch(`/api/dashboard?month=${month}&year=${year}`);
  const data = await response.json();

  document.getElementById("saldoAtual").textContent = currency.format(data.saldo_atual);
  document.getElementById("entradasMes").textContent = currency.format(data.total_entradas_mes);
  document.getElementById("saidasMes").textContent = currency.format(data.total_saidas_mes);
  document.getElementById("saldoFuturo").textContent = currency.format(data.saldo_futuro);

  document.getElementById("contasPagar").innerHTML = data.contas_pagar.length
    ? data.contas_pagar.map(listTemplate).join("")
    : "<li class='list-item'>Sem contas a pagar pendentes.</li>";

  document.getElementById("contasReceber").innerHTML = data.contas_receber.length
    ? data.contas_receber.map(listTemplate).join("")
    : "<li class='list-item'>Sem contas a receber pendentes.</li>";
}

async function loadTransactions() {
  const month = monthFilter.value;
  const year = yearFilter.value;
  const response = await fetch(`/api/transactions?month=${month}&year=${year}`);
  const transactions = await response.json();

  tableBody.innerHTML = transactions
    .map(
      (item) => `
      <tr>
        <td>${item.data}</td>
        <td>${item.tipo}</td>
        <td>${item.categoria}</td>
        <td>${normalizePaymentMethod(item.forma_pagamento)}</td>
        <td>${item.descricao || "-"}</td>
        <td>${currency.format(item.valor)}</td>
        <td>
          <span class="tag ${item.pago ? "ok" : "warn"}">
            ${item.pago ? "Pago/Recebido" : "Pendente"}
          </span>
        </td>
        <td>
          <button onclick="togglePaid(${item.id}, ${item.pago})">${item.pago ? "Marcar pendente" : "Marcar pago"}</button>
          <button onclick="removeTransaction(${item.id})">Excluir</button>
        </td>
      </tr>
    `,
    )
    .join("");
}

async function refreshAll() {
  await Promise.all([loadDashboard(), loadTransactions()]);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const payload = {
    valor: Number(document.getElementById("valor").value),
    data: document.getElementById("data").value,
    tipo: document.getElementById("tipo").value,
    categoria: document.getElementById("categoria").value,
    forma_pagamento: document.getElementById("forma_pagamento").value,
    descricao: document.getElementById("descricao").value || null,
    pago: document.getElementById("pago").checked,
  };

  await fetch("/api/transactions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  form.reset();
  await refreshAll();
});

applyFiltersBtn.addEventListener("click", async () => {
  await refreshAll();
});

window.togglePaid = async (id, paid) => {
  await fetch(`/api/transactions/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pago: !paid }),
  });
  await refreshAll();
};

window.removeTransaction = async (id) => {
  await fetch(`/api/transactions/${id}`, { method: "DELETE" });
  await refreshAll();
};

refreshAll();
