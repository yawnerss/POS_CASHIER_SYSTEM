import json
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, render_template_string, abort
from flask_cors import CORS
from supabase import create_client, Client

# ---------------------------
# Configuration
# ---------------------------
SUPABASE_URL = "https://oeydqwwgyfecqiobuvav.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9leWRxd3dneWZlY3Fpb2J1dmF2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTI4ODU5NSwiZXhwIjoyMDkwODY0NTk1fQ.iH64lRrt7Hfr7qIGqcu_7UgehTtKDFIN1GhvDLcbgC8"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

app = Flask(__name__)
app.secret_key = "change-this-in-production"
CORS(app)

THEME_FILE = "theme.json"
ALLOWED_ADMIN_IPS = ["192.168.8.39"]

PH_TZ_OFFSET = timedelta(hours=8)

def ph_now():
    return datetime.utcnow() + PH_TZ_OFFSET

def get_current_theme():
    if os.path.exists(THEME_FILE):
        try:
            with open(THEME_FILE, "r") as f:
                return json.load(f).get("theme", "light")
        except:
            return "light"
    return "light"

def set_theme(theme_name):
    with open(THEME_FILE, "w") as f:
        json.dump({"theme": theme_name}, f)

def admin_ip_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.remote_addr not in ALLOWED_ADMIN_IPS and request.remote_addr != "127.0.0.1":
            abort(403)
        return f(*args, **kwargs)
    return decorated

# ---------------------------
# Error handlers
# ---------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template_string("""
    <!DOCTYPE html>
    <html><head><title>404 - Not Found</title><meta name="viewport" content="width=device-width,initial-scale=1"><script src="https://cdn.tailwindcss.com"></script></head>
    <body class="bg-gray-100 flex items-center justify-center h-screen"><div class="text-center"><h1 class="text-6xl font-bold text-primary">404</h1><p class="text-xl mt-2">Page not found</p><a href="/" class="mt-4 inline-block bg-primary text-white px-4 py-2 rounded-lg">Go Home</a></div></body></html>
    """), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template_string("""
    <!DOCTYPE html>
    <html><head><title>403 - Forbidden</title><meta name="viewport" content="width=device-width,initial-scale=1"><script src="https://cdn.tailwindcss.com"></script></head>
    <body class="bg-gray-100 flex items-center justify-center h-screen"><div class="text-center"><h1 class="text-6xl font-bold text-error">403</h1><p class="text-xl mt-2">Access denied.</p><a href="/" class="mt-4 inline-block bg-primary text-white px-4 py-2 rounded-lg">Return to POS</a></div></body></html>
    """), 403

# ---------------------------
# Health Check Endpoint
# ---------------------------
@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        supabase.table('product').select('id').limit(1).execute()
        return jsonify({"status": "ok", "supabase": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "error", "supabase": "disconnected", "message": str(e)}), 500

# ---------------------------
# POS HTML (full version)
# ---------------------------
@app.route('/')
def index():
    pos_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <title>Descalzo Store POS</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200">
  <style id="theme-style">
    /* Default light theme */
    :root {
      --primary: #004ac6;
      --primary-container: #2563eb;
      --secondary: #006c49;
      --surface: #f8f9ff;
      --surface-container-lowest: #ffffff;
      --surface-container-low: #eff4ff;
      --surface-container: #e5eeff;
      --surface-container-high: #dce9ff;
      --surface-container-highest: #d3e4fe;
      --on-surface: #0b1c30;
      --on-surface-variant: #434655;
      --outline-variant: #c3c6d7;
    }
    body { background-color: var(--surface); color: var(--on-surface); font-family: 'Inter', sans-serif; transition: background-color 0.2s, color 0.2s; }
    .tap-scale:active { transform: scale(0.96); transition: transform 0.1s; }
    .smooth-scroll { -webkit-overflow-scrolling: touch; }
    @keyframes rhythmic-breathe { 0%,100% { transform: scale(1); opacity:0.8; filter:blur(40px); } 50% { transform: scale(1.15); opacity:1; filter:blur(60px); } }
    @keyframes soft-float { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
    @keyframes icon-pulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.03); } }
    @keyframes fadeInUp { from { opacity:0; transform: translateY(20px); } to { opacity:1; transform: translateY(0); } }
    .animate-breathe { animation: rhythmic-breathe 4s ease-in-out infinite; }
    .animate-float { animation: soft-float 3s ease-in-out infinite; }
    .animate-icon-pulse { animation: icon-pulse 2s ease-in-out infinite; }
    .fade-in-up { animation: fadeInUp 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
    .mesh-gradient { background: radial-gradient(at 0% 0%, #f0f4ff 0%, transparent 50%), radial-gradient(at 100% 0%, #e8eaff 0%, transparent 50%), radial-gradient(at 100% 100%, #eff4ff 0%, transparent 50%), radial-gradient(at 0% 100%, #f8f9ff 0%, transparent 50%), #ffffff; }
  </style>
  <style>
    @media (min-width: 1024px) {
      .cart-fixed { position: fixed; right: 20px; top: 80px; width: 380px; max-height: calc(100vh - 100px); overflow-y: auto; z-index: 40; border-radius: 0.75rem; }
      .products-container { margin-right: 420px; }
    }
    @media (max-width: 1023px) {
      .cart-fixed { position: fixed; bottom: 0; left: 0; right: 0; max-height: 60vh; overflow-y: auto; z-index: 40; border-radius: 1rem 1rem 0 0; box-shadow: 0 -4px 12px rgba(0,0,0,0.1); }
      .products-container { margin-bottom: 60vh; padding-bottom: 1rem; }
    }
  </style>
  <script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            primary: 'var(--primary)',
            'primary-container': 'var(--primary-container)',
            secondary: 'var(--secondary)',
            surface: 'var(--surface)',
            'surface-container-lowest': 'var(--surface-container-lowest)',
            'surface-container-low': 'var(--surface-container-low)',
            'surface-container': 'var(--surface-container)',
            'surface-container-high': 'var(--surface-container-high)',
            'surface-container-highest': 'var(--surface-container-highest)',
            'on-surface': 'var(--on-surface)',
            'on-surface-variant': 'var(--on-surface-variant)',
            'outline-variant': 'var(--outline-variant)'
          },
          borderRadius: { xl: '0.75rem' }
        }
      }
    }
    async function loadTheme() {
      const res = await fetch('/api/theme');
      const data = await res.json();
      applyTheme(data.theme);
    }
    function applyTheme(theme) {
      const style = document.getElementById('theme-style');
      if (theme === 'dark') {
        style.innerHTML = `:root {
          --primary: #a4c9ff;
          --primary-container: #60a5fa;
          --secondary: #bcc7de;
          --surface: #0b1326;
          --surface-container-lowest: #060e20;
          --surface-container-low: #131b2e;
          --surface-container: #171f33;
          --surface-container-high: #222a3d;
          --surface-container-highest: #2d3449;
          --on-surface: #dae2fd;
          --on-surface-variant: #c1c7d3;
          --outline-variant: #414751;
        } body { background-color: var(--surface); color: var(--on-surface); }`;
      } else if (theme === 'blue') {
        style.innerHTML = `:root {
          --primary: #1e3a8a;
          --primary-container: #2563eb;
          --secondary: #0284c7;
          --surface: #eef2ff;
          --surface-container-lowest: #ffffff;
          --surface-container-low: #eff4ff;
          --surface-container: #e5eeff;
          --surface-container-high: #dce9ff;
          --surface-container-highest: #d3e4fe;
          --on-surface: #0f172a;
          --on-surface-variant: #475569;
          --outline-variant: #cbd5e1;
        } body { background-color: var(--surface); color: var(--on-surface); }`;
      } else if (theme === 'black') {
        style.innerHTML = `:root {
          --primary: #f97316;
          --primary-container: #ea580c;
          --secondary: #84cc16;
          --surface: #000000;
          --surface-container-lowest: #1a1a1a;
          --surface-container-low: #2a2a2a;
          --surface-container: #333333;
          --surface-container-high: #3d3d3d;
          --surface-container-highest: #4a4a4a;
          --on-surface: #e5e5e5;
          --on-surface-variant: #a3a3a3;
          --outline-variant: #404040;
        } body { background-color: var(--surface); color: var(--on-surface); }`;
      } else {
        style.innerHTML = `:root {
          --primary: #004ac6;
          --primary-container: #2563eb;
          --secondary: #006c49;
          --surface: #f8f9ff;
          --surface-container-lowest: #ffffff;
          --surface-container-low: #eff4ff;
          --surface-container: #e5eeff;
          --surface-container-high: #dce9ff;
          --surface-container-highest: #d3e4fe;
          --on-surface: #0b1c30;
          --on-surface-variant: #434655;
          --outline-variant: #c3c6d7;
        } body { background-color: var(--surface); color: var(--on-surface); }`;
      }
    }
    loadTheme();
  </script>
</head>
<body class="antialiased">
  <div id="loadingScreen" class="fixed inset-0 z-[200] mesh-gradient flex items-center justify-center transition-opacity duration-700 ease-out">
    <div class="relative flex flex-col items-center gap-12 z-10">
      <div class="relative flex items-center justify-center w-48 h-48 fade-in-up" style="animation-delay: 0.1s;"><div class="absolute w-32 h-32 rounded-full bg-primary opacity-20 blur-3xl animate-breathe"></div><div class="absolute w-20 h-20 rounded-full bg-primary-container opacity-10 blur-xl animate-float"></div><div class="relative w-32 h-32 flex items-center justify-center animate-icon-pulse backdrop-blur-[2px]"><img alt="Descalzo Store Loading" class="w-full h-full object-contain" src="https://lh3.googleusercontent.com/aida/ADBb0ugC4EUz1fjRvv2YjnrBdC70Wr4K0h4TrY4kWMYJZMvoa3AJDVHmwi052GgcVXI0HVnVrIRkAYNVC6_duU4zmueF9USa5KnMk8KJ7lxpuA158aCkr8Cqwo4TuD1NiK_zJz5ARe2s8bUDHZKMhgMSnozrmwyMQBurclpVHB2WQ91FNZcsbFKQv_guZmRNdjyzwGWwxmw_-46CSduFdZ3Pdo9MJmqIZCNFFm46AxZKWe49kiRcLkvBUiU2extG"/></div></div>
      <div class="flex flex-col items-center fade-in-up" style="animation-delay: 0.4s;"><h1 class="font-headline-lg text-headline-lg text-on-surface tracking-[0.6em] uppercase font-bold opacity-90">descalzo store</h1><div class="mt-8 w-1 h-1 rounded-full bg-primary-container opacity-60"></div></div>
    </div>
    <div class="fixed inset-0 pointer-events-none"><div class="absolute top-[-15%] right-[-10%] w-[50%] h-[50%] rounded-full bg-primary-container/10 blur-[140px]"></div><div class="absolute bottom-[-15%] left-[-10%] w-[50%] h-[50%] rounded-full bg-secondary-container/10 blur-[140px]"></div></div>
  </div>
  <div id="posContent" class="opacity-0 transition-opacity duration-700" style="display: none;">
    <header class="fixed top-0 w-full z-50 bg-surface-container-lowest/90 backdrop-blur-sm shadow-sm flex justify-between items-center px-4 h-16 border-b border-outline-variant">
      <div class="flex items-center gap-2"><div class="w-8 h-8 rounded-full bg-primary-container flex items-center justify-center"><span class="material-symbols-outlined text-on-primary-container text-xl">point_of_sale</span></div><h1 class="text-lg md:text-2xl font-bold text-primary whitespace-nowrap">Descalzo Store</h1></div>
      <div class="flex items-center gap-2"><button id="manageProductsBtn" class="bg-surface-container-high px-2 md:px-3 py-1.5 rounded-full text-xs md:text-sm font-medium"><span class="material-symbols-outlined text-sm">inventory</span> Manage</button><span class="material-symbols-outlined text-primary">account_circle</span></div>
    </header>
    <main class="pt-16">
      <div class="products-container px-3 md:px-4 pb-24">
        <div class="mb-3 relative"><input type="text" id="searchInput" placeholder="Search items..." class="w-full pl-10 pr-3 py-2.5 bg-surface-container-lowest border border-outline-variant rounded-xl text-sm"><span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-base">search</span></div>
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3" id="productsGrid">Loading products...</div>
      </div>
      <div class="cart-fixed bg-surface-container-lowest border border-outline-variant shadow-lg">
        <div class="p-3 border-b bg-surface-container-low/30"><h2 class="text-base md:text-lg font-bold">Current Order</h2></div>
        <div id="cartItemsContainer" class="overflow-y-auto smooth-scroll max-h-[200px] md:max-h-[280px] divide-y divide-outline-variant p-1">Your cart is empty</div>
        <div class="p-2 border-t flex flex-wrap gap-1"><button id="discountChip" class="bg-surface-container-high px-2 py-1 rounded-full text-xs">Add Discount</button><button id="taxExemptChip" class="bg-surface-container-high px-2 py-1 rounded-full text-xs">Tax Exempt</button><button id="clearCartBtn" class="bg-error/10 text-error px-2 py-1 rounded-full text-xs">Clear</button></div>
        <div class="p-3 space-y-1 bg-surface-container-low/40 text-sm"><div class="flex justify-between"><span>Subtotal</span><span id="subtotalAmount">₱0</span></div><div class="flex justify-between"><span>Tax (8%)</span><span id="taxAmount">₱0</span></div><div class="flex justify-between"><span>Discount</span><span id="discountAmountDisplay">-₱0</span></div><div class="pt-1 border-t flex justify-between items-baseline"><span class="font-bold">TOTAL</span><span id="grandTotal" class="text-xl font-bold text-primary">₱0</span></div></div>
        <div class="p-3 border-t bg-surface-container-low/20"><label class="block text-xs font-medium mb-1">Amount Received (₱)</label><input type="number" id="cashGiven" step="1" min="0" class="w-full px-2 py-2 rounded-lg border border-outline-variant bg-surface-container-lowest text-sm" placeholder="Enter whole peso"><div id="changeDueArea" class="mt-2 hidden bg-surface-container-high rounded-lg p-1 text-center"><p class="text-xs">Change Due</p><p id="changeDue" class="text-lg font-bold text-secondary">₱0</p></div><div id="insufficientError" class="mt-1 text-error text-xs text-center hidden">Amount must be at least total</div><button id="completePaymentBtn" class="w-full mt-2 bg-secondary text-on-primary py-2 rounded-lg font-bold text-sm">Complete Payment</button></div>
      </div>
    </main>
    <div id="successModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 hidden items-center justify-center p-4"><div class="bg-surface-container-lowest max-w-md w-full rounded-2xl text-center p-6"><div class="w-20 h-20 bg-secondary-container rounded-full flex items-center justify-center mx-auto mb-4"><span class="material-symbols-outlined text-5xl text-secondary">check_circle</span></div><h2 class="text-2xl font-bold">Payment Successful!</h2><p class="text-sm">Transaction #<span id="receiptId"></span> completed</p><div class="bg-surface-container-high rounded-xl p-3 my-4 text-left text-sm"><div id="receiptItems"></div><div class="flex justify-between mt-2 pt-2 border-t"><span class="font-bold">Cash Given</span><span id="receiptCashGiven"></span></div><div class="flex justify-between"><span class="font-bold">Change</span><span id="receiptChange"></span></div><div class="flex justify-between mt-2 pt-2 border-t font-bold"><span>Total Paid</span><span id="receiptTotal"></span></div></div><button id="newTransactionBtn" class="w-full bg-primary text-on-primary py-2 rounded-xl font-bold">New Transaction</button></div></div>
    <div id="productModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 hidden items-center justify-center p-4"><div class="bg-surface-container-lowest rounded-2xl max-w-2xl w-full max-h-[85vh] overflow-y-auto shadow-2xl"><div class="p-4 border-b flex justify-between sticky top-0 bg-surface-container-lowest"><h3 class="text-lg font-bold">Manage Products</h3><button id="closeProductModal" class="p-1 rounded-full"><span class="material-symbols-outlined">close</span></button></div><div class="p-4"><div class="bg-surface-container-high rounded-xl p-3 mb-5"><h4 class="font-bold mb-2">Add New Product</h4><div class="grid grid-cols-1 sm:grid-cols-3 gap-2"><input type="text" id="newProductId" placeholder="ID" class="px-2 py-2 rounded-lg border border-outline-variant bg-surface-container-lowest text-sm"><input type="text" id="newProductName" placeholder="Name" class="px-2 py-2 rounded-lg border border-outline-variant bg-surface-container-lowest text-sm"><input type="number" id="newProductPrice" placeholder="Price (₱)" step="1" class="px-2 py-2 rounded-lg border border-outline-variant bg-surface-container-lowest text-sm"></div><button id="addProductBtn" class="mt-2 bg-primary text-on-primary px-3 py-1.5 rounded-lg text-sm">Add Product</button></div><h4 class="font-bold mb-2">Existing Products</h4><div id="manageProductsList" class="space-y-2 max-h-[350px] overflow-y-auto"></div></div></div></div>
  </div>
  <script>
    let products = [], cart = [], taxRate = 8, discountAmount = 0, isTaxExempt = false, searchQuery = '';
    const productsGrid = document.getElementById('productsGrid');
    const cartContainer = document.getElementById('cartItemsContainer');
    const subtotalSpan = document.getElementById('subtotalAmount');
    const taxSpan = document.getElementById('taxAmount');
    const discountSpan = document.getElementById('discountAmountDisplay');
    const grandTotalSpan = document.getElementById('grandTotal');
    const cashGivenInput = document.getElementById('cashGiven');
    const changeDueArea = document.getElementById('changeDueArea');
    const changeDueSpan = document.getElementById('changeDue');
    const insufficientError = document.getElementById('insufficientError');
    const completePaymentBtn = document.getElementById('completePaymentBtn');
    const loadingScreen = document.getElementById('loadingScreen');
    const posContent = document.getElementById('posContent');
    const taxExemptChip = document.getElementById('taxExemptChip');

    function saveCartToLocalStorage() {
        localStorage.setItem('pos_cart', JSON.stringify(cart));
        localStorage.setItem('pos_discount', discountAmount);
        localStorage.setItem('pos_taxExempt', isTaxExempt);
    }
    function loadCartFromLocalStorage() {
        const savedCart = localStorage.getItem('pos_cart');
        const savedDiscount = localStorage.getItem('pos_discount');
        const savedTaxExempt = localStorage.getItem('pos_taxExempt');
        if (savedCart) { try { cart = JSON.parse(savedCart); } catch(e) { cart = []; } }
        if (savedDiscount && !isNaN(parseInt(savedDiscount))) discountAmount = parseInt(savedDiscount);
        if (savedTaxExempt === 'true') isTaxExempt = true;
        if (isTaxExempt && taxExemptChip) taxExemptChip.classList.add('bg-primary-container');
        updateCartUI();
    }
    function clearLocalStorageCart() {
        localStorage.removeItem('pos_cart');
        localStorage.removeItem('pos_discount');
        localStorage.removeItem('pos_taxExempt');
        cart = [];
        discountAmount = 0;
        isTaxExempt = false;
        if (taxExemptChip) taxExemptChip.classList.remove('bg-primary-container');
        updateCartUI();
    }

    async function fetchProducts() {
      try {
        const res = await fetch('/api/products');
        const data = await res.json();
        products = data.map(p => ({ id: String(p.id), name: p.name, price: Math.round(parseFloat(p.price)) }));
        renderProducts();
        if (loadingScreen && posContent) {
          loadingScreen.style.opacity = '0';
          setTimeout(() => { loadingScreen.style.display = 'none'; posContent.style.display = 'block'; setTimeout(() => posContent.style.opacity = '1', 50); }, 700);
        }
        loadCartFromLocalStorage();
      } catch(e) { productsGrid.innerHTML = '<div class="col-span-full text-center py-10 text-error">Failed to load products.</div>'; if (loadingScreen) loadingScreen.style.display = 'none'; if (posContent) posContent.style.display = 'block'; }
    }
    function renderProducts() {
      let filtered = products.filter(p => p.name.toLowerCase().includes(searchQuery));
      if (!filtered.length) { productsGrid.innerHTML = '<div class="col-span-full text-center py-10">No products</div>'; return; }
      productsGrid.innerHTML = filtered.map(p => `<div onclick="addToCart('${p.id}')" class="bg-surface-container-lowest border rounded-lg p-2 cursor-pointer tap-scale"><div class="aspect-square bg-surface-container-high flex items-center justify-center text-3xl"><span class="material-symbols-outlined text-3xl">shopping_cart</span></div><p class="font-semibold text-sm mt-1 truncate">${escapeHtml(p.name)}</p><p class="text-primary font-bold text-sm">₱${p.price}</p></div>`).join('');
    }
    window.addToCart = function(id) {
      const p = products.find(x => x.id === id);
      if (!p) return;
      const existing = cart.find(i => i.id === id);
      if (existing) existing.quantity += 1;
      else cart.push({ id: p.id, name: p.name, price: p.price, quantity: 1 });
      updateCartUI();
      saveCartToLocalStorage();
      showToast(p.name + ' added');
    };
    function updateCartUI() {
      if (!cart.length) { cartContainer.innerHTML = '<div class="p-3 text-center text-sm">Cart empty</div>'; computeTotals(); return; }
      cartContainer.innerHTML = cart.map(item => `<div class="p-2 flex justify-between items-center"><div><b class="text-sm">${escapeHtml(item.name)}</b><div class="text-xs">₱${item.price} ea</div></div><div class="flex items-center gap-1"><button class="qty-decr w-6 h-6 flex items-center justify-center rounded-full" data-id="${item.id}">-</button><span class="w-5 text-center text-sm">${item.quantity}</span><button class="qty-incr w-6 h-6 flex items-center justify-center rounded-full" data-id="${item.id}">+</button><span class="font-bold w-14 text-right text-sm">₱${item.price * item.quantity}</span><button class="remove-item text-error" data-id="${item.id}"><span class="material-symbols-outlined text-sm">delete</span></button></div></div>`).join('');
      document.querySelectorAll('.qty-incr').forEach(btn => btn.onclick = () => changeQuantity(btn.dataset.id, 1));
      document.querySelectorAll('.qty-decr').forEach(btn => btn.onclick = () => changeQuantity(btn.dataset.id, -1));
      document.querySelectorAll('.remove-item').forEach(btn => btn.onclick = () => removeCartItem(btn.dataset.id));
      computeTotals();
    }
    function changeQuantity(id, delta) { let i = cart.find(x => x.id === id); if(i) { i.quantity += delta; if(i.quantity <= 0) cart = cart.filter(x => x.id !== id); updateCartUI(); saveCartToLocalStorage(); } }
    function removeCartItem(id) { cart = cart.filter(x => x.id !== id); updateCartUI(); saveCartToLocalStorage(); }
    function computeTotals() { const subtotal = cart.reduce((s,i)=>s + i.price * i.quantity,0); let tax = isTaxExempt ? 0 : Math.round(subtotal * taxRate / 100); const final = subtotal + tax - discountAmount; subtotalSpan.innerText = `₱${subtotal}`; taxSpan.innerText = `₱${tax}`; discountSpan.innerText = `-₱${discountAmount}`; grandTotalSpan.innerText = `₱${final}`; updateCashPreview(); }
    function showToast(msg) { let t=document.createElement('div'); t.className='fixed bottom-24 left-1/2 -translate-x-1/2 bg-inverse-surface text-inverse-on-surface px-3 py-2 rounded-full z-[100] text-xs shadow-lg'; t.innerText=msg; document.body.appendChild(t); setTimeout(()=>t.remove(),2000); }
    document.getElementById('discountChip').onclick = () => { let val=parseInt(prompt("Discount amount (₱):")); if(!isNaN(val) && val>=0) discountAmount=val; computeTotals(); saveCartToLocalStorage(); };
    document.getElementById('taxExemptChip').onclick = () => { isTaxExempt=!isTaxExempt; computeTotals(); saveCartToLocalStorage(); };
    document.getElementById('clearCartBtn').onclick = () => { if(confirm("Clear cart?")) { cart=[]; discountAmount=0; isTaxExempt=false; updateCartUI(); saveCartToLocalStorage(); } };
    function updateCashPreview() { const total = parseInt(grandTotalSpan.innerText.replace('₱','')); const cash = parseInt(cashGivenInput.value) || 0; if (cash >= total) { changeDueSpan.innerText = `₱${cash - total}`; changeDueArea.classList.remove('hidden'); insufficientError.classList.add('hidden'); } else { changeDueArea.classList.add('hidden'); insufficientError.classList.remove('hidden'); } }
    cashGivenInput.addEventListener('input', updateCashPreview);
    completePaymentBtn.onclick = async () => {
      const total = parseInt(grandTotalSpan.innerText.replace('₱',''));
      const cashGiven = parseInt(cashGivenInput.value);
      if (isNaN(cashGiven) || cashGiven < total) { showToast("Insufficient cash."); return; }
      const change = cashGiven - total;
      const subtotal = parseInt(subtotalSpan.innerText.replace('₱',''));
      const tax = parseInt(taxSpan.innerText.replace('₱',''));
      const final = total;
      const tid = 'MRT-' + Math.floor(Math.random()*100000);
      await fetch('/api/transaction', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ transactionId:tid, items:cart, subtotal, tax, total:final, method:'cash', cash_given:cashGiven, change_due:change }) });
      document.getElementById('receiptId').innerText = tid;
      document.getElementById('receiptItems').innerHTML = cart.map(i => `<div class="flex justify-between"><span>${escapeHtml(i.name)} x${i.quantity}</span><span>₱${i.price * i.quantity}</span></div>`).join('');
      document.getElementById('receiptCashGiven').innerText = `₱${cashGiven}`;
      document.getElementById('receiptChange').innerText = `₱${change}`;
      document.getElementById('receiptTotal').innerText = `₱${final}`;
      document.getElementById('successModal').classList.remove('hidden');
      cart = [];
      discountAmount = 0;
      isTaxExempt = false;
      updateCartUI();
      clearLocalStorageCart();
      cashGivenInput.value = '';
      changeDueArea.classList.add('hidden');
      insufficientError.classList.add('hidden');
    };
    document.getElementById('newTransactionBtn').onclick = () => {
      cart = [];
      discountAmount = 0;
      isTaxExempt = false;
      cashGivenInput.value = '';
      changeDueArea.classList.add('hidden');
      insufficientError.classList.add('hidden');
      updateCartUI();
      clearLocalStorageCart();
      document.getElementById('successModal').classList.add('hidden');
    };
    document.getElementById('searchInput').oninput = (e) => { searchQuery = e.target.value.toLowerCase(); renderProducts(); };
    document.getElementById('manageProductsBtn').onclick = () => { renderManageList(); document.getElementById('productModal').classList.remove('hidden'); };
    document.getElementById('closeProductModal').onclick = () => document.getElementById('productModal').classList.add('hidden');
    async function renderManageList() { const res = await fetch('/api/products'); const data = await res.json(); document.getElementById('manageProductsList').innerHTML = data.map(p => `<div class="flex justify-between items-center p-2 border border-outline-variant rounded"><span class="text-sm">${escapeHtml(p.name)}</span><div><input type="number" step="1" value="${Math.round(p.price)}" class="price-edit w-20 px-1 py-1 border border-outline-variant rounded text-sm bg-surface-container-lowest" data-id="${p.id}"><button class="save-price-btn ml-1 text-primary" data-id="${p.id}">💾</button><button class="delete-product-btn ml-1 text-error" data-id="${p.id}">🗑️</button></div></div>`).join(''); document.querySelectorAll('.save-price-btn').forEach(btn => btn.onclick = async () => { const id=btn.dataset.id; const newPrice=parseInt(document.querySelector(`.price-edit[data-id="${id}"]`).value); if(!isNaN(newPrice)) await fetch(`/api/products/${id}`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({price:newPrice})}); fetchProducts(); showToast('Price updated'); }); document.querySelectorAll('.delete-product-btn').forEach(btn => btn.onclick = async () => { if(confirm('Delete?')) await fetch(`/api/products/${btn.dataset.id}`,{method:'DELETE'}); fetchProducts(); cart = cart.filter(i => i.id !== btn.dataset.id); updateCartUI(); saveCartToLocalStorage(); }); }
    document.getElementById('addProductBtn').onclick = async () => { const id = document.getElementById('newProductId').value.trim(); const name = document.getElementById('newProductName').value.trim(); const price = parseInt(document.getElementById('newProductPrice').value); if(!id || !name || isNaN(price)) return showToast('Invalid data'); await fetch('/api/products', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ id, name, price }) }); fetchProducts(); showToast('Product added'); };
    function escapeHtml(str) { return String(str).replace(/[&<>]/g, function(m){if(m==='&') return '&amp;'; if(m==='<') return '&lt;'; if(m==='>') return '&gt;'; return m;}); }
    fetchProducts();
  </script>
</body>
</html>
"""
    return render_template_string(pos_html)

# ---------------------------
# Admin Panel HTML
# ---------------------------
@app.route('/admin', methods=['GET'])
@admin_ip_required
def admin_panel():
    admin_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>Admin - Descalzo Store</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200">
    <style>*{font-family:'Inter',sans-serif;}body{background:#f8f9ff;}.tap-scale:active{transform:scale(0.96);}</style>
</head>
<body class="bg-background text-on-surface">
    <header class="sticky top-0 z-40 bg-surface border-b border-outline-variant shadow-sm flex justify-between items-center px-4 h-16">
        <div class="flex items-center gap-4"><button id="mobileMenuBtn" class="md:hidden material-symbols-outlined text-primary">menu</button><h1 class="text-xl md:text-2xl font-bold text-primary">Descalzo Store Admin</h1></div>
        <div class="flex items-center gap-2"><span class="hidden md:block text-sm text-on-surface-variant">Administrator</span><div class="w-8 h-8 rounded-full bg-primary-container flex items-center justify-center"><span class="material-symbols-outlined text-primary">admin_panel_settings</span></div></div>
    </header>
    <aside id="desktopSidebar" class="hidden md:flex fixed left-0 top-16 w-64 h-full flex-col bg-surface-container-low border-r border-outline-variant p-4 gap-2">
        <div class="mb-4 px-2"><h2 class="text-xs font-bold text-primary uppercase">Management</h2></div>
        <button onclick="showSection('inventory')" class="sidebar-btn active flex items-center gap-3 w-full px-4 py-3 rounded-full text-left transition-all bg-primary-container text-on-primary-container"><span class="material-symbols-outlined">inventory_2</span><span class="font-medium">Inventory</span></button>
        <button onclick="showSection('analytics')" class="sidebar-btn flex items-center gap-3 w-full px-4 py-3 rounded-full text-left text-on-surface-variant hover:bg-surface-container-high"><span class="material-symbols-outlined">monitoring</span><span class="font-medium">Analytics</span></button>
        <button onclick="showSection('theme')" class="sidebar-btn flex items-center gap-3 w-full px-4 py-3 rounded-full text-left text-on-surface-variant hover:bg-surface-container-high"><span class="material-symbols-outlined">palette</span><span class="font-medium">Theme</span></button>
        <a href="/" class="mt-8 flex items-center gap-3 w-full px-4 py-3 rounded-full text-primary hover:bg-surface-container-high"><span class="material-symbols-outlined">point_of_sale</span><span class="font-medium">Back to POS</span></a>
    </aside>
    <main class="md:ml-64 px-4 py-6 pb-24">
        <div id="inventorySection">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6"><div><h2 class="text-2xl font-bold">Product List</h2><p class="text-sm text-on-surface-variant">Manage products (add, edit price, delete)</p></div><button onclick="openAddProductModal()" class="bg-primary text-white px-4 py-2 rounded-xl flex items-center gap-2 tap-scale"><span class="material-symbols-outlined">add</span> Add Product</button></div>
            <div class="bg-primary/10 rounded-xl p-4 text-center mb-6"><div class="text-sm">Total Products</div><div id="statTotalProducts" class="text-3xl font-bold text-primary">-</div></div>
            <div class="flex gap-2 mb-4"><input type="text" id="searchProducts" placeholder="Search by name or ID..." class="flex-1 px-4 py-2 rounded-xl border border-outline-variant bg-white"><button id="searchBtn" class="px-4 py-2 bg-primary text-white rounded-xl">Search</button><button id="clearSearchBtn" class="px-4 py-2 border border-outline-variant rounded-xl">Clear</button></div>
            <div id="productsList" class="space-y-3">Loading products...</div>
        </div>
        <div id="analyticsSection" class="hidden"><div class="max-w-md mx-auto bg-white rounded-2xl shadow-lg p-6 text-center"><h2 class="text-2xl font-bold mb-4">📊 Today's Sales</h2><div id="salesDateDisplay" class="text-sm text-gray-500 mb-3"></div><div class="grid grid-cols-2 gap-4 mb-4"><div class="bg-primary/10 rounded-xl p-3"><div class="text-xs">Items Sold</div><div id="totalQuantityDisplay" class="text-2xl font-bold text-primary">0</div></div><div class="bg-secondary/10 rounded-xl p-3"><div class="text-xs">Total Value</div><div id="totalSalesDisplay" class="text-2xl font-bold text-secondary">₱0</div></div></div><button onclick="loadAnalytics()" class="bg-primary text-white px-4 py-2 rounded-lg text-sm">Refresh</button></div></div>
        <div id="themeSection" class="hidden"><div class="max-w-md mx-auto bg-white rounded-2xl shadow-lg p-6 text-center"><h2 class="text-2xl font-bold mb-4">🎨 Theme Manager</h2><p class="text-gray-500 mb-6">Select a color scheme for the POS system.</p><div class="grid grid-cols-2 gap-3"><button onclick="setTheme('light')" class="p-4 rounded-xl border-2 hover:bg-gray-50">☀️ Light</button><button onclick="setTheme('dark')" class="p-4 rounded-xl border-2 hover:bg-gray-50">🌙 Dark</button><button onclick="setTheme('blue')" class="p-4 rounded-xl border-2 hover:bg-gray-50">💙 Blue</button><button onclick="setTheme('black')" class="p-4 rounded-xl border-2 hover:bg-gray-50">🖤 Black</button></div><div id="themeMsg" class="mt-4 text-green-600 text-sm"></div></div></div>
    </main>
    <div id="addProductModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 hidden items-center justify-center p-4"><div class="bg-white rounded-2xl max-w-md w-full p-6"><h3 class="text-xl font-bold mb-4">Add New Product</h3><input type="text" id="newId" placeholder="Product ID" class="w-full mb-2 px-3 py-2 border rounded-lg"><input type="text" id="newName" placeholder="Product Name" class="w-full mb-2 px-3 py-2 border rounded-lg"><input type="number" id="newPrice" placeholder="Price (₱)" step="1" class="w-full mb-4 px-3 py-2 border rounded-lg"><div class="flex gap-2"><button onclick="addProduct()" class="flex-1 bg-primary text-white py-2 rounded-lg">Add</button><button onclick="closeAddProductModal()" class="flex-1 border py-2 rounded-lg">Cancel</button></div></div></div>
    <script>
        let allProducts = [];
        let currentFiltered = [];
        async function fetchProducts() { const res = await fetch('/api/admin/products'); allProducts = await res.json(); currentFiltered = [...allProducts]; renderProductList(currentFiltered); await fetchStats(); }
        function renderProductList(products) { const container = document.getElementById('productsList'); if (!products.length) { container.innerHTML = '<div class="text-center py-8 text-gray-500">No products found</div>'; return; } container.innerHTML = products.map(p => `<div class="bg-white border rounded-xl p-4 shadow-sm"><div class="flex flex-col md:flex-row md:items-center gap-4"><div class="flex-1"><div class="text-xs text-gray-500">ID: ${p.id}</div><div class="font-bold text-lg">${escapeHtml(p.name)}</div></div><div class="flex items-center gap-4"><div><div class="text-xs text-gray-500">Price</div><div class="font-bold">₱${p.price}</div></div><div class="flex gap-1"><button class="edit-price-btn p-1 text-primary" data-id="${p.id}" data-price="${p.price}">✏️ Edit</button><button class="delete-product-btn p-1 text-error" data-id="${p.id}">🗑️ Delete</button></div></div></div></div>`).join(''); document.querySelectorAll('.edit-price-btn').forEach(btn => btn.onclick = () => editPrice(btn.dataset.id, btn.dataset.price)); document.querySelectorAll('.delete-product-btn').forEach(btn => btn.onclick = () => deleteProduct(btn.dataset.id)); }
        async function editPrice(id, current) { const newPrice = prompt('Enter new price (₱):', current); if (newPrice && !isNaN(parseInt(newPrice))) { await fetch(`/api/admin/products/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ price: parseInt(newPrice) }) }); await fetchProducts(); } }
        async function deleteProduct(id) { if (!confirm('Delete this product?')) return; await fetch(`/api/admin/products/${id}`, { method: 'DELETE' }); await fetchProducts(); }
        async function addProduct() { const id = document.getElementById('newId').value.trim(); const name = document.getElementById('newName').value.trim(); const price = parseInt(document.getElementById('newPrice').value); if (!id || !name || isNaN(price)) { alert('Fill all fields'); return; } await fetch('/api/admin/products', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id, name, price }) }); closeAddProductModal(); fetchProducts(); }
        async function fetchStats() { const res = await fetch('/api/admin/stats'); const data = await res.json(); document.getElementById('statTotalProducts').innerHTML = data.total_products; }
        async function loadAnalytics() { const res = await fetch('/api/sales/today'); const data = await res.json(); document.getElementById('salesDateDisplay').innerHTML = data.date; document.getElementById('totalQuantityDisplay').innerHTML = data.total_quantity || 0; document.getElementById('totalSalesDisplay').innerHTML = `₱${data.total_sales || 0}`; }
        async function setTheme(theme) { const res = await fetch('/admin/set_theme', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ theme }) }); if (res.ok) document.getElementById('themeMsg').innerText = 'Theme saved! Refresh POS to see changes.'; }
        function openAddProductModal() { document.getElementById('addProductModal').classList.remove('hidden'); }
        function closeAddProductModal() { document.getElementById('addProductModal').classList.add('hidden'); }
        function showSection(section) { document.getElementById('inventorySection').classList.add('hidden'); document.getElementById('analyticsSection').classList.add('hidden'); document.getElementById('themeSection').classList.add('hidden'); document.getElementById(`${section}Section`).classList.remove('hidden'); document.querySelectorAll('.sidebar-btn').forEach(btn => btn.classList.remove('bg-primary-container', 'text-on-primary-container')); if (section === 'inventory') fetchProducts(); if (section === 'analytics') loadAnalytics(); }
        document.getElementById('searchBtn').onclick = () => { const q = document.getElementById('searchProducts').value.toLowerCase(); currentFiltered = allProducts.filter(p => p.name.toLowerCase().includes(q) || String(p.id).includes(q)); renderProductList(currentFiltered); };
        document.getElementById('clearSearchBtn').onclick = () => { document.getElementById('searchProducts').value = ''; currentFiltered = [...allProducts]; renderProductList(currentFiltered); };
        function escapeHtml(str) { return String(str).replace(/[&<>]/g, m => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;' })[m]); }
        fetchProducts(); showSection('inventory');
    </script>
</body>
</html>
"""
    return render_template_string(admin_html)

# ---------------------------
# Admin API endpoints
# ---------------------------
@app.route('/api/admin/stats', methods=['GET'])
@admin_ip_required
def admin_stats():
    try:
        resp = supabase.table('product').select('id', count='exact').execute()
        total_products = len(resp.data)
        return jsonify({"total_products": total_products})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/products', methods=['GET'])
@admin_ip_required
def admin_products():
    try:
        resp = supabase.table('product').select('id, name, price').execute()
        return jsonify(resp.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/products', methods=['POST'])
@admin_ip_required
def admin_add_product():
    data = request.json
    try:
        supabase.table('product').insert({"id": str(data['id']), "name": data['name'], "price": int(data['price'])}).execute()
        return jsonify({"status": "ok"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/admin/products/<product_id>', methods=['PUT'])
@admin_ip_required
def admin_update_product(product_id):
    data = request.json
    try:
        supabase.table('product').update({"price": int(data['price'])}).eq('id', product_id).execute()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/admin/products/<product_id>', methods=['DELETE'])
@admin_ip_required
def admin_delete_product(product_id):
    try:
        supabase.table('product').delete().eq('id', product_id).execute()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ---------------------------
# Today's Sales API
# ---------------------------
@app.route('/api/sales/today', methods=['GET'])
@admin_ip_required
def get_today_sales():
    try:
        now_ph = ph_now()
        today_start_ph = datetime(now_ph.year, now_ph.month, now_ph.day, 0, 0, 0)
        today_end_ph = today_start_ph + timedelta(days=1)
        start_utc = today_start_ph - PH_TZ_OFFSET
        end_utc = today_end_ph - PH_TZ_OFFSET
        response = supabase.table('transactions').select('items, total').gte('created_at', start_utc.isoformat()).lt('created_at', end_utc.isoformat()).execute()
        total_quantity = 0
        total_sales = 0
        for tx in response.data:
            total_sales += tx.get('total', 0)
            items = tx.get('items')
            if items:
                try:
                    items_list = json.loads(items) if isinstance(items, str) else items
                    for item in items_list:
                        total_quantity += item.get('quantity', 0)
                except:
                    pass
        date_str = now_ph.strftime("%B %d, %Y")
        return jsonify({"date": date_str, "total_sales": total_sales, "total_quantity": total_quantity})
    except Exception as e:
        date_str = ph_now().strftime("%B %d, %Y")
        return jsonify({"date": date_str, "total_sales": 0, "total_quantity": 0}), 200

# ---------------------------
# Theme API
# ---------------------------
@app.route('/api/theme', methods=['GET'])
def get_theme():
    return jsonify({"theme": get_current_theme()})

@app.route('/admin/set_theme', methods=['POST'])
@admin_ip_required
def set_theme_route():
    data = request.json
    theme = data.get('theme')
    if theme in ['light', 'dark', 'blue', 'black']:
        set_theme(theme)
        return jsonify({"status": "ok"})
    return jsonify({"error": "invalid theme"}), 400

@app.route('/robots.txt')
def robots():
    return "User-agent: *\nDisallow: /admin\n"

# ---------------------------
# POS Product APIs
# ---------------------------
@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        resp = supabase.table('product').select('id, name, price').execute()
        for p in resp.data:
            p['price'] = int(round(float(p['price']))) if p.get('price') else 0
        return jsonify(resp.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.json
    supabase.table('product').insert({"id": str(data['id']), "name": data['name'], "price": int(data['price'])}).execute()
    return jsonify({"status": "ok"}), 201

@app.route('/api/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.json
    supabase.table('product').update({"price": int(data['price'])}).eq('id', product_id).execute()
    return jsonify({"status": "ok"})

@app.route('/api/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    supabase.table('product').delete().eq('id', product_id).execute()
    return jsonify({"status": "ok"})

@app.route('/api/transaction', methods=['POST'])
def log_transaction():
    data = request.json
    try:
        supabase.table('transactions').insert({
            "transaction_id": data['transactionId'],
            "items": json.dumps(data['items']),
            "subtotal": int(data['subtotal']),
            "tax": int(data['tax']),
            "total": int(data['total']),
            "payment_method": data['method'],
            "cash_given": int(data.get('cash_given', 0)),
            "change_due": int(data.get('change_due', 0)),
            "created_at": datetime.utcnow().isoformat()
        }).execute()
    except Exception as e:
        app.logger.warning(f"Transaction save failed: {e}")
    return jsonify({"status": "ok"}), 200

# ---------------------------
# Run Server
# ---------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)