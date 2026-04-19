const menuGrid = document.getElementById("menu-grid");
const template = document.getElementById("menu-card-template");
const stackTemplate = document.getElementById("stack-item-template");
const assistantForm = document.getElementById("assistant-form");
const promptInput = document.getElementById("prompt");
const assistantResponse = document.getElementById("assistant-response");
const categoryStrip = document.getElementById("category-strip");
const searchInput = document.getElementById("search-input");
const trendTabs = document.getElementById("trend-tabs");
const recommendTabs = document.getElementById("recommend-tabs");
const bottomNav = document.getElementById("bottom-nav");
const cartCount = document.getElementById("cart-count");
const categoriesPageGrid = document.getElementById("categories-page-grid");
const trendGrid = document.getElementById("trend-grid");
const cartList = document.getElementById("cart-list");
const wishlistList = document.getElementById("wishlist-list");
const cartSubtotal = document.getElementById("cart-subtotal");
const detailImage = document.getElementById("detail-image");
const detailCategory = document.getElementById("detail-category");
const detailName = document.getElementById("detail-name");
const detailPrice = document.getElementById("detail-price");
const detailOldPrice = document.getElementById("detail-old-price");
const detailSold = document.getElementById("detail-sold");
const detailDescription = document.getElementById("detail-description");
const backButton = document.getElementById("back-button");
const installButton = document.getElementById("install-button");
const installNowButton = document.getElementById("install-now");
const installBanner = document.getElementById("install-banner");
const messagesList = document.getElementById("messages-list");

const STORAGE_KEYS = {
  cart: "zaycho-cart",
  wishlist: "zaycho-wishlist",
  messages: "zaycho-messages",
};

let menuItems = [];
let filteredItems = [];
let cartItems = [];
let wishlistItems = [];
let messages = [];
let currentView = "home";
let currentSort = "recommended";
let selectedProduct = null;
let installPrompt = null;
const viewHistory = ["home"];

function formatPrice(price) {
  return new Intl.NumberFormat("ja-JP", {
    style: "currency",
    currency: "JPY",
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
  if (lower.includes("coffee")) return "☕";
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

function getSortedItems(items, sort) {
  const copy = [...items];

  if (sort === "latest") {
    return copy.sort((a, b) => b.id - a.id);
  }

  if (sort === "sale") {
    return copy.sort((a, b) => getDiscountLabel(b.id) - getDiscountLabel(a.id));
  }

  if (sort === "bestseller") {
    return copy.sort((a, b) => (b.id % 9) - (a.id % 9));
  }

  return copy;
}

function updateActiveButtons(container, selector, activeValue, attribute) {
  container.querySelectorAll(selector).forEach((button) => {
    button.classList.toggle("active", button.getAttribute(attribute) === activeValue);
  });
}

function persistState() {
  localStorage.setItem(STORAGE_KEYS.cart, JSON.stringify(cartItems));
  localStorage.setItem(STORAGE_KEYS.wishlist, JSON.stringify(wishlistItems));
  localStorage.setItem(STORAGE_KEYS.messages, JSON.stringify(messages));
}

function hydrateState() {
  try {
    cartItems = JSON.parse(localStorage.getItem(STORAGE_KEYS.cart) || "[]");
    wishlistItems = JSON.parse(localStorage.getItem(STORAGE_KEYS.wishlist) || "[]");
    messages = JSON.parse(localStorage.getItem(STORAGE_KEYS.messages) || "[]");
  } catch (error) {
    cartItems = [];
    wishlistItems = [];
    messages = [];
  }

  if (!messages.length) {
    messages = [
      {
        title: "Welcome to ZayCho",
        body: "အသစ်ရောက် user များအတွက် coupon နဲ့ free shipping promo ရှိပါတယ်။",
      },
      {
        title: "Need help?",
        body: "Assistant section မှာ မေးမြန်းပြီး ပစ္စည်းရှာနိုင်ပါတယ်။",
      },
    ];
  }
}

function addMessage(title, body) {
  messages.unshift({ title, body });
  messages = messages.slice(0, 12);
  persistState();
  renderMessages();
}

function renderMessages() {
  messagesList.innerHTML = "";
  messages.forEach((message) => {
    const card = document.createElement("article");
    card.className = "message-card";
    card.innerHTML = `<strong>${message.title}</strong><p>${message.body}</p>`;
    messagesList.appendChild(card);
  });
}

function renderCategories(items) {
  const categories = Array.from(new Set(items.map((item) => item.category.trim())));
  categoryStrip.innerHTML = "";
  categoriesPageGrid.innerHTML = "";

  categories.forEach((category) => {
    const markup = `
      <span class="category-icon">${getCategoryIcon(category)}</span>
      <span class="category-text">${getCategoryLabel(category)}</span>
    `;

    const homeButton = document.createElement("button");
    homeButton.type = "button";
    homeButton.className = "category-chip";
    homeButton.innerHTML = markup;
    homeButton.addEventListener("click", () => {
      searchInput.value = category;
      filterMenu(category);
      showView("home");
    });
    categoryStrip.appendChild(homeButton);

    const pageButton = document.createElement("button");
    pageButton.type = "button";
    pageButton.className = "category-chip category-page-chip";
    pageButton.innerHTML = markup;
    pageButton.addEventListener("click", () => {
      searchInput.value = category;
      filterMenu(category);
      showView("home");
    });
    categoriesPageGrid.appendChild(pageButton);
  });
}

function updateCartCount() {
  cartCount.textContent = String(cartItems.length);
}

function findItemById(id) {
  return menuItems.find((item) => item.id === id);
}

function openProductDetail(item) {
  selectedProduct = item;
  detailImage.src = item.image_url;
  detailImage.alt = item.name;
  detailCategory.textContent = item.category;
  detailName.textContent = item.name;
  detailPrice.textContent = formatPrice(item.price);
  detailOldPrice.textContent = formatPrice(Math.round(item.price * 1.15));
  detailSold.textContent = `${(item.id % 9) + 1}.9k+ sold`;
  detailDescription.textContent = item.description;
  showView("detail");
}

function addToCart(item) {
  cartItems.push(item);
  updateCartCount();
  renderCart();
  persistState();
  addMessage("Added to cart", `${item.name} ကို cart ထဲထည့်ပြီးပါပြီ။`);
}

function addToWishlist(item) {
  if (!wishlistItems.some((wishlistItem) => wishlistItem.id === item.id)) {
    wishlistItems.push(item);
    addMessage("Saved to wishlist", `${item.name} ကို wishlist ထဲသိမ်းထားလိုက်ပါပြီ။`);
  }
  renderWishlist();
  persistState();
}

function renderStackList(container, items, emptyMessage, actionLabel, onAction) {
  container.innerHTML = "";

  if (!items.length) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = emptyMessage;
    container.appendChild(empty);
    return;
  }

  items.forEach((item) => {
    const fragment = stackTemplate.content.cloneNode(true);
    fragment.querySelector(".stack-image").src = item.image_url;
    fragment.querySelector(".stack-image").alt = item.name;
    fragment.querySelector(".stack-name").textContent = item.name;
    fragment.querySelector(".stack-price").textContent = formatPrice(item.price);
    fragment.querySelector(".stack-copy").textContent = item.category;
    const action = fragment.querySelector(".stack-action");
    action.textContent = actionLabel;
    action.addEventListener("click", () => onAction(item));
    container.appendChild(fragment);
  });
}

function renderCart() {
  renderStackList(
    cartList,
    cartItems,
    "Cart ထဲမှာ ပစ္စည်းမရှိသေးပါ။",
    "View",
    (item) => openProductDetail(item)
  );
  const subtotal = cartItems.reduce((sum, item) => sum + item.price, 0);
  cartSubtotal.textContent = formatPrice(subtotal);
}

function renderWishlist() {
  renderStackList(
    wishlistList,
    wishlistItems,
    "Wishlist ထဲမှာ ပစ္စည်းမရှိသေးပါ။",
    "Add",
    (item) => addToCart(item)
  );
}

function buildProductCard(item, targetGrid, jumpToCart = false) {
  const fragment = template.content.cloneNode(true);
  fragment.querySelector(".product-image").src = item.image_url;
  fragment.querySelector(".product-image").alt = item.name;
  fragment.querySelector(".product-category").textContent = item.category;
  fragment.querySelector(".product-name").textContent = item.name;
  fragment.querySelector(".product-description").textContent = item.description;
  fragment.querySelector(".product-price").textContent = formatPrice(item.price);
  fragment.querySelector(".product-sold").textContent = `${(item.id % 9) + 1}.9k+ sold`;
  fragment.querySelector(".product-badge").textContent = `-${getDiscountLabel(item.id)}%`;
  fragment.querySelector(".product-old-price").textContent = formatPrice(
    Math.round(item.price * 1.15)
  );

  const card = fragment.querySelector(".product-card");
  card.addEventListener("click", () => openProductDetail(item));

  fragment.querySelector(".product-cart").addEventListener("click", (event) => {
    event.stopPropagation();
    addToCart(item);
    if (jumpToCart) {
      showView("cart");
    }
  });

  targetGrid.appendChild(fragment);
}

function renderTrendView() {
  trendGrid.innerHTML = "";
  const trendItems = getSortedItems(menuItems, "sale").slice(0, 8);
  trendItems.forEach((item) => buildProductCard(item, trendGrid, true));
}

function renderMenu(items) {
  menuGrid.innerHTML = "";
  const sortedItems = getSortedItems(items, currentSort);

  if (!sortedItems.length) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "No products available right now.";
    menuGrid.appendChild(empty);
    return;
  }

  sortedItems.forEach((item) => buildProductCard(item, menuGrid));
}

function filterMenu(query) {
  const normalized = query.trim().toLowerCase();
  filteredItems = menuItems.filter((item) => {
    return (
      !normalized ||
      item.name.toLowerCase().includes(normalized) ||
      item.category.toLowerCase().includes(normalized) ||
      item.description.toLowerCase().includes(normalized)
    );
  });

  renderMenu(filteredItems);
}

function showView(viewName, pushHistory = true) {
  document.querySelectorAll(".view").forEach((view) => {
    view.classList.toggle("active", view.id === `view-${viewName}`);
  });

  bottomNav.querySelectorAll(".nav-item").forEach((item) => {
    item.classList.toggle("active", item.dataset.view === viewName);
  });

  currentView = viewName;
  if (pushHistory && viewHistory[viewHistory.length - 1] !== viewName) {
    viewHistory.push(viewName);
  }

  if (viewName === "cart") {
    renderCart();
  }
  if (viewName === "wishlist") {
    renderWishlist();
  }
  if (viewName === "trend") {
    renderTrendView();
  }
  if (viewName === "messages") {
    renderMessages();
  }
}

function updateInstallUi(visible) {
  installButton.classList.toggle("utility-button-hidden", !visible);
  installBanner.classList.toggle("hidden", !visible);
}

async function triggerInstallPrompt() {
  if (installPrompt) {
    installPrompt.prompt();
    await installPrompt.userChoice;
    installPrompt = null;
    updateInstallUi(false);
    return;
  }

  addMessage(
    "Install hint",
    "iPhone မှာ Share > Add to Home Screen နဲ့ install လုပ်နိုင်ပါတယ်။ Android မှာ browser install prompt ပေါ်လာမယ်။"
  );
  showView("messages");
}

async function shareSelection() {
  const item = selectedProduct || filteredItems[0] || menuItems[0];
  if (!item) {
    return;
  }

  const shareData = {
    title: item.name,
    text: `${item.name} - ${item.description}`,
    url: window.location.origin,
  };

  if (navigator.share) {
    try {
      await navigator.share(shareData);
      addMessage("Shared", `${item.name} ကို share လုပ်ပြီးပါပြီ။`);
      return;
    } catch (error) {
      if (error?.name === "AbortError") {
        return;
      }
    }
  }

  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(`${shareData.title}\n${shareData.text}\n${shareData.url}`);
    addMessage("Link copied", "Share link ကို clipboard ထဲကူးထားပါပြီ။");
  } else {
    addMessage("Share ready", `${shareData.title} - ${shareData.url}`);
  }
  showView("messages");
}

async function registerPwa() {
  if ("serviceWorker" in navigator) {
    try {
      await navigator.serviceWorker.register("/service-worker.js");
    } catch (error) {
      console.error("Service worker registration failed", error);
    }
  }

  window.addEventListener("beforeinstallprompt", (event) => {
    event.preventDefault();
    installPrompt = event;
    updateInstallUi(true);
  });

  window.addEventListener("appinstalled", () => {
    installPrompt = null;
    updateInstallUi(false);
    addMessage("Installed", "ZayCho ကို home screen app အဖြစ် install လုပ်ပြီးပါပြီ။");
  });
}

async function loadMenu() {
  try {
    const response = await fetch("/menu");
    if (!response.ok) {
      throw new Error("Failed to load menu");
    }

    menuItems = await response.json();
    filteredItems = [...menuItems];
    renderCategories(menuItems);
    renderMenu(menuItems);
    renderTrendView();
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
    addMessage("Assistant reply", data.reply);
  } catch (error) {
    assistantResponse.textContent =
      "The request did not complete. Please make sure the backend is running.";
  }
});

searchInput.addEventListener("input", (event) => {
  filterMenu(event.target.value);
  showView("home");
});

document.getElementById("search-go").addEventListener("click", () => {
  filterMenu(searchInput.value);
  showView("home");
  document.getElementById("menu-section").scrollIntoView({ behavior: "smooth" });
});

document.getElementById("camera-button").addEventListener("click", () => {
  assistantResponse.textContent =
    "Camera search demo: photo upload or barcode scan flow ကို native app step မှာဆက်ချိတ်နိုင်ပါတယ်။";
  addMessage("Camera search", "Camera search demo flow ကို next mobile iteration အတွက် ready လုပ်ထားပါတယ်။");
  showView("home");
  document.getElementById("assistant-section").scrollIntoView({ behavior: "smooth" });
});

document.getElementById("wishlist-button").addEventListener("click", () => showView("wishlist"));
document.getElementById("header-cart-button").addEventListener("click", () => showView("cart"));
document.getElementById("brand-home-button").addEventListener("click", () => showView("home"));
document.getElementById("mini-wishlist").addEventListener("click", () => showView("wishlist"));
document.getElementById("mini-share").addEventListener("click", () => shareSelection());
document.getElementById("shop-all-link").addEventListener("click", (event) => {
  event.preventDefault();
  showView("home");
  document.getElementById("menu-section").scrollIntoView({ behavior: "smooth" });
});
document.getElementById("categories-link").addEventListener("click", (event) => {
  event.preventDefault();
  showView("categories");
});
document.getElementById("promo-cta").addEventListener("click", () => showView("cart"));
document.getElementById("shipping-card").addEventListener("click", () => {
  addMessage("Free shipping", "Tokyo delivery zone အတွက် free shipping promo လက်ရှိ active ဖြစ်ပါတယ်။");
  showView("messages");
});
document.getElementById("coupon-card").addEventListener("click", () => showView("profile"));
document.querySelectorAll("[data-quick-product]").forEach((card) => {
  card.addEventListener("click", () => {
    const item = findItemById(Number(card.dataset.quickProduct));
    if (item) {
      openProductDetail(item);
    }
  });
});

document.getElementById("detail-add-cart").addEventListener("click", () => {
  if (selectedProduct) {
    addToCart(selectedProduct);
    showView("cart");
  }
});

document.getElementById("detail-wishlist").addEventListener("click", () => {
  if (selectedProduct) {
    addToWishlist(selectedProduct);
    showView("wishlist");
  }
});

document.getElementById("checkout-button").addEventListener("click", () => {
  const subtotal = cartItems.reduce((sum, item) => sum + item.price, 0);
  if (!cartItems.length) {
    addMessage("Cart is empty", "Checkout မလုပ်ခင် ပစ္စည်းတစ်ခုခုရွေးပါ။");
    showView("messages");
    return;
  }

  addMessage(
    "Checkout ready",
    `${cartItems.length} items, total ${formatPrice(subtotal)}. Payment gateway နှင့် address form ကို native release step မှာဆက်ချိတ်နိုင်ပါတယ်။`
  );
  cartItems = [];
  updateCartCount();
  renderCart();
  persistState();
  showView("messages");
});

document.getElementById("buy-action").addEventListener("click", () => {
  const target = selectedProduct || filteredItems[0] || menuItems[0];
  if (target) {
    addToCart(target);
  }
  showView("cart");
});

document.getElementById("profile-orders").addEventListener("click", () => showView("messages"));
document.getElementById("profile-coupons").addEventListener("click", () => {
  addMessage("Coupon ready", "Member credit ¥5000 ကို launch promo အတွက်သုံးနိုင်ပါတယ်။");
  showView("messages");
});
document.getElementById("profile-address").addEventListener("click", () => {
  addMessage("Delivery zone", "Tokyo delivery zone setup ပြီးရင် address form နဲ့ map integration ဆက်ချိတ်နိုင်ပါတယ်။");
  showView("messages");
});
document.getElementById("profile-support").addEventListener("click", () => showView("messages"));
installButton.addEventListener("click", () => triggerInstallPrompt());
installNowButton.addEventListener("click", () => triggerInstallPrompt());

trendTabs.querySelectorAll(".trend-tab").forEach((button) => {
  button.addEventListener("click", () => {
    updateActiveButtons(trendTabs, ".trend-tab", button.dataset.query, "data-query");
    searchInput.value = button.dataset.query;
    filterMenu(button.dataset.query);
    showView("home");
  });
});

recommendTabs.querySelectorAll(".recommend-tab").forEach((button) => {
  button.addEventListener("click", () => {
    currentSort = button.dataset.sort;
    updateActiveButtons(recommendTabs, ".recommend-tab", currentSort, "data-sort");
    renderMenu(filteredItems);
  });
});

bottomNav.querySelectorAll(".nav-item").forEach((button) => {
  button.addEventListener("click", () => showView(button.dataset.view));
});

backButton.addEventListener("click", () => {
  if (viewHistory.length > 1) {
    viewHistory.pop();
    showView(viewHistory[viewHistory.length - 1], false);
  } else {
    showView("home", false);
  }
});

hydrateState();
updateInstallUi(false);
loadMenu();
updateCartCount();
renderCart();
renderWishlist();
renderMessages();
registerPwa();
