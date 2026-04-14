const menuGrid = document.getElementById("menu-grid");
const template = document.getElementById("menu-card-template");
const statusBadge = document.getElementById("status-badge");
const backendUrl = document.getElementById("backend-url");
const assistantForm = document.getElementById("assistant-form");
const promptInput = document.getElementById("prompt");
const assistantResponse = document.getElementById("assistant-response");

backendUrl.textContent = window.location.origin;

function formatPrice(price) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "MMK",
    maximumFractionDigits: 0,
  }).format(price);
}

function renderMenu(items) {
  menuGrid.innerHTML = "";

  if (!items.length) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "No products available right now.";
    menuGrid.appendChild(empty);
    return;
  }

  items.forEach((item) => {
    const fragment = template.content.cloneNode(true);
    fragment.querySelector(".menu-image").src = item.image_url;
    fragment.querySelector(".menu-image").alt = item.name;
    fragment.querySelector(".menu-category").textContent = item.category;
    fragment.querySelector(".menu-price").textContent = formatPrice(item.price);
    fragment.querySelector(".menu-name").textContent = item.name;
    fragment.querySelector(".menu-description").textContent = item.description;
    menuGrid.appendChild(fragment);
  });
}

async function loadMenu() {
  try {
    const response = await fetch("/menu");
    if (!response.ok) {
      throw new Error("Failed to load menu");
    }

    const items = await response.json();
    renderMenu(items);
    statusBadge.textContent = "Connected to backend";
  } catch (error) {
    statusBadge.textContent = "Backend connection failed";
    menuGrid.innerHTML = '<p class="empty-state">Could not load the menu.</p>';
  }
}

assistantForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const prompt = promptInput.value.trim();

  if (!prompt) {
    assistantResponse.textContent = "Please type a prompt first.";
    return;
  }

  assistantResponse.textContent = "Sending request...";

  try {
    const response = await fetch("/agent", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ prompt }),
    });

    if (!response.ok) {
      throw new Error("Failed to fetch assistant response");
    }

    const data = await response.json();
    assistantResponse.textContent = data.reply;
  } catch (error) {
    assistantResponse.textContent =
      "The request did not complete. Please make sure the backend is running.";
  }
});

loadMenu();
