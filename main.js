// main.js

// ----------------------------
// AI Chat
// ----------------------------
const form = document.getElementById("question-form");
const input = document.getElementById("question-input");
const output = document.getElementById("answer-output");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const question = input.value.trim();
  if (!question) return;

  // Clear previous answer and show loading
  output.textContent = "⏳ Thinking...";

  try {
    const response = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    const data = await response.json();

    if (data.answer) {
      const formatted = data.answer
        .split("\n")
        .map(line => line.trim())
        .filter(line => line.length > 0)
        .join("\n");
      output.textContent = formatted;
    } else {
      output.textContent = "⚠️ No answer received.";
    }

    output.scrollTop = output.scrollHeight;

  } catch (err) {
    output.textContent = `❌ Error: ${err.message}`;
  }

  input.value = "";
  input.focus();
});

// ----------------------------
// Transaction Table
// ----------------------------
async function loadTransactions() {
  const tbody = document.querySelector("#transactions-table tbody");
  tbody.innerHTML = "";
  const res = await fetch("/transactions");
  const data = await res.json();

  data.forEach((t, idx) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${t.date}</td>
      <td>$${t.amount.toFixed(2)}</td>
      <td>${t.category}</td>
      <td>${t.description}</td>
      <td>${t.payment_method}</td>
      <td><button class="btn btn-delete" data-idx="${idx}">Delete</button></td>
    `;
    tbody.appendChild(row);
  });

  // Attach delete events
  document.querySelectorAll(".btn-delete").forEach(btn => {
    btn.addEventListener("click", async () => {
      const idx = parseInt(btn.getAttribute("data-idx"));
      await fetch("/delete_transaction", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ idx })
      });
      loadTransactions(); // Refresh table
    });
  });
}

// Add transaction
document.getElementById("add-transaction-form").addEventListener("submit", async e => {
  e.preventDefault();
  const data = {
    date: document.getElementById("t-date").value,
    amount: document.getElementById("t-amount").value,
    category: document.getElementById("t-category").value,
    description: document.getElementById("t-description").value,
    payment_method: document.getElementById("t-method").value
  };

  await fetch("/add_transaction", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });

  loadTransactions();
  document.getElementById("add-transaction-form").reset();
});

// Initial load
loadTransactions();
