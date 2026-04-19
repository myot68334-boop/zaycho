const menuGrid = document.getElementById("menu-grid");
const template = document.getElementById("menu-card-template");
const assistantForm = document.getElementById("assistant-form");
const promptInput = document.getElementById("prompt");
const assistantResponse = document.getElementById("assistant-response");
const categoryStrip = document.getElementById("category-strip");
const searchInput = document.getElementById("search-input");

let menuItems = [];

function formatPrice(price) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "MMK",
    maximumFractionDigits: 0,
  }).format(price);
}

function getDiscountLabel(id) {
  const values = [5, 10, 12, 15, 18, 20];
  return values[id % values.length];
}

function getCategoryIcon(category) {
  const lower = category.toLowerCase();
  if (lower.includes("tea") || lower.includes("လက်ဖက်")) return "🍵";
  if (lower.includes("noodle") || lower.includes("ခေါက်ဆွဲ")) return "🍜";
  if (lower.includes("spice") || lower.includes("အနှစ်") || lower.includes("မဆလာ")) return "🌶️";
  if (lower.includes("fruit") || lower.includes("ယို")) return "🍍";
  if (lower.includes("coffee") || lower.includes("tea")) return "☕";
  if (lower.includes("canned")) return "🥫";
  if (lower.includes("vegetarian")) return "🥬";
  return "🛍️";
}

function getCategoryLabel(category) {
  const labels = [
    ["Tea Leaves & Assorted Beans", "လက်ဖက်"],
    ["Monhinga & Noodles", "ခေါက်ဆွဲ"],
    ["Preserved Fruits & Snack", "ယိုစုံ"],
    ["Curry Paste, Oil, Powder & Spices", "ဟင်းအနှစ်"],
    ["Canned Foods", "စည်သွပ်"],
    ["Fish Paste, Dried Fish & Dried Prawns", "ငါးပိ/ခြောက်"],
    ["Ready To Eat Food & Relish", "အသင့်စား"],
    ["Pickles & Ready To Eat Leaves", "အချဉ်အရွက်"],
    ["Salads", "အသုပ်"],
    ["Crackers and Dried Goods", "မုန့်ခြောက်"],
    ["Soup", "ဟင်းချို"],
    ["Coffee & Tea", "ကော်ဖီ"],
    ["Vegetarian", "သက်သတ်လွတ်"],
    ["Asian Groceries", "Asian"],
  ];

  for (const [match, label] of labels) {
    if (category.includes(match)) {
      return label;
    }
  }

  return category.length > 14 ? `${category.slice(0, 12)}...` : category;
}

function renderCategories(items) {
  const categories = Array.from(
    new Set(items.map((item) => item.category.trim()))
  );

  categoryStrip.innerHTML = "";

  categories.forEach((category) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "category-chip";
    button.innerHTML = `
      <span class="category-icon">${getCategoryIcon(category)}</span>
      <span class="category-text">${getCategoryLabel(category)}</span>
    `;
    button.addEventListener("click", () => {
      searchInput.value = category;
      filterMenu(category);
    });
    categoryStrip.appendChild(button);
  });
}

function filterMenu(query) {
  const normalized = query.trim().toLowerCase();
  const filtered = menuItems.filter((item) => {
    return (
      item.name.toLowerCase().includes(normalized) ||
      item.category.toLowerCase().includes(normalized) ||
      item.description.toLowerCase().includes(normalized)
    );
  });

  if (!normalized) {
    renderMenu(menuItems);
  } else {
    renderMenu(filtered);
  }
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
    fragment.querySelector(".product-image").src = item.image_url;
    fragment.querySelector(".product-image").alt = item.name;
    fragment.querySelector(".product-category").textContent = item.category;
    fragment.querySelector(".product-name").textContent = item.name;
    fragment.querySelector(".product-description").textContent = item.description;
    fragment.querySelector(".product-price").textContent = formatPrice(item.price);
    fragment.querySelector(".product-sold").textContent = `${(item.id % 9) + 1}.9k+ sold`;

    const discount = getDiscountLabel(item.id);
    fragment.querySelector(".product-badge").textContent = `-${discount}%`;
    fragment.querySelector(
      ".product-old-price"
    ).textContent = formatPrice(Math.round(item.price * 1.15));

    menuGrid.appendChild(fragment);
  });
}

async function loadMenu() {
  try {
    const response = await fetch("/menu");
    if (!response.ok) {
      throw new Error("Failed to load menu");
    }

    menuItems = await response.json();
    renderCategories(menuItems);
    renderMenu(menuItems);
  } catch (error) {
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

searchInput.addEventListener("input", (event) => {
  filterMenu(event.target.value);
});

loadMenu();
