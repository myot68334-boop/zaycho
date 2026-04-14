const menuGrid = document.getElementById("menu-grid");
const template = document.getElementById("menu-card-template");
const statusBadge = document.getElementById("status-badge");
const menuCount = document.getElementById("menu-count");
const categoryCount = document.getElementById("category-count");
const menuSearch = document.getElementById("menu-search");
const categoryFilters = document.getElementById("category-filters");
const refreshMenuButton = document.getElementById("refresh-menu");
const assistantForm = document.getElementById("assistant-form");
const promptInput = document.getElementById("prompt");
const assistantResponse = document.getElementById("assistant-response");
const promptChips = document.querySelectorAll(".prompt-chip");
const clearResponseButton = document.getElementById("clear-response");

let menuItems = [];
let activeCategory = "All";

function formatPrice(price) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "MMK",
    maximumFractionDigits: 0,
  }).format(price);
}

function updateStats(items) {
  menuCount.textContent = String(items.length);
  categoryCount.textContent = String(new Set(items.map((item) => item.category)).size);
}

function renderCategoryFilters(items) {
  const categories = ["All", ...new Set(items.map((item) => item.category))];
  categoryFilters.innerHTML = "";

  categories.forEach((category) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `ghost-button filter-pill${category === activeCategory ? " is-active" : ""}`;
    button.textContent = category;
    button.addEventListener("click", () => {
      activeCategory = category;
      renderCategoryFilters(menuItems);
      renderFilteredMenu();
    });
    categoryFilters.appendChild(button);
  });
}

function renderMenu(items) {
  menuGrid.innerHTML = "";
  menuGrid.classList.remove("is-loading");

  if (!items.length) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "No products matched your current filters.";
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

function renderFilteredMenu() {
  const query = menuSearch.value.trim().toLowerCase();
  const filteredItems = menuItems.filter((item) => {
    const matchesCategory = activeCategory === "All" || item.category === activeCategory;
    const haystack = `${item.name} ${item.category} ${item.description}`.toLowerCase();
    const matchesQuery = !query || haystack.includes(query);
    return matchesCategory && matchesQuery;
  });

  renderMenu(filteredItems);
}

async function loadMenu() {
  menuGrid.classList.add("is-loading");
  statusBadge.textContent = "Checking connection...";

  try {
    const response = await fetch("/menu");
    if (!response.ok) {
      throw new Error("Failed to load menu");
    }

    menuItems = await response.json();
    updateStats(menuItems);
    renderCategoryFilters(menuItems);
    renderFilteredMenu();
    statusBadge.textContent = "Connected to backend";
  } catch (error) {
    statusBadge.textContent = "Backend connection failed";
    menuGrid.classList.remove("is-loading");
    menuGrid.innerHTML = '<p class="empty-state">Could not load the menu.</p>';
  }
}

menuSearch.addEventListener("input", () => {
  renderFilteredMenu();
});

refreshMenuButton.addEventListener("click", () => {
  loadMenu();
});

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

promptChips.forEach((chip) => {
  chip.addEventListener("click", () => {
    promptInput.value = chip.dataset.prompt || "";
    promptInput.focus();
  });
});

clearResponseButton.addEventListener("click", () => {
  promptInput.value = "";
  assistantResponse.textContent = "Waiting for your message...";
});

loadMenu();
