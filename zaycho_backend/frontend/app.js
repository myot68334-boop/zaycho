const productGrid = document.getElementById("product-grid");
const categoryList = document.getElementById("category-list");
const searchInput = document.getElementById("search-input");
const resultSummary = document.getElementById("result-summary");
const cartItemsEl = document.getElementById("cart-items");
const cartCount = document.getElementById("cart-count");
const cartSubtotal = document.getElementById("cart-subtotal");
const cartShipping = document.getElementById("cart-shipping");
const cartTotal = document.getElementById("cart-total");
const checkoutPanel = document.getElementById("checkout-panel");
const checkoutToggle = document.getElementById("checkout-toggle");
const closeCheckout = document.getElementById("close-checkout");
const checkoutForm = document.getElementById("checkout-form");
const checkoutStatus = document.getElementById("checkout-status");
const authForm = document.getElementById("auth-form");
const authModeToggle = document.getElementById("auth-mode-toggle");
const authSubmit = document.getElementById("auth-submit");
const authStatus = document.getElementById("auth-status");
const authHelper = document.getElementById("auth-helper");
const authName = document.getElementById("auth-name");
const authEmail = document.getElementById("auth-email");
const authPassword = document.getElementById("auth-password");
const authStateGuest = document.getElementById("auth-state-guest");
const authStateUser = document.getElementById("auth-state-user");
const accountName = document.getElementById("account-name");
const accountEmail = document.getElementById("account-email");
const accountRole = document.getElementById("account-role");
const logoutButton = document.getElementById("logout-button");
const deleteAccountButton = document.getElementById("delete-account-button");
const ordersList = document.getElementById("orders-list");
const assistantInput = document.getElementById("assistant-input");
const assistantSubmit = document.getElementById("assistant-submit");
const assistantResponse = document.getElementById("assistant-response");
const openCartButton = document.getElementById("open-cart-button");
const checkoutPayment = document.getElementById("checkout-payment");
const stripePanel = document.getElementById("stripe-panel");
const stripeNote = document.getElementById("stripe-note");
const paymentElementContainer = document.getElementById("payment-element");
const adminPanel = document.getElementById("admin-panel");
const adminStats = document.getElementById("admin-stats");
const metricProducts = document.getElementById("metric-products");
const metricOrders = document.getElementById("metric-orders");
const adminHint = document.getElementById("admin-hint");
const scrollAdmin = document.getElementById("scroll-admin");
const telegramAdminSummary = document.getElementById("telegram-admin-summary");
const telegramWebhookUrl = document.getElementById("telegram-webhook-url");
const telegramSetupButton = document.getElementById("telegram-setup-button");
const telegramStatus = document.getElementById("telegram-status");
const telegramOpenBot = document.getElementById("telegram-open-bot");
const telegramTestMessage = document.getElementById("telegram-test-message");
const telegramTestButton = document.getElementById("telegram-test-button");

const productForm = document.getElementById("product-form");
const productStatus = document.getElementById("product-status");
const adminProductList = document.getElementById("admin-product-list");
const adminOrderList = document.getElementById("admin-order-list");
const adminOrderStatus = document.getElementById("admin-order-status");
const clearProductForm = document.getElementById("clear-product-form");
const uploadImageButton = document.getElementById("upload-image-button");
const productImageFile = document.getElementById("product-image-file");

const STORAGE_KEYS = {
  cart: "lyra-cart",
  token: "lyra-token",
};

const state = {
  mode: "login",
  token: localStorage.getItem(STORAGE_KEYS.token) || "",
  user: null,
  products: [],
  categories: [],
  selectedCategory: "All",
  cart: [],
  orders: [],
  adminProducts: [],
  adminOrders: [],
  config: {
    stripe_enabled: false,
    stripe_publishable_key: "",
    tracking_steps: [],
    default_admin_email: "",
    telegram_enabled: false,
    telegram_bot_username: "",
    telegram_webhook_url: "",
    telegram_last_chat_id: "",
  },
  stripe: null,
  elements: null,
  paymentElement: null,
  activePaymentIntent: null,
};

const LOCAL_ASSISTANT_HOSTS = new Set(["localhost", "127.0.0.1"]);
const N8N_WEBHOOK_URL = "http://localhost:5678/webhook/ollama-chat";

function formatPrice(amount) {
  return new Intl.NumberFormat("ja-JP", {
    style: "currency",
    currency: "JPY",
    maximumFractionDigits: 0,
  }).format(amount);
}

function saveCart() {
  localStorage.setItem(STORAGE_KEYS.cart, JSON.stringify(state.cart));
}

function loadCart() {
  try {
    state.cart = JSON.parse(localStorage.getItem(STORAGE_KEYS.cart) || "[]");
  } catch (error) {
    state.cart = [];
  }
}

function groupedCartItems() {
  const grouped = new Map();
  state.cart.forEach((item) => {
    const existing = grouped.get(item.id);
    if (existing) {
      existing.quantity += 1;
    } else {
      grouped.set(item.id, { ...item, quantity: 1 });
    }
  });
  return [...grouped.values()];
}

function calculateTotals() {
  const subtotal = groupedCartItems().reduce((sum, item) => sum + item.price * item.quantity, 0);
  const shipping = subtotal === 0 ? 0 : subtotal >= 12000 ? 0 : 800;
  return { subtotal, shipping, total: subtotal + shipping };
}

function parseCsv(value) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function productVisual(product) {
  if (product.image_url) {
    return `<img src="${product.image_url}" alt="${product.name}" class="product-image" />`;
  }
  return `<span>${product.display_emoji}</span>`;
}

function updateAuthUi() {
  const isRegister = state.mode === "register";
  authSubmit.textContent = isRegister ? "Create Account" : "Login";
  authModeToggle.textContent = isRegister ? "Switch to Login" : "Switch to Register";
  authHelper.textContent = isRegister
    ? "Register လုပ်ပြီးတာနဲ့ order history နဲ့ checkout ကို account နဲ့သုံးနိုင်ပါတယ်။"
    : "အကောင့်ဝင်ပြီး checkout နဲ့ order history ကို အသုံးပြုနိုင်ပါတယ်။";
  authName.required = isRegister;
  authName.style.display = isRegister ? "block" : "none";

  if (state.user) {
    authStateGuest.classList.add("hidden");
    authStateUser.classList.remove("hidden");
    accountName.textContent = state.user.full_name;
    accountEmail.textContent = state.user.email;
    accountRole.textContent = `Role: ${state.user.role}`;
  } else {
    authStateGuest.classList.remove("hidden");
    authStateUser.classList.add("hidden");
  }

  adminPanel.classList.toggle("hidden", state.user?.role !== "admin");
  telegramSetupButton.disabled = state.user?.role !== "admin";
  telegramTestButton.disabled = state.user?.role !== "admin";
}

function renderCategories() {
  categoryList.innerHTML = "";
  ["All", ...state.categories].forEach((category) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = category === state.selectedCategory ? "category-button active" : "category-button";
    button.textContent = category;
    button.addEventListener("click", () => {
      state.selectedCategory = category;
      renderCategories();
      renderProducts();
    });
    categoryList.appendChild(button);
  });
}

function filteredProducts() {
  const normalized = searchInput.value.trim().toLowerCase();
  return state.products.filter((product) => {
    const categoryMatch = state.selectedCategory === "All" || product.category === state.selectedCategory;
    const searchMatch =
      normalized === "" ||
      product.name.toLowerCase().includes(normalized) ||
      product.category.toLowerCase().includes(normalized) ||
      product.description.toLowerCase().includes(normalized);
    return categoryMatch && searchMatch;
  });
}

function addToCart(product) {
  state.cart.push(product);
  state.activePaymentIntent = null;
  saveCart();
  renderCart();
}

function removeFromCart(productId) {
  const index = state.cart.findIndex((item) => item.id === productId);
  if (index >= 0) {
    state.cart.splice(index, 1);
    state.activePaymentIntent = null;
    saveCart();
    renderCart();
  }
}

function renderProducts() {
  const items = filteredProducts();
  resultSummary.textContent = `${items.length} products available`;
  metricProducts.textContent = String(state.products.length);
  productGrid.innerHTML = "";

  if (!items.length) {
    productGrid.innerHTML = '<p class="empty-state">No products matched your current search.</p>';
    return;
  }

  items.forEach((product) => {
    const article = document.createElement("article");
    article.className = "product-card";
    article.innerHTML = `
      <div class="product-visual" style="background:${product.accent_color}">
        ${productVisual(product)}
      </div>
      <div class="product-copy">
        <div class="product-meta">
          <span class="badge">${product.badge}</span>
          <span>${product.category}</span>
        </div>
        <h3>${product.name}</h3>
        <p>${product.description}</p>
        <div class="swatches">
          ${product.colors.map((color) => `<span>${color}</span>`).join("")}
        </div>
        <div class="sizes">
          ${product.sizes.map((size) => `<span>${size}</span>`).join("")}
        </div>
        <div class="price-row">
          <strong>${formatPrice(product.price)}</strong>
          <small>${formatPrice(product.compare_at_price)}</small>
        </div>
        <div class="card-footer">
          <span>Stock ${product.inventory}</span>
          <span>★ ${product.rating.toFixed(1)}</span>
        </div>
      </div>
    `;
    const button = document.createElement("button");
    button.type = "button";
    button.className = "primary-button full-width";
    button.textContent = "Add to Cart";
    button.addEventListener("click", () => addToCart(product));
    article.appendChild(button);
    productGrid.appendChild(article);
  });
}

function renderCart() {
  const items = groupedCartItems();
  cartItemsEl.innerHTML = "";

  if (!items.length) {
    cartItemsEl.innerHTML = '<p class="empty-state">Your cart is empty.</p>';
  } else {
    items.forEach((item) => {
      const article = document.createElement("article");
      article.className = "cart-item";
      article.innerHTML = `
        <div class="cart-icon" style="background:${item.accent_color}">
          ${item.image_url ? `<img src="${item.image_url}" alt="${item.name}" class="mini-image" />` : item.display_emoji}
        </div>
        <div class="cart-copy">
          <strong>${item.name}</strong>
          <span>${formatPrice(item.price)} x ${item.quantity}</span>
        </div>
      `;
      const removeButton = document.createElement("button");
      removeButton.type = "button";
      removeButton.className = "text-button";
      removeButton.textContent = "Remove";
      removeButton.addEventListener("click", () => removeFromCart(item.id));
      article.appendChild(removeButton);
      cartItemsEl.appendChild(article);
    });
  }

  const totals = calculateTotals();
  cartCount.textContent = String(state.cart.length);
  cartSubtotal.textContent = formatPrice(totals.subtotal);
  cartShipping.textContent = formatPrice(totals.shipping);
  cartTotal.textContent = formatPrice(totals.total);
}

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (state.token) {
    headers.Authorization = `Bearer ${state.token}`;
  }

  const response = await fetch(path, { ...options, headers });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || "Request failed");
  }
  return data;
}

async function requestAssistantReply(prompt) {
  const assistantEndpoints = [];

  if (LOCAL_ASSISTANT_HOSTS.has(window.location.hostname)) {
    assistantEndpoints.push({
      url: N8N_WEBHOOK_URL,
      options: {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      },
    });
  }

  assistantEndpoints.push({
    url: "/api/assistant",
    options: {
      method: "POST",
      body: JSON.stringify({ prompt }),
    },
    useApiHelper: true,
  });

  let lastError = new Error("Assistant request failed");

  for (const endpoint of assistantEndpoints) {
    try {
      const data = endpoint.useApiHelper ? await api(endpoint.url, endpoint.options) : await fetch(endpoint.url, endpoint.options).then(async (response) => {
        const payload = await response.json().catch(() => ({}));
        if (!response.ok) {
          throw new Error(payload.detail || payload.message || "Assistant request failed");
        }
        return payload;
      });

      if (typeof data.reply === "string" && data.reply.trim()) {
        return data.reply.trim();
      }

      throw new Error("Assistant response was empty");
    } catch (error) {
      lastError = error instanceof Error ? error : new Error("Assistant request failed");
    }
  }

  throw lastError;
}

function orderTimeline(order) {
  return order.tracking_history
    .map(
      (entry) =>
        `<li><strong>${entry.status}</strong> <span>${new Date(entry.timestamp).toLocaleString()}</span><p>${entry.message}</p></li>`
    )
    .join("");
}

async function loadOrders() {
  if (!state.user) {
    ordersList.innerHTML = '<p class="empty-state">Login to view order history.</p>';
    metricOrders.textContent = "0";
    return;
  }

  const data = await api("/api/orders");
  state.orders = data.orders;
  metricOrders.textContent = String(state.orders.length);

  if (!state.orders.length) {
    ordersList.innerHTML = '<p class="empty-state">No orders yet. Your completed checkouts will appear here.</p>';
    return;
  }

  ordersList.innerHTML = "";
  state.orders.forEach((order) => {
    const card = document.createElement("article");
    card.className = "order-card";
    card.innerHTML = `
      <strong>${order.order_number}</strong>
      <span>${new Date(order.created_at).toLocaleString()}</span>
      <span>Payment: ${order.payment_status}</span>
      <span>Tracking: ${order.tracking_status}</span>
      <span>${formatPrice(order.total)}</span>
      <p>${order.items.map((item) => `${item.product_name} x${item.quantity}`).join(", ")}</p>
      <ul class="timeline">${orderTimeline(order)}</ul>
    `;
    ordersList.appendChild(card);
  });
}

async function loadConfig() {
  const data = await api("/api/config");
  state.config = data;
  adminHint.textContent = `Default admin login: ${data.default_admin_email}. Change the password before release.`;
  renderTelegramConfig();
}

function renderTelegramConfig() {
  const username = state.config.telegram_bot_username?.trim();
  const webhookUrl = state.config.telegram_webhook_url?.trim();
  const lastChatId = state.config.telegram_last_chat_id?.trim();

  if (!state.config.telegram_enabled) {
    telegramAdminSummary.textContent = "Telegram bot token is not configured yet. Add TELEGRAM_BOT_TOKEN in the server env first.";
    telegramWebhookUrl.textContent = "Webhook URL will appear after PUBLIC_BASE_URL and bot token are configured.";
    telegramOpenBot.classList.add("hidden");
    telegramOpenBot.href = "#";
    telegramTestMessage.placeholder = "Configure Telegram first.";
    return;
  }

  telegramAdminSummary.textContent = username
    ? `Bot is configured as @${username}. Use the button below to register the webhook with Telegram.`
    : "Telegram bot token is configured. Add TELEGRAM_BOT_USERNAME if you want the bot link shown here.";
  telegramWebhookUrl.textContent = webhookUrl
    ? `Webhook URL: ${webhookUrl}${lastChatId ? ` | Last chat: ${lastChatId}` : ""}`
    : "Set PUBLIC_BASE_URL to your live HTTPS site before running webhook setup.";
  telegramTestMessage.placeholder = lastChatId
    ? "Send a test message to the latest Telegram chat..."
    : "Message the bot once, then send a test message from here.";

  if (username) {
    telegramOpenBot.href = `https://t.me/${username}`;
    telegramOpenBot.classList.remove("hidden");
  } else {
    telegramOpenBot.classList.add("hidden");
    telegramOpenBot.href = "#";
  }
}

async function loadProducts() {
  state.products = await api("/api/products");
  renderProducts();
}

async function loadCategories() {
  state.categories = await api("/api/categories");
  renderCategories();
}

async function refreshSession() {
  if (!state.token) {
    state.user = null;
    updateAuthUi();
    await loadOrders();
    return;
  }

  try {
    const data = await api("/api/me");
    state.user = data.user;
  } catch (error) {
    state.token = "";
    state.user = null;
    localStorage.removeItem(STORAGE_KEYS.token);
  }

  updateAuthUi();
  if (state.user) {
    document.getElementById("checkout-name").value = state.user.full_name;
  }
  await loadOrders();
  if (state.user?.role === "admin") {
    await Promise.all([loadAdminStats(), loadAdminProducts(), loadAdminOrders()]);
  }
}

function resetStripeUi() {
  if (state.paymentElement) {
    state.paymentElement.unmount();
    state.paymentElement = null;
  }
  state.elements = null;
  state.activePaymentIntent = null;
  paymentElementContainer.innerHTML = "";
}

async function loadStripeScript() {
  if (!state.config.stripe_enabled || window.Stripe) {
    return;
  }
  await new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = "https://js.stripe.com/v3/";
    script.onload = resolve;
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

async function ensureStripeElements() {
  if (checkoutPayment.value !== "Stripe Card") {
    stripePanel.classList.add("hidden");
    return;
  }

  stripePanel.classList.remove("hidden");
  if (!state.config.stripe_enabled) {
    stripeNote.textContent = "Stripe keys are not configured on the server yet. Use COD or Bank Transfer for now.";
    return;
  }

  stripeNote.textContent = "Card details are securely collected by Stripe.";
  await loadStripeScript();
  if (!state.stripe) {
    state.stripe = window.Stripe(state.config.stripe_publishable_key);
  }

  if (state.user && groupedCartItems().length) {
    await getOrCreatePaymentIntent();
  }
}

async function getOrCreatePaymentIntent() {
  const items = groupedCartItems().map((item) => ({
    product_id: item.id,
    quantity: item.quantity,
  }));
  const signature = JSON.stringify(items);
  if (state.activePaymentIntent?.signature === signature) {
    return state.activePaymentIntent;
  }

  const data = await api("/api/payments/intent", {
    method: "POST",
    body: JSON.stringify({ items, currency: "jpy" }),
  });
  state.activePaymentIntent = { ...data, signature };
  state.elements = state.stripe.elements({ clientSecret: data.client_secret });
  state.paymentElement = state.elements.create("payment");
  paymentElementContainer.innerHTML = "";
  state.paymentElement.mount("#payment-element");
  return state.activePaymentIntent;
}

function productFormPayload() {
  return {
    sku: document.getElementById("product-sku").value.trim(),
    name: document.getElementById("product-name").value.trim(),
    category: document.getElementById("product-category").value.trim(),
    description: document.getElementById("product-description").value.trim(),
    price: Number(document.getElementById("product-price").value),
    compare_at_price: Number(document.getElementById("product-compare-price").value),
    badge: document.getElementById("product-badge").value.trim(),
    inventory: Number(document.getElementById("product-inventory").value),
    rating: Number(document.getElementById("product-rating").value),
    display_emoji: document.getElementById("product-emoji").value.trim(),
    accent_color: document.getElementById("product-accent").value.trim(),
    sizes: parseCsv(document.getElementById("product-sizes").value),
    colors: parseCsv(document.getElementById("product-colors").value),
    image_url: document.getElementById("product-image-url").value.trim(),
  };
}

function fillProductForm(product = null) {
  document.getElementById("product-id").value = product?.id || "";
  document.getElementById("product-sku").value = product?.sku || "";
  document.getElementById("product-name").value = product?.name || "";
  document.getElementById("product-category").value = product?.category || "";
  document.getElementById("product-description").value = product?.description || "";
  document.getElementById("product-price").value = product?.price || "";
  document.getElementById("product-compare-price").value = product?.compare_at_price || "";
  document.getElementById("product-badge").value = product?.badge || "";
  document.getElementById("product-inventory").value = product?.inventory || "";
  document.getElementById("product-rating").value = product?.rating || "";
  document.getElementById("product-emoji").value = product?.display_emoji || "";
  document.getElementById("product-accent").value = product?.accent_color || "#d86a7f";
  document.getElementById("product-sizes").value = product?.sizes?.join(", ") || "";
  document.getElementById("product-colors").value = product?.colors?.join(", ") || "";
  document.getElementById("product-image-url").value = product?.image_url || "";
  productStatus.textContent = "";
}

async function loadAdminStats() {
  const data = await api("/api/admin/stats");
  adminStats.textContent = `${data.products} products, ${data.orders} orders, ${formatPrice(data.revenue)} revenue`;
}

async function loadAdminProducts() {
  const data = await api("/api/admin/products");
  state.adminProducts = data.products;
  adminProductList.innerHTML = "";

  state.adminProducts.forEach((product) => {
    const row = document.createElement("article");
    row.className = "admin-card";
    row.innerHTML = `
      <div>
        <strong>${product.name}</strong>
        <span>${product.sku} • ${product.category}</span>
      </div>
      <div class="admin-row-actions">
        <button type="button" class="ghost-button">Edit</button>
        <button type="button" class="danger-button">Delete</button>
      </div>
    `;
    const [editButton, deleteButton] = row.querySelectorAll("button");
    editButton.addEventListener("click", () => {
      fillProductForm(product);
      productForm.scrollIntoView({ behavior: "smooth", block: "start" });
    });
    deleteButton.addEventListener("click", async () => {
      if (!window.confirm(`Delete ${product.name}?`)) {
        return;
      }
      await api(`/api/admin/products/${product.id}`, { method: "DELETE" });
      await Promise.all([loadAdminProducts(), loadProducts(), loadCategories(), loadAdminStats()]);
    });
    adminProductList.appendChild(row);
  });
}

async function loadAdminOrders() {
  const data = await api("/api/admin/orders");
  state.adminOrders = data.orders;
  adminOrderList.innerHTML = "";

  state.adminOrders.forEach((order) => {
    const card = document.createElement("article");
    card.className = "admin-order-card";
    card.innerHTML = `
      <strong>${order.order_number}</strong>
      <span>${order.customer_name} • ${formatPrice(order.total)}</span>
      <span>${order.payment_method} / ${order.payment_status}</span>
      <input type="text" class="order-status-input" value="${order.status}" placeholder="Order status" />
      <select class="tracking-select">
        ${state.config.tracking_steps
          .map((step) => `<option value="${step}" ${step === order.tracking_status ? "selected" : ""}>${step}</option>`)
          .join("")}
      </select>
      <input type="text" class="tracking-number-input" value="${order.tracking_number || ""}" placeholder="Tracking number" />
      <input type="text" class="tracking-note-input" placeholder="Tracking note" />
      <button type="button" class="primary-button">Save Tracking</button>
    `;
    const button = card.querySelector("button");
    button.addEventListener("click", async () => {
      const status = card.querySelector(".order-status-input").value.trim();
      const trackingStatus = card.querySelector(".tracking-select").value;
      const trackingNumber = card.querySelector(".tracking-number-input").value.trim();
      const note = card.querySelector(".tracking-note-input").value.trim();
      await api(`/api/admin/orders/${order.id}`, {
        method: "PATCH",
        body: JSON.stringify({
          status,
          tracking_status: trackingStatus,
          tracking_number: trackingNumber,
          note,
        }),
      });
      adminOrderStatus.textContent = `${order.order_number} updated.`;
      await Promise.all([loadAdminOrders(), loadOrders(), loadAdminStats()]);
    });
    adminOrderList.appendChild(card);
  });
}

authModeToggle.addEventListener("click", () => {
  state.mode = state.mode === "login" ? "register" : "login";
  authStatus.textContent = "";
  updateAuthUi();
});

authForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  authStatus.textContent = "Working...";

  const payload =
    state.mode === "register"
      ? {
          full_name: authName.value.trim(),
          email: authEmail.value.trim(),
          password: authPassword.value,
        }
      : {
          email: authEmail.value.trim(),
          password: authPassword.value,
        };

  try {
    const data = await api(state.mode === "register" ? "/api/auth/register" : "/api/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    state.token = data.token;
    state.user = data.user;
    localStorage.setItem(STORAGE_KEYS.token, state.token);
    authStatus.textContent = state.mode === "register" ? "Account created successfully." : "Logged in successfully.";
    authForm.reset();
    state.mode = "login";
    updateAuthUi();
    await refreshSession();
  } catch (error) {
    authStatus.textContent = error.message;
  }
});

logoutButton.addEventListener("click", async () => {
  state.token = "";
  state.user = null;
  localStorage.removeItem(STORAGE_KEYS.token);
  resetStripeUi();
  authStatus.textContent = "Logged out.";
  updateAuthUi();
  await loadOrders();
});

deleteAccountButton.addEventListener("click", async () => {
  if (!window.confirm("Delete your account and order history from this starter app?")) {
    return;
  }
  try {
    await api("/api/me", { method: "DELETE" });
    state.token = "";
    state.user = null;
    localStorage.removeItem(STORAGE_KEYS.token);
    state.orders = [];
    updateAuthUi();
    await loadOrders();
    authStatus.textContent = "Account deleted.";
  } catch (error) {
    authStatus.textContent = error.message;
  }
});

checkoutToggle.addEventListener("click", async () => {
  checkoutPanel.classList.add("open");
  checkoutPanel.scrollIntoView({ behavior: "smooth", block: "start" });
  await ensureStripeElements();
});

closeCheckout.addEventListener("click", () => {
  checkoutPanel.classList.remove("open");
});

checkoutPayment.addEventListener("change", async () => {
  resetStripeUi();
  await ensureStripeElements();
});

checkoutForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!state.user) {
    checkoutStatus.textContent = "Checkout မတင်ခင် account ဝင်ထားဖို့လိုပါတယ်။";
    return;
  }

  const items = groupedCartItems().map((item) => ({
    product_id: item.id,
    quantity: item.quantity,
  }));
  if (!items.length) {
    checkoutStatus.textContent = "Cart is empty.";
    return;
  }

  checkoutStatus.textContent = "Placing order...";
  let paymentStatus = "Pending";
  let paymentProvider = "";
  let paymentIntentId = "";

  try {
    if (checkoutPayment.value === "Stripe Card") {
      if (!state.config.stripe_enabled) {
        throw new Error("Stripe is not configured on the server.");
      }
      await ensureStripeElements();
      const intent = await getOrCreatePaymentIntent();
      const result = await state.stripe.confirmPayment({
        elements: state.elements,
        redirect: "if_required",
      });
      if (result.error) {
        throw new Error(result.error.message);
      }
      paymentStatus = result.paymentIntent?.status || "processing";
      paymentProvider = "stripe";
      paymentIntentId = result.paymentIntent?.id || intent.payment_intent_id;
    }

    const data = await api("/api/orders", {
      method: "POST",
      body: JSON.stringify({
        customer_name: document.getElementById("checkout-name").value.trim(),
        phone: document.getElementById("checkout-phone").value.trim(),
        city: document.getElementById("checkout-city").value.trim(),
        payment_method: checkoutPayment.value,
        payment_status: paymentStatus,
        payment_provider: paymentProvider,
        payment_intent_id: paymentIntentId,
        address_line: document.getElementById("checkout-address").value.trim(),
        notes: document.getElementById("checkout-notes").value.trim(),
        items,
      }),
    });
    checkoutStatus.textContent = `${data.order.order_number} order ကိုအောင်မြင်စွာတင်ပြီးပါပြီ။`;
    state.cart = [];
    saveCart();
    renderCart();
    checkoutForm.reset();
    resetStripeUi();
    await Promise.all([loadProducts(), loadOrders()]);
    checkoutPayment.value = "Cash on Delivery";
    stripePanel.classList.add("hidden");
  } catch (error) {
    checkoutStatus.textContent = error.message;
  }
});

assistantSubmit.addEventListener("click", async () => {
  const prompt = assistantInput.value.trim();
  if (!prompt) {
    assistantResponse.textContent = "Type a question first.";
    return;
  }

  assistantResponse.textContent = "Thinking...";
  try {
    assistantResponse.textContent = await requestAssistantReply(prompt);
  } catch (error) {
    assistantResponse.textContent = error.message;
  }
});

searchInput.addEventListener("input", () => renderProducts());

openCartButton.addEventListener("click", () => {
  cartItemsEl.scrollIntoView({ behavior: "smooth", block: "start" });
});

scrollAdmin.addEventListener("click", () => {
  adminPanel.scrollIntoView({ behavior: "smooth", block: "start" });
});

telegramSetupButton.addEventListener("click", async () => {
  telegramStatus.textContent = "Setting Telegram webhook...";
  try {
    const data = await api("/api/telegram/set-webhook", {
      method: "POST",
      body: JSON.stringify({}),
    });
    state.config.telegram_webhook_url = data.webhook_url || state.config.telegram_webhook_url;
    renderTelegramConfig();
    telegramStatus.textContent = data.ok
      ? `Webhook connected: ${data.webhook_url}`
      : "Telegram webhook request completed, but Telegram did not confirm success.";
  } catch (error) {
    telegramStatus.textContent = error.message;
  }
});

telegramTestButton.addEventListener("click", async () => {
  const message = telegramTestMessage.value.trim();
  if (!message) {
    telegramStatus.textContent = "Type a Telegram test message first.";
    return;
  }

  telegramStatus.textContent = "Sending Telegram test message...";
  try {
    const data = await api("/api/telegram/test-message", {
      method: "POST",
      body: JSON.stringify({ message }),
    });
    telegramStatus.textContent = data.ok
      ? `Telegram test message sent to chat ${data.chat_id}.`
      : "Telegram accepted the request, but did not confirm success.";
    telegramTestMessage.value = "";
  } catch (error) {
    telegramStatus.textContent = error.message;
  }
});

clearProductForm.addEventListener("click", () => fillProductForm());

uploadImageButton.addEventListener("click", async () => {
  const file = productImageFile.files?.[0];
  if (!file) {
    productStatus.textContent = "Choose an image file first.";
    return;
  }
  const reader = new FileReader();
  reader.onload = async () => {
    try {
      productStatus.textContent = "Uploading image...";
      const data = await api("/api/admin/uploads", {
        method: "POST",
        body: JSON.stringify({
          filename: file.name,
          content_base64: reader.result,
        }),
      });
      document.getElementById("product-image-url").value = data.url;
      productStatus.textContent = "Image uploaded successfully.";
    } catch (error) {
      productStatus.textContent = error.message;
    }
  };
  reader.readAsDataURL(file);
});

productForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const productId = document.getElementById("product-id").value;
  try {
    productStatus.textContent = "Saving product...";
    await api(productId ? `/api/admin/products/${productId}` : "/api/admin/products", {
      method: productId ? "PUT" : "POST",
      body: JSON.stringify(productFormPayload()),
    });
    productStatus.textContent = "Product saved.";
    fillProductForm();
    await Promise.all([loadProducts(), loadCategories(), loadAdminProducts(), loadAdminStats()]);
  } catch (error) {
    productStatus.textContent = error.message;
  }
});

async function init() {
  loadCart();
  renderCart();
  updateAuthUi();

  await loadConfig();
  await Promise.all([loadProducts(), loadCategories(), refreshSession()]);
}

init().catch((error) => {
  resultSummary.textContent = error.message;
});
