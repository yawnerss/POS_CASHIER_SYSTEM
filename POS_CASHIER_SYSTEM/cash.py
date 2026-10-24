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
# Shared design system CSS
# ---------------------------
BASE_CSS = """
*,*::before,*::after{box-sizing:border-box;}
html,body{margin:0;padding:0;}
html{-webkit-text-size-adjust:100%;text-size-adjust:100%;}
body{
  font-family:'Inter',system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;
  background:var(--bg);color:var(--text);
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;
  line-height:1.45;min-height:100dvh;
}
button{font:inherit;color:inherit;cursor:pointer;border:none;background:none;padding:0;}
input,select,textarea{font:inherit;color:inherit;}
img{max-width:100%;display:block;}
a{color:inherit;text-decoration:none;}

:root{
  --bg:#f4f6fb;--surface:#ffffff;--surface-2:#eef1f8;--surface-3:#e2e7f1;
  --border:#dde3ed;--border-strong:#c7cfdd;
  --text:#0f1729;--text-2:#4b5567;--text-3:#8892a4;
  --primary:#1d4ed8;--primary-2:#1e40af;--primary-soft:#dbeafe;--primary-fg:#ffffff;
  --success:#059669;--success-soft:#d1fae5;
  --danger:#dc2626;--danger-soft:#fee2e2;
  --warning:#d97706;--warning-soft:#fef3c7;
  --shadow-1:0 1px 2px rgba(15,23,41,.05);
  --shadow-2:0 4px 12px rgba(15,23,41,.08);
  --shadow-3:0 10px 28px rgba(15,23,41,.14);
  --r-sm:8px;--r-md:12px;--r-lg:16px;--r-xl:20px;--r-full:9999px;
  --tap:44px;--header-h:56px;
  --safe-b:env(safe-area-inset-bottom,0px);
  --safe-t:env(safe-area-inset-top,0px);
  --safe-l:env(safe-area-inset-left,0px);
  --safe-r:env(safe-area-inset-right,0px);
}
[data-theme="dark"]{
  --bg:#0a0f1f;--surface:#131a2c;--surface-2:#1a2238;--surface-3:#232d45;
  --border:#2a3348;--border-strong:#3a4560;
  --text:#e8ecf5;--text-2:#aab5c8;--text-3:#6b7893;
  --primary:#5c8bff;--primary-2:#3f6fea;--primary-soft:#1c2a4d;--primary-fg:#ffffff;
  --success:#34d399;--success-soft:#064e3b;--danger:#f87171;--danger-soft:#4c0519;--warning:#fbbf24;--warning-soft:#451a03;
  --shadow-1:0 1px 2px rgba(0,0,0,.35);--shadow-2:0 4px 12px rgba(0,0,0,.4);
  --shadow-3:0 10px 28px rgba(0,0,0,.55);
}
[data-theme="blue"]{
  --bg:#eaf1ff;--surface:#ffffff;--surface-2:#e3ecff;--surface-3:#d4e1f7;
  --border:#c7d5ec;--border-strong:#a9bdd9;
  --text:#0a1a35;--text-2:#3d4f6e;--text-3:#7a8aa0;
  --primary:#1e40af;--primary-2:#1e3a8a;--primary-soft:#dbeafe;
}
[data-theme="black"]{
  --bg:#000;--surface:#111;--surface-2:#1b1b1b;--surface-3:#262626;
  --border:#2a2a2a;--border-strong:#3a3a3a;
  --text:#f5f5f5;--text-2:#a3a3a3;--text-3:#6b6b6b;
  --primary:#f97316;--primary-2:#ea580c;--primary-soft:#3d1a00;--primary-fg:#fff;
  --success:#22c55e;--success-soft:#052e16;--danger:#ef4444;--danger-soft:#450a0a;--warning:#eab308;--warning-soft:#422006;
}

.app{
  min-height:100dvh;display:flex;flex-direction:column;
  padding-top:var(--safe-t);padding-left:var(--safe-l);padding-right:var(--safe-r);
}
.app-header{
  position:sticky;top:0;z-index:30;height:var(--header-h);padding:0 12px;
  display:flex;align-items:center;gap:8px;
  background:color-mix(in srgb,var(--surface) 92%,transparent);
  backdrop-filter:saturate(180%) blur(12px);-webkit-backdrop-filter:saturate(180%) blur(12px);
  border-bottom:1px solid var(--border);
}
.brand{display:flex;align-items:center;gap:10px;min-width:0;flex:1;}
.brand-mark{
  width:34px;height:34px;border-radius:10px;
  background:linear-gradient(135deg,var(--primary),var(--primary-2));
  color:var(--primary-fg);display:flex;align-items:center;justify-content:center;
  flex-shrink:0;font-weight:700;font-size:16px;
}
.brand-name{font-size:15px;font-weight:700;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}

.btn{
  display:inline-flex;align-items:center;justify-content:center;gap:6px;
  min-height:var(--tap);padding:0 16px;border-radius:var(--r-md);
  font-weight:600;font-size:14px;transition:background .15s,border-color .15s,transform .05s;
  user-select:none;-webkit-user-select:none;white-space:nowrap;
}
.btn:active{transform:scale(.97);}
.btn-primary{background:var(--primary);color:var(--primary-fg);}
.btn-primary:hover{background:var(--primary-2);}
.btn-secondary{background:var(--surface-2);color:var(--text);border:1px solid var(--border);}
.btn-secondary:hover{background:var(--surface-3);}
.btn-success{background:var(--success);color:#fff;}
.btn-danger{background:var(--danger-soft);color:var(--danger);}
.btn-ghost{background:transparent;color:var(--text-2);}
.btn-ghost:hover{background:var(--surface-2);color:var(--text);}
.btn-sm{min-height:36px;padding:0 12px;font-size:13px;border-radius:var(--r-sm);}
.btn-block{width:100%;}
.btn:disabled,.btn[disabled]{opacity:.5;pointer-events:none;}

.icon-btn{
  width:var(--tap);height:var(--tap);border-radius:var(--r-md);
  display:inline-flex;align-items:center;justify-content:center;
  color:var(--text-2);background:transparent;transition:background .15s,color .15s;
}
.icon-btn:hover{background:var(--surface-2);color:var(--text);}
.icon-btn.primary{color:var(--primary);}

.field{display:flex;flex-direction:column;gap:6px;}
.field-label{font-size:13px;font-weight:600;color:var(--text-2);}
.input{
  width:100%;min-height:var(--tap);padding:10px 14px;border-radius:var(--r-md);
  border:1px solid var(--border);background:var(--surface);color:var(--text);
  font-size:16px;outline:none;transition:border-color .15s,box-shadow .15s;
}
.input:focus{border-color:var(--primary);box-shadow:0 0 0 3px var(--primary-soft);}
.input::placeholder{color:var(--text-3);}

.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-lg);box-shadow:var(--shadow-1);}

.badge{display:inline-flex;align-items:center;gap:4px;padding:2px 10px;border-radius:var(--r-full);font-size:12px;font-weight:600;}
.badge-primary{background:var(--primary-soft);color:var(--primary);}
.badge-success{background:var(--success-soft);color:var(--success);}
.badge-danger{background:var(--danger-soft);color:var(--danger);}
.badge-neutral{background:var(--surface-2);color:var(--text-2);}

.thin-scroll{scrollbar-width:thin;scrollbar-color:var(--border-strong) transparent;}
.thin-scroll::-webkit-scrollbar{width:6px;}
.thin-scroll::-webkit-scrollbar-thumb{background:var(--border-strong);border-radius:3px;}

.toast-wrap{
  position:fixed;left:50%;transform:translateX(-50%);
  top:calc(var(--header-h) + var(--safe-t) + 12px);z-index:200;
  display:flex;flex-direction:column;gap:8px;width:calc(100% - 24px);
  max-width:380px;pointer-events:none;
}
.toast{
  background:var(--text);color:var(--bg);padding:12px 14px;border-radius:var(--r-md);
  font-size:13px;font-weight:500;box-shadow:var(--shadow-3);
  display:flex;align-items:center;justify-content:space-between;gap:12px;
  animation:toastIn .25s ease-out;pointer-events:auto;
}
@keyframes toastIn{from{opacity:0;transform:translateY(-8px);}to{opacity:1;transform:translateY(0);}}
.toast-undo{color:#fbbf24;font-weight:700;text-transform:uppercase;font-size:12px;letter-spacing:.05em;}

.modal{
  position:fixed;inset:0;z-index:150;display:none;
  background:rgba(6,10,22,.55);backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px);
  align-items:flex-end;justify-content:center;padding:0;animation:fadeIn .15s ease-out;
}
.modal.open{display:flex;}
@keyframes fadeIn{from{opacity:0;}to{opacity:1;}}
.modal-card{
  background:var(--surface);width:100%;max-width:520px;
  border-radius:var(--r-xl) var(--r-xl) 0 0;
  max-height:92dvh;display:flex;flex-direction:column;
  box-shadow:var(--shadow-3);animation:sheetUp .25s cubic-bezier(.16,1,.3,1);
  padding-bottom:var(--safe-b);
}
@keyframes sheetUp{from{transform:translateY(20px);opacity:.6;}to{transform:translateY(0);opacity:1;}}
.modal-head{
  padding:14px 16px;border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;gap:8px;flex-shrink:0;
}
.modal-title{font-size:17px;font-weight:700;}
.modal-body{padding:16px;overflow-y:auto;flex:1;-webkit-overflow-scrolling:touch;}
.modal-foot{padding:12px 16px;border-top:1px solid var(--border);display:flex;gap:8px;flex-shrink:0;}

@media (min-width:640px){
  .modal{align-items:center;padding:20px;}
  .modal-card{border-radius:var(--r-xl);max-height:85dvh;padding-bottom:0;}
}

.empty{padding:40px 20px;text-align:center;color:var(--text-3);font-size:14px;}
.empty-icon{font-size:40px;opacity:.4;margin-bottom:8px;display:block;}
.spinner{width:22px;height:22px;border:2px solid var(--border);border-top-color:var(--primary);border-radius:50%;animation:spin .7s linear infinite;margin:0 auto;}
@keyframes spin{to{transform:rotate(360deg);}}
.loading-row{display:flex;align-items:center;justify-content:center;gap:10px;padding:40px 20px;color:var(--text-3);font-size:14px;}

:focus-visible{outline:2px solid var(--primary);outline-offset:2px;border-radius:6px;}
.btn:focus-visible,.icon-btn:focus-visible,.input:focus-visible{outline-offset:2px;}

.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0;}
.row{display:flex;align-items:center;}
.row-between{display:flex;align-items:center;justify-content:space-between;}
.text-muted{color:var(--text-2);}
.text-sm{font-size:13px;}
.text-xs{font-size:12px;}
.mono{font-variant-numeric:tabular-nums;font-feature-settings:'tnum';}
"""

def _error_page(code, title, msg):
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{code} — {title}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>{BASE_CSS}</style></head>
<body>
<div style="min-height:100dvh;display:flex;align-items:center;justify-content:center;padding:24px;">
  <div style="text-align:center;max-width:400px;">
    <div style="font-size:64px;font-weight:800;color:var(--primary);line-height:1;">{code}</div>
    <h1 style="font-size:20px;margin:12px 0 8px;">{title}</h1>
    <p style="color:var(--text-2);margin:0 0 24px;font-size:14px;">{msg}</p>
    <a href="/" class="btn btn-primary" style="display:inline-flex;">Back to POS</a>
  </div>
</div></body></html>"""

@app.errorhandler(404)
def page_not_found(e):
    return _error_page(404, "Page not found", "The page you're looking for doesn't exist."), 404

@app.errorhandler(403)
def forbidden(e):
    return _error_page(403, "Access denied", "Your IP is not authorised to access this page."), 403

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        supabase.table('product').select('id').limit(1).execute()
        return jsonify({"status": "ok", "supabase": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "error", "supabase": "disconnected", "message": str(e)}), 500

# ---------------------------
# POS PAGE
# ---------------------------
@app.route('/')
def index():
    pos_html = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Descalzo Store — POS</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200">
<style>
__BASE_CSS__

.pos-main{
  flex:1;display:flex;flex-direction:column;
  padding-bottom:calc(96px + var(--safe-b));
}

.search-wrap{
  padding:12px 12px 8px;position:sticky;top:var(--header-h);z-index:20;
  background:color-mix(in srgb,var(--bg) 92%,transparent);
  backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);
}
.search-box{position:relative;}
.search-box .material-symbols-outlined{
  position:absolute;left:14px;top:50%;transform:translateY(-50%);
  color:var(--text-3);font-size:20px;pointer-events:none;
}
.search-box .input{padding-left:44px;}

.product-grid{
  display:grid;grid-template-columns:repeat(2,1fr);gap:10px;padding:0 12px 12px;
}
@media (min-width:520px){.product-grid{grid-template-columns:repeat(3,1fr);}}
@media (min-width:900px){.product-grid{grid-template-columns:repeat(4,1fr);}}

.product-card{
  background:var(--surface);border:1px solid var(--border);
  border-radius:var(--r-lg);overflow:hidden;cursor:pointer;
  transition:transform .08s,box-shadow .15s,border-color .15s;
  display:flex;flex-direction:column;text-align:left;box-shadow:var(--shadow-1);
}
.product-card:active{transform:scale(.97);}
@media (hover:hover){.product-card:hover{border-color:var(--primary);box-shadow:var(--shadow-2);}}
.product-thumb{
  aspect-ratio:1/1;background:var(--surface-2);
  display:flex;align-items:center;justify-content:center;
  color:var(--primary);opacity:.6;
}
.product-thumb .material-symbols-outlined{font-size:36px;}
.product-meta{padding:8px 10px 10px;min-width:0;}
.product-name{font-size:13px;font-weight:600;color:var(--text);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin:0 0 2px;}
.product-price{font-size:14px;font-weight:700;color:var(--primary);margin:0;
  font-variant-numeric:tabular-nums;}

/* ---------- Floating cart button ---------- */
.cart-fab{
  position:fixed;bottom:calc(16px + var(--safe-b));right:calc(16px + var(--safe-r));
  z-index:60;display:flex;align-items:center;gap:10px;
  min-height:56px;padding:0 20px;border-radius:var(--r-full);
  background:var(--primary);color:var(--primary-fg);
  box-shadow:var(--shadow-3);font-weight:700;font-size:14px;
  transition:transform .1s,opacity .2s;user-select:none;-webkit-user-select:none;
}
.cart-fab:active{transform:scale(.95);}
.cart-fab.empty{opacity:.65;}
.cart-fab .material-symbols-outlined{font-size:22px;}
.cart-fab-count{
  background:rgba(255,255,255,.25);padding:2px 8px;
  border-radius:var(--r-full);font-size:12px;
  font-variant-numeric:tabular-nums;
}
.cart-fab-total{font-variant-numeric:tabular-nums;}

/* ---------- Cart modal internals ---------- */
.cart-items{padding:0 8px;min-height:80px;}
.cart-item{
  display:flex;align-items:center;gap:8px;
  padding:10px 8px;border-bottom:1px solid var(--border);
}
.cart-item:last-child{border-bottom:none;}
.cart-item-info{flex:1;min-width:0;}
.cart-item-name{font-size:13px;font-weight:600;color:var(--text);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.cart-item-unit{font-size:11px;color:var(--text-3);}
.cart-item-controls{display:flex;align-items:center;gap:4px;flex-shrink:0;}
.qty-btn{
  width:32px;height:32px;border-radius:var(--r-sm);
  background:var(--surface-2);color:var(--text);
  display:inline-flex;align-items:center;justify-content:center;
  font-weight:700;font-size:16px;transition:background .15s;
}
.qty-btn:hover{background:var(--surface-3);}
.qty-btn:active{transform:scale(.9);}
.qty-val{min-width:22px;text-align:center;font-size:13px;font-weight:700;font-variant-numeric:tabular-nums;}
.cart-item-line{min-width:60px;text-align:right;font-size:13px;font-weight:700;font-variant-numeric:tabular-nums;}
.remove-btn{
  width:32px;height:32px;border-radius:var(--r-sm);
  background:var(--danger-soft);color:var(--danger);
  display:inline-flex;align-items:center;justify-content:center;
}
.remove-btn:active{transform:scale(.9);}

.cart-toolbar{
  display:flex;gap:6px;padding:10px 16px;
  border-top:1px solid var(--border);overflow-x:auto;
}
.chip{
  display:inline-flex;align-items:center;gap:4px;
  min-height:32px;padding:0 12px;border-radius:var(--r-full);
  background:var(--surface-2);color:var(--text-2);
  font-size:12px;font-weight:600;white-space:nowrap;
  transition:background .15s,color .15s;
}
.chip:hover{background:var(--surface-3);}
.chip.active{background:var(--primary-soft);color:var(--primary);}
.chip.danger{background:var(--danger-soft);color:var(--danger);}

.cart-totals{
  padding:12px 16px;background:var(--surface-2);
  border-top:1px solid var(--border);font-size:13px;
}
.totals-line{display:flex;justify-content:space-between;padding:3px 0;font-variant-numeric:tabular-nums;}
.totals-line.total{
  padding-top:8px;margin-top:4px;border-top:1px dashed var(--border-strong);
  font-size:15px;font-weight:700;
}
.totals-line.total .amount{color:var(--primary);font-size:22px;}

.cart-pay{
  padding:12px 16px 16px;border-top:1px solid var(--border);
  display:flex;flex-direction:column;gap:8px;
}
.pay-field .field-label{font-size:12px;margin-bottom:4px;}
.pay-field .input{min-height:44px;font-size:16px;padding:8px 12px;}
.pay-change{
  background:var(--success-soft);color:var(--success);
  border-radius:var(--r-md);padding:8px 12px;
  display:flex;align-items:center;justify-content:space-between;
  font-size:12px;font-weight:600;
}
.pay-change .amount{font-size:18px;font-weight:800;font-variant-numeric:tabular-nums;}
.pay-error{color:var(--danger);font-size:12px;text-align:center;font-weight:600;}
.pay-submit{min-height:48px;font-size:15px;font-weight:700;border-radius:var(--r-md);}

.mgmt-row{
  display:flex;align-items:center;gap:8px;
  padding:10px 12px;border:1px solid var(--border);
  border-radius:var(--r-md);background:var(--surface);margin-bottom:8px;
}
.mgmt-row-name{flex:1;min-width:0;font-size:13px;font-weight:600;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.mgmt-row-price{width:80px;min-height:36px;font-size:14px;padding:6px 8px;}

.success-hero{text-align:center;padding:8px 0 16px;}
.success-icon{
  width:72px;height:72px;border-radius:50%;
  background:var(--success-soft);color:var(--success);
  display:inline-flex;align-items:center;justify-content:center;margin-bottom:12px;
}
.success-icon .material-symbols-outlined{font-size:40px;}

.boot{
  position:fixed;inset:0;z-index:300;display:flex;align-items:center;justify-content:center;
  background:var(--bg);transition:opacity .5s;
}
.boot-mark{
  width:64px;height:64px;border-radius:16px;
  background:linear-gradient(135deg,var(--primary),var(--primary-2));
  display:flex;align-items:center;justify-content:center;
  color:#fff;font-weight:800;font-size:24px;margin:0 auto 16px;
  animation:pulse 2s ease-in-out infinite;
}
@keyframes pulse{0%,100%{transform:scale(1);}50%{transform:scale(1.05);}}
.boot-title{font-size:13px;font-weight:700;letter-spacing:.4em;text-transform:uppercase;color:var(--text-2);}
</style>
</head>
<body>

<div id="loadingScreen" class="boot">
  <div style="text-align:center;">
    <div class="boot-mark">D</div>
    <div class="boot-title">Descalzo Store</div>
  </div>
</div>

<div id="posContent" class="app" style="display:none;opacity:0;transition:opacity .4s;">
  <header class="app-header">
    <div class="brand">
      <div class="brand-mark">D</div>
      <div class="brand-name">Descalzo Store</div>
    </div>
    <button id="manageProductsBtn" class="icon-btn" aria-label="Manage products">
      <span class="material-symbols-outlined">inventory_2</span>
    </button>
    <a href="/admin" class="icon-btn" aria-label="Admin panel">
      <span class="material-symbols-outlined">admin_panel_settings</span>
    </a>
  </header>

  <main class="pos-main">
    <div class="search-wrap">
      <div class="search-box">
        <span class="material-symbols-outlined">search</span>
        <input type="search" id="searchInput" class="input" placeholder="Search products…" autocomplete="off" inputmode="search">
      </div>
    </div>
    <div class="product-grid" id="productsGrid">
      <div class="loading-row" style="grid-column:1/-1;"><span class="spinner"></span> Loading products…</div>
    </div>
  </main>

  <!-- FLOATING CART BUTTON (replaces the cashier panel) -->
  <button id="cartFab" class="cart-fab empty" aria-label="Open cart">
    <span class="material-symbols-outlined">shopping_cart</span>
    <span id="cartFabCount" class="cart-fab-count">0</span>
    <span id="cartFabTotal" class="cart-fab-total">₱0</span>
  </button>
</div>

<!-- CART MODAL -->
<div id="cartModal" class="modal" role="dialog" aria-modal="true" aria-labelledby="cartModalTitle">
  <div class="modal-card">
    <div class="modal-head">
      <h3 class="modal-title" id="cartModalTitle">Current Order</h3>
      <button id="closeCartModal" class="icon-btn" aria-label="Close">
        <span class="material-symbols-outlined">close</span>
      </button>
    </div>
    <div class="modal-body thin-scroll" style="padding:0;">
      <div id="cartItemsContainer" class="cart-items thin-scroll"></div>
      <div class="cart-toolbar">
        <button id="discountChip" class="chip">
          <span class="material-symbols-outlined" style="font-size:16px;">percent</span> Discount
        </button>
        <button id="taxExemptChip" class="chip">
          <span class="material-symbols-outlined" style="font-size:16px;">receipt_long</span> Tax Exempt
        </button>
        <button id="clearCartBtn" class="chip danger">
          <span class="material-symbols-outlined" style="font-size:16px;">delete_sweep</span> Clear
        </button>
      </div>
      <div class="cart-totals">
        <div class="totals-line"><span>Subtotal</span><span id="subtotalAmount" class="mono">₱0</span></div>
        <div class="totals-line"><span>Tax (8%)</span><span id="taxAmount" class="mono">₱0</span></div>
        <div class="totals-line"><span>Discount</span><span id="discountAmountDisplay" class="mono">-₱0</span></div>
        <div class="totals-line total"><span>Total</span><span id="grandTotal" class="amount mono">₱0</span></div>
      </div>
      <div class="cart-pay">
        <div class="pay-field">
          <label class="field-label" for="cashGiven">Amount received (₱)</label>
          <input type="number" id="cashGiven" class="input" step="1" min="0" inputmode="numeric" placeholder="0" autocomplete="off">
        </div>
        <div id="changeDueArea" class="pay-change" style="display:none;">
          <span>Change</span>
          <span id="changeDue" class="amount mono">₱0</span>
        </div>
        <div id="insufficientError" class="pay-error" style="display:none;">Amount is below total</div>
        <button id="completePaymentBtn" class="btn btn-success btn-block pay-submit">
          <span class="material-symbols-outlined" style="font-size:20px;">check_circle</span> Complete Payment
        </button>
      </div>
    </div>
  </div>
</div>

<!-- MANAGE PRODUCTS MODAL -->
<div id="productModal" class="modal" role="dialog" aria-modal="true" aria-labelledby="manageTitle">
  <div class="modal-card">
    <div class="modal-head">
      <h3 class="modal-title" id="manageTitle">Manage Products</h3>
      <button id="closeProductModal" class="icon-btn" aria-label="Close">
        <span class="material-symbols-outlined">close</span>
      </button>
    </div>
    <div class="modal-body thin-scroll">
      <div class="card" style="padding:14px;margin-bottom:16px;">
        <h4 style="font-size:14px;font-weight:700;margin:0 0 10px;">Add New Product</h4>
        <div style="display:grid;grid-template-columns:1fr 2fr 1fr;gap:8px;">
          <input type="text" id="newProductId" class="input" placeholder="ID" style="font-size:14px;">
          <input type="text" id="newProductName" class="input" placeholder="Name" style="font-size:14px;">
          <input type="number" id="newProductPrice" class="input" placeholder="₱" step="1" inputmode="decimal" style="font-size:14px;">
        </div>
        <button id="addProductBtn" class="btn btn-primary btn-block" style="margin-top:10px;">
          <span class="material-symbols-outlined" style="font-size:20px;">add</span> Add Product
        </button>
      </div>
      <h4 style="font-size:14px;font-weight:700;margin:0 0 10px;">Existing Products</h4>
      <div id="manageProductsList"></div>
    </div>
  </div>
</div>

<!-- SUCCESS MODAL -->
<div id="successModal" class="modal" role="dialog" aria-modal="true" aria-labelledby="successTitle">
  <div class="modal-card">
    <div class="modal-body">
      <div class="success-hero">
        <div class="success-icon"><span class="material-symbols-outlined">check_circle</span></div>
        <h2 class="modal-title" id="successTitle">Payment complete</h2>
        <p class="text-sm text-muted" style="margin:4px 0 0;">Transaction #<span id="receiptId" class="mono"></span></p>
      </div>
      <div style="background:var(--surface-2);border-radius:var(--r-md);padding:12px;font-size:13px;">
        <div id="receiptItems"></div>
        <div style="border-top:1px dashed var(--border-strong);margin-top:8px;padding-top:8px;display:flex;justify-content:space-between;">
          <span>Cash given</span><span id="receiptCashGiven" class="mono"></span>
        </div>
        <div style="display:flex;justify-content:space-between;margin-top:2px;">
          <span>Change</span><span id="receiptChange" class="mono"></span>
        </div>
        <div style="display:flex;justify-content:space-between;margin-top:8px;padding-top:8px;border-top:1px dashed var(--border-strong);font-weight:700;">
          <span>Total paid</span><span id="receiptTotal" class="mono"></span>
        </div>
      </div>
    </div>
    <div class="modal-foot">
      <button id="newTransactionBtn" class="btn btn-primary btn-block">New Transaction</button>
    </div>
  </div>
</div>

<div class="toast-wrap" id="toastWrap"></div>

<script>
'use strict';

async function loadTheme(){
  try{
    const r = await fetch('/api/theme'); const d = await r.json();
    document.documentElement.setAttribute('data-theme', d.theme || 'light');
  }catch(e){ document.documentElement.setAttribute('data-theme','light'); }
}
loadTheme();

let products = [];
let cart = [];
let taxRate = 8;
let discountAmount = 0;
let isTaxExempt = false;
let searchQuery = '';
let paymentLocked = false;

const $ = id => document.getElementById(id);
const productsGrid = $('productsGrid');
const cartContainer = $('cartItemsContainer');
const subtotalSpan = $('subtotalAmount');
const taxSpan = $('taxAmount');
const discountSpan = $('discountAmountDisplay');
const grandTotalSpan = $('grandTotal');
const cashGivenInput = $('cashGiven');
const changeDueArea = $('changeDueArea');
const changeDueSpan = $('changeDue');
const insufficientError = $('insufficientError');
const completePaymentBtn = $('completePaymentBtn');
const loadingScreen = $('loadingScreen');
const posContent = $('posContent');
const taxExemptChip = $('taxExemptChip');
const discountChip = $('discountChip');
const cartFab = $('cartFab');
const cartFabCount = $('cartFabCount');
const cartFabTotal = $('cartFabTotal');

/* ---------- Persistence ---------- */
function saveCartToLocalStorage(){
  localStorage.setItem('pos_cart', JSON.stringify(cart));
  localStorage.setItem('pos_discount', discountAmount);
  localStorage.setItem('pos_taxExempt', isTaxExempt);
}
function loadCartFromLocalStorage(){
  try{
    const s = localStorage.getItem('pos_cart');
    if(s) cart = JSON.parse(s) || [];
    const d = parseInt(localStorage.getItem('pos_discount')||'0');
    if(!isNaN(d)) discountAmount = d;
    isTaxExempt = localStorage.getItem('pos_taxExempt') === 'true';
    if(isTaxExempt) taxExemptChip.classList.add('active');
    if(discountAmount > 0) discountChip.classList.add('active');
  }catch(e){ cart = []; }
  updateCartUI();
}
function clearLocalStorageCart(){
  localStorage.removeItem('pos_cart');
  localStorage.removeItem('pos_discount');
  localStorage.removeItem('pos_taxExempt');
}

/* ---------- Products ---------- */
async function fetchProducts(){
  try{
    const r = await fetch('/api/products');
    const data = await r.json();
    products = data.map(p => ({ id: String(p.id), name: p.name, price: Math.round(parseFloat(p.price)) }));
    renderProducts();
    if(loadingScreen && posContent && posContent.style.display === 'none'){
      loadingScreen.style.opacity = '0';
      setTimeout(()=>{
        loadingScreen.style.display = 'none';
        posContent.style.display = 'flex';
        requestAnimationFrame(()=>{ posContent.style.opacity = '1'; });
      }, 400);
    }
    loadCartFromLocalStorage();
  }catch(e){
    productsGrid.innerHTML = '<div class="empty" style="grid-column:1/-1;"><span class="material-symbols-outlined empty-icon">error</span>Could not load products</div>';
    if(loadingScreen) loadingScreen.style.display = 'none';
    if(posContent){ posContent.style.display = 'flex'; posContent.style.opacity = '1'; }
  }
}
function renderProducts(){
  const filtered = products.filter(p => p.name.toLowerCase().includes(searchQuery));
  if(!filtered.length){
    productsGrid.innerHTML = '<div class="empty" style="grid-column:1/-1;"><span class="material-symbols-outlined empty-icon">search_off</span>No products found</div>';
    return;
  }
  productsGrid.innerHTML = filtered.map(p => `
    <button type="button" class="product-card" onclick="addToCart('${p.id}')" aria-label="Add ${escapeHtml(p.name)} to cart">
      <div class="product-thumb"><span class="material-symbols-outlined">local_mall</span></div>
      <div class="product-meta">
        <p class="product-name">${escapeHtml(p.name)}</p>
        <p class="product-price">₱${p.price}</p>
      </div>
    </button>`).join('');
}

/* ---------- Cart ---------- */
window.addToCart = function(id){
  const p = products.find(x => x.id === id);
  if(!p) return;
  const existing = cart.find(i => i.id === id);
  const wasExisting = !!existing;
  if(existing) existing.quantity += 1;
  else cart.push({ id: p.id, name: p.name, price: p.price, quantity: 1 });
  updateCartUI();
  saveCartToLocalStorage();
  showToast(`${p.name} added`, () => {
    if(wasExisting){
      const it = cart.find(x => x.id === id);
      if(it){ it.quantity -= 1; if(it.quantity <= 0) cart = cart.filter(x => x.id !== id); }
    }else{
      cart = cart.filter(x => x.id !== id);
    }
    updateCartUI(); saveCartToLocalStorage();
  });
};

function updateCartUI(){
  if(!cart.length){
    cartContainer.innerHTML = '<div class="empty" style="padding:32px 12px;"><span class="material-symbols-outlined empty-icon">shopping_cart</span>Your cart is empty</div>';
    computeTotals();
    return;
  }
  cartContainer.innerHTML = cart.map(item => `
    <div class="cart-item">
      <div class="cart-item-info">
        <div class="cart-item-name">${escapeHtml(item.name)}</div>
        <div class="cart-item-unit">₱${item.price} each</div>
      </div>
      <div class="cart-item-controls">
        <button class="qty-btn" data-id="${item.id}" data-d="-1" aria-label="Decrease quantity">−</button>
        <span class="qty-val">${item.quantity}</span>
        <button class="qty-btn" data-id="${item.id}" data-d="1" aria-label="Increase quantity">+</button>
        <span class="cart-item-line mono">₱${item.price * item.quantity}</span>
        <button class="remove-btn" data-id="${item.id}" aria-label="Remove item">
          <span class="material-symbols-outlined" style="font-size:16px;">delete</span>
        </button>
      </div>
    </div>`).join('');

  cartContainer.querySelectorAll('.qty-btn').forEach(btn => {
    btn.onclick = () => changeQuantity(btn.dataset.id, parseInt(btn.dataset.d));
  });
  cartContainer.querySelectorAll('.remove-btn').forEach(btn => {
    btn.onclick = () => removeCartItem(btn.dataset.id);
  });
  computeTotals();
}

function changeQuantity(id, delta){
  const i = cart.find(x => x.id === id);
  if(!i) return;
  i.quantity += delta;
  if(i.quantity <= 0) cart = cart.filter(x => x.id !== id);
  updateCartUI(); saveCartToLocalStorage();
}
function removeCartItem(id){
  cart = cart.filter(x => x.id !== id);
  updateCartUI(); saveCartToLocalStorage();
}

function computeTotals(){
  const subtotal = cart.reduce((s,i) => s + i.price * i.quantity, 0);
  const tax = isTaxExempt ? 0 : Math.round(subtotal * taxRate / 100);
  const final = Math.max(0, subtotal + tax - discountAmount);
  subtotalSpan.textContent = `₱${subtotal}`;
  taxSpan.textContent = `₱${tax}`;
  discountSpan.textContent = `-₱${discountAmount}`;
  grandTotalSpan.textContent = `₱${final}`;
  updateCashPreview();
  // Update FAB
  const count = cart.reduce((s,i) => s + i.quantity, 0);
  cartFabCount.textContent = count;
  cartFabTotal.textContent = `₱${final}`;
  cartFab.classList.toggle('empty', count === 0);
}

function updateCashPreview(){
  const total = parseInt(grandTotalSpan.textContent.replace('₱','')) || 0;
  const cash = parseInt(cashGivenInput.value) || 0;
  if(cash >= total && total > 0){
    changeDueSpan.textContent = `₱${cash - total}`;
    changeDueArea.style.display = 'flex';
    insufficientError.style.display = 'none';
  }else{
    changeDueArea.style.display = 'none';
    insufficientError.style.display = (total > 0 && cash > 0) ? 'block' : 'none';
  }
}
cashGivenInput.addEventListener('input', updateCashPreview);

/* ---------- Toast ---------- */
function showToast(msg, onUndo){
  const wrap = document.getElementById('toastWrap');
  const t = document.createElement('div');
  t.className = 'toast';
  t.innerHTML = `<span>${escapeHtml(msg)}</span>${onUndo ? '<button class="toast-undo">Undo</button>' : ''}`;
  if(onUndo){
    t.querySelector('.toast-undo').onclick = (ev) => { ev.stopPropagation(); onUndo(); t.remove(); };
  }
  wrap.appendChild(t);
  setTimeout(() => { if(t.parentNode) t.remove(); }, onUndo ? 3500 : 2200);
}

/* ---------- Cart modal open/close ---------- */
cartFab.addEventListener('click', () => {
  document.getElementById('cartModal').classList.add('open');
});
$('closeCartModal').onclick = () => document.getElementById('cartModal').classList.remove('open');
$('cartModal').addEventListener('click', e => {
  if(e.target.id === 'cartModal') e.target.classList.remove('open');
});

/* ---------- Chips ---------- */
discountChip.onclick = () => {
  const val = parseInt(prompt('Discount amount (₱):'));
  if(!isNaN(val) && val >= 0){
    discountAmount = val;
    discountChip.classList.toggle('active', val > 0);
    computeTotals(); saveCartToLocalStorage();
  }
};
taxExemptChip.onclick = () => {
  isTaxExempt = !isTaxExempt;
  taxExemptChip.classList.toggle('active', isTaxExempt);
  computeTotals(); saveCartToLocalStorage();
};
$('clearCartBtn').onclick = () => {
  if(confirm('Clear cart and discount?')){
    cart = []; discountAmount = 0; isTaxExempt = false;
    discountChip.classList.remove('active');
    taxExemptChip.classList.remove('active');
    updateCartUI(); saveCartToLocalStorage();
  }
};

/* ---------- Payment ---------- */
completePaymentBtn.onclick = async () => {
  if(paymentLocked) return;
  const total = parseInt(grandTotalSpan.textContent.replace('₱',''));
  const cashGiven = parseInt(cashGivenInput.value);
  if(isNaN(cashGiven) || cashGiven < total){ showToast('Insufficient cash'); return; }
  paymentLocked = true;
  completePaymentBtn.disabled = true;
  try{
    const change = cashGiven - total;
    const subtotal = parseInt(subtotalSpan.textContent.replace('₱',''));
    const tax = parseInt(taxSpan.textContent.replace('₱',''));
    const tid = 'MRT-' + Math.floor(Math.random()*100000);
    await fetch('/api/transaction', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ transactionId: tid, items: cart, subtotal, tax, total, method: 'cash', cash_given: cashGiven, change_due: change })
    });
    document.getElementById('receiptId').textContent = tid;
    document.getElementById('receiptItems').innerHTML = cart.map(i =>
      `<div style="display:flex;justify-content:space-between;padding:2px 0;"><span>${escapeHtml(i.name)} × ${i.quantity}</span><span class="mono">₱${i.price * i.quantity}</span></div>`).join('');
    document.getElementById('receiptCashGiven').textContent = `₱${cashGiven}`;
    document.getElementById('receiptChange').textContent = `₱${change}`;
    document.getElementById('receiptTotal').textContent = `₱${total}`;
    // Close cart modal, show success
    document.getElementById('cartModal').classList.remove('open');
    document.getElementById('successModal').classList.add('open');
    cart = []; discountAmount = 0; isTaxExempt = false;
    discountChip.classList.remove('active');
    taxExemptChip.classList.remove('active');
    updateCartUI(); clearLocalStorageCart();
    cashGivenInput.value = '';
    changeDueArea.style.display = 'none';
    insufficientError.style.display = 'none';
  }catch(e){
    showToast('Payment failed — try again');
  }finally{
    paymentLocked = false;
    completePaymentBtn.disabled = false;
  }
};
document.getElementById('newTransactionBtn').onclick = () => {
  document.getElementById('successModal').classList.remove('open');
};

/* ---------- Search ---------- */
document.getElementById('searchInput').addEventListener('input', (e) => {
  searchQuery = e.target.value.toLowerCase();
  renderProducts();
});

/* ---------- Manage Products ---------- */
document.getElementById('manageProductsBtn').onclick = () => {
  renderManageList();
  document.getElementById('productModal').classList.add('open');
};
document.getElementById('closeProductModal').onclick = () => {
  document.getElementById('productModal').classList.remove('open');
};
document.getElementById('productModal').addEventListener('click', (e) => {
  if(e.target.id === 'productModal') e.target.classList.remove('open');
});

async function renderManageList(){
  const r = await fetch('/api/products');
  const data = await r.json();
  const list = document.getElementById('manageProductsList');
  if(!data.length){
    list.innerHTML = '<div class="empty">No products yet</div>';
    return;
  }
  list.innerHTML = data.map(p => `
    <div class="mgmt-row">
      <span class="mgmt-row-name">${escapeHtml(p.name)}</span>
      <input type="number" step="1" inputmode="decimal" value="${Math.round(p.price)}" class="input mgmt-row-price" data-id="${p.id}" aria-label="Price for ${escapeHtml(p.name)}">
      <button class="icon-btn primary" data-action="save" data-id="${p.id}" aria-label="Save price">
        <span class="material-symbols-outlined" style="font-size:20px;">check</span>
      </button>
      <button class="icon-btn" style="color:var(--danger);" data-action="delete" data-id="${p.id}" aria-label="Delete product">
        <span class="material-symbols-outlined" style="font-size:20px;">delete</span>
      </button>
    </div>`).join('');

  list.querySelectorAll('button[data-action="save"]').forEach(btn => {
    btn.onclick = async () => {
      const id = btn.dataset.id;
      const input = list.querySelector(`.mgmt-row-price[data-id="${id}"]`);
      const price = parseInt(input.value);
      if(isNaN(price)){ showToast('Enter a valid price'); return; }
      await fetch(`/api/products/${id}`, { method:'PUT', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ price }) });
      await fetchProducts(); await renderManageList();
      showToast('Price updated');
    };
  });
  list.querySelectorAll('button[data-action="delete"]').forEach(btn => {
    btn.onclick = async () => {
      if(!confirm('Delete this product?')) return;
      const id = btn.dataset.id;
      await fetch(`/api/products/${id}`, { method:'DELETE' });
      await fetchProducts();
      cart = cart.filter(i => i.id !== id);
      updateCartUI(); saveCartToLocalStorage();
      await renderManageList();
      showToast('Product deleted');
    };
  });
}

document.getElementById('addProductBtn').onclick = async () => {
  const id = document.getElementById('newProductId').value.trim();
  const name = document.getElementById('newProductName').value.trim();
  const price = parseInt(document.getElementById('newProductPrice').value);
  if(!id || !name || isNaN(price)){ showToast('Fill all fields'); return; }
  await fetch('/api/products', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ id, name, price }) });
  await fetchProducts(); await renderManageList();
  document.getElementById('newProductId').value = '';
  document.getElementById('newProductName').value = '';
  document.getElementById('newProductPrice').value = '';
  showToast('Product added');
};

function escapeHtml(str){
  return String(str).replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[m]);
}

fetchProducts();
</script>
</body>
</html>
"""
    return render_template_string(pos_html.replace("__BASE_CSS__", BASE_CSS))

# ---------------------------
# ADMIN PAGE
# ---------------------------
@app.route('/admin', methods=['GET'])
@admin_ip_required
def admin_panel():
    admin_html = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Admin — Descalzo Store</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200">
<style>
__BASE_CSS__

.admin-main{
  flex:1;padding:16px 12px;
  padding-bottom:calc(72px + var(--safe-b) + 24px);
  max-width:880px;width:100%;margin:0 auto;
}
@media (min-width:1024px){.admin-main{padding-bottom:32px;padding-top:24px;}}
.section{display:none;}
.section.active{display:block;animation:fadeIn .2s;}
.section-head{margin-bottom:16px;}
.section-title{font-size:20px;font-weight:800;margin:0 0 4px;}
.section-sub{font-size:13px;color:var(--text-2);margin:0;}

.stat-card{padding:16px;border-radius:var(--r-lg);background:var(--primary-soft);color:var(--primary);text-align:center;margin-bottom:16px;}
.stat-label{font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.05em;opacity:.8;}
.stat-value{font-size:32px;font-weight:800;line-height:1.1;margin-top:4px;font-variant-numeric:tabular-nums;}

.search-row{display:flex;gap:8px;margin-bottom:14px;}
.search-row .input{flex:1;}

.prod-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-lg);padding:12px;margin-bottom:10px;box-shadow:var(--shadow-1);}
.prod-head{display:flex;align-items:center;gap:8px;margin-bottom:8px;}
.prod-id{font-size:11px;color:var(--text-3);font-weight:600;font-family:ui-monospace,monospace;}
.prod-name{font-size:15px;font-weight:700;flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.prod-price{font-size:14px;font-weight:700;color:var(--primary);font-variant-numeric:tabular-nums;white-space:nowrap;}
.prod-actions{display:flex;gap:6px;}
.prod-actions .btn{min-height:40px;font-size:13px;padding:0 14px;}

.analytics-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-lg);padding:20px;box-shadow:var(--shadow-1);}
.date-chip{display:inline-block;background:var(--surface-2);color:var(--text-2);padding:4px 12px;border-radius:var(--r-full);font-size:12px;font-weight:600;margin-bottom:16px;}
.analytics-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px;}
.analytics-stat{padding:16px;border-radius:var(--r-md);text-align:center;}
.analytics-stat.qty{background:var(--primary-soft);color:var(--primary);}
.analytics-stat.val{background:var(--success-soft);color:var(--success);}
.analytics-stat .label{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.05em;opacity:.85;}
.analytics-stat .num{font-size:24px;font-weight:800;margin-top:4px;font-variant-numeric:tabular-nums;}

.theme-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px;}
.theme-btn{
  padding:16px 12px;border-radius:var(--r-md);background:var(--surface);
  border:2px solid var(--border);display:flex;flex-direction:column;
  align-items:center;gap:6px;font-size:13px;font-weight:600;
  transition:border-color .15s,background .15s;min-height:80px;
}
.theme-btn:hover{border-color:var(--border-strong);}
.theme-btn.active{border-color:var(--primary);background:var(--primary-soft);color:var(--primary);}
.theme-btn .material-symbols-outlined{font-size:24px;}

.bottom-nav{
  position:fixed;left:0;right:0;bottom:0;z-index:30;
  background:color-mix(in srgb,var(--surface) 94%,transparent);
  backdrop-filter:saturate(180%) blur(12px);-webkit-backdrop-filter:saturate(180%) blur(12px);
  border-top:1px solid var(--border);display:grid;grid-template-columns:repeat(3,1fr);
  padding-bottom:var(--safe-b);padding-left:var(--safe-l);padding-right:var(--safe-r);
}
.nav-item{
  min-height:60px;padding:8px 4px;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  gap:2px;color:var(--text-3);font-size:11px;font-weight:600;transition:color .15s;
}
.nav-item .material-symbols-outlined{font-size:24px;}
.nav-item.active{color:var(--primary);}
.nav-item:active{background:var(--surface-2);}

@media (min-width:1024px){
  .bottom-nav{
    position:static;margin:0 auto;max-width:880px;background:transparent;
    backdrop-filter:none;-webkit-backdrop-filter:none;border:none;
    border-bottom:1px solid var(--border);padding:0;border-radius:0;
    display:flex;gap:4px;
  }
  .nav-item{flex:1;flex-direction:row;gap:8px;font-size:14px;min-height:48px;padding:0 16px;border-radius:var(--r-md);}
  .nav-item.active{background:var(--primary-soft);}
}
</style>
</head>
<body>
<div class="app">
  <header class="app-header">
    <a href="/" class="icon-btn" aria-label="Back to POS">
      <span class="material-symbols-outlined">arrow_back</span>
    </a>
    <div class="brand" style="flex:1;"><div class="brand-name">Admin</div></div>
    <div class="badge badge-primary">
      <span class="material-symbols-outlined" style="font-size:14px;">verified_user</span> Admin
    </div>
  </header>

  <nav class="bottom-nav" role="tablist">
    <button class="nav-item active" data-tab="inventory" role="tab">
      <span class="material-symbols-outlined">inventory_2</span><span>Inventory</span>
    </button>
    <button class="nav-item" data-tab="analytics" role="tab">
      <span class="material-symbols-outlined">bar_chart</span><span>Sales</span>
    </button>
    <button class="nav-item" data-tab="theme" role="tab">
      <span class="material-symbols-outlined">palette</span><span>Theme</span>
    </button>
  </nav>

  <main class="admin-main">
    <section id="inventorySection" class="section active">
      <div class="section-head row-between" style="align-items:flex-start;">
        <div>
          <h2 class="section-title">Inventory</h2>
          <p class="section-sub">Add, edit prices, or delete products</p>
        </div>
        <button id="openAddModal" class="btn btn-primary btn-sm">
          <span class="material-symbols-outlined" style="font-size:18px;">add</span> Add
        </button>
      </div>
      <div class="stat-card">
        <div class="stat-label">Total Products</div>
        <div class="stat-value" id="statTotalProducts">—</div>
      </div>
      <div class="search-row">
        <input type="search" id="searchProducts" class="input" placeholder="Search by name or ID…" inputmode="search">
        <button id="clearSearchBtn" class="btn btn-secondary" style="padding:0 16px;">Clear</button>
      </div>
      <div id="productsList"></div>
    </section>

    <section id="analyticsSection" class="section">
      <div class="section-head">
        <h2 class="section-title">Today's Sales</h2>
        <p class="section-sub">Real-time overview of today's activity</p>
      </div>
      <div class="analytics-card">
        <div class="date-chip" id="salesDateDisplay">—</div>
        <div class="analytics-grid">
          <div class="analytics-stat qty"><div class="label">Items Sold</div><div class="num" id="totalQuantityDisplay">0</div></div>
          <div class="analytics-stat val"><div class="label">Revenue</div><div class="num" id="totalSalesDisplay">₱0</div></div>
        </div>
        <button onclick="loadAnalytics()" class="btn btn-secondary btn-block">
          <span class="material-symbols-outlined" style="font-size:18px;">refresh</span> Refresh
        </button>
      </div>
    </section>

    <section id="themeSection" class="section">
      <div class="section-head">
        <h2 class="section-title">Theme</h2>
        <p class="section-sub">Colour scheme for the POS</p>
      </div>
      <div class="theme-grid">
        <button class="theme-btn" data-set-theme="light"><span class="material-symbols-outlined">light_mode</span> Light</button>
        <button class="theme-btn" data-set-theme="dark"><span class="material-symbols-outlined">dark_mode</span> Dark</button>
        <button class="theme-btn" data-set-theme="blue"><span class="material-symbols-outlined">water_drop</span> Blue</button>
        <button class="theme-btn" data-set-theme="black"><span class="material-symbols-outlined">contrast</span> Black</button>
      </div>
      <div class="card" style="padding:14px;">
        <p class="text-sm text-muted" style="margin:0;">Refresh the POS after saving to apply the theme.</p>
        <div id="themeMsg" style="margin-top:8px;font-size:13px;font-weight:600;color:var(--success);"></div>
      </div>
    </section>
  </main>
</div>

<div id="addProductModal" class="modal" role="dialog" aria-modal="true">
  <div class="modal-card">
    <div class="modal-head">
      <h3 class="modal-title">Add New Product</h3>
      <button onclick="closeAddProductModal()" class="icon-btn" aria-label="Close">
        <span class="material-symbols-outlined">close</span>
      </button>
    </div>
    <div class="modal-body">
      <div class="field" style="margin-bottom:12px;">
        <label class="field-label" for="newId">Product ID</label>
        <input type="text" id="newId" class="input" placeholder="e.g. 001" autocomplete="off">
      </div>
      <div class="field" style="margin-bottom:12px;">
        <label class="field-label" for="newName">Name</label>
        <input type="text" id="newName" class="input" placeholder="e.g. Coke 1.5L" autocomplete="off">
      </div>
      <div class="field">
        <label class="field-label" for="newPrice">Price (₱)</label>
        <input type="number" id="newPrice" class="input" placeholder="0" step="1" inputmode="decimal">
      </div>
    </div>
    <div class="modal-foot">
      <button onclick="closeAddProductModal()" class="btn btn-secondary btn-block">Cancel</button>
      <button onclick="addProduct()" class="btn btn-primary btn-block">Add Product</button>
    </div>
  </div>
</div>

<script>
'use strict';
async function loadTheme(){
  try{
    const r = await fetch('/api/theme'); const d = await r.json();
    const t = d.theme || 'light';
    document.documentElement.setAttribute('data-theme', t);
    document.querySelectorAll('.theme-btn').forEach(b => b.classList.toggle('active', b.dataset.setTheme === t));
  }catch(e){}
}
loadTheme();

let allProducts = [];
let currentFiltered = [];

async function fetchProducts(){
  const r = await fetch('/api/admin/products');
  allProducts = await r.json();
  currentFiltered = [...allProducts];
  renderProductList(currentFiltered);
  await fetchStats();
}

function renderProductList(list){
  const el = document.getElementById('productsList');
  if(!list.length){
    el.innerHTML = '<div class="empty"><span class="material-symbols-outlined empty-icon">inventory_2</span>No products</div>';
    return;
  }
  el.innerHTML = list.map(p => `
    <div class="prod-card">
      <div class="prod-head">
        <span class="prod-id">#${escapeHtml(String(p.id))}</span>
        <span class="prod-name">${escapeHtml(p.name)}</span>
        <span class="prod-price">₱${p.price}</span>
      </div>
      <div class="prod-actions">
        <button class="btn btn-secondary btn-sm" data-action="edit" data-id="${p.id}" data-price="${p.price}">
          <span class="material-symbols-outlined" style="font-size:16px;">edit</span> Price
        </button>
        <button class="btn btn-danger btn-sm" data-action="delete" data-id="${p.id}">
          <span class="material-symbols-outlined" style="font-size:16px;">delete</span> Delete
        </button>
      </div>
    </div>`).join('');
  el.querySelectorAll('button[data-action="edit"]').forEach(btn => {
    btn.onclick = () => editPrice(btn.dataset.id, btn.dataset.price);
  });
  el.querySelectorAll('button[data-action="delete"]').forEach(btn => {
    btn.onclick = () => deleteProduct(btn.dataset.id);
  });
}

async function editPrice(id, current){
  const newPrice = prompt(`New price for #${id} (current: ₱${current}):`, current);
  if(newPrice === null) return;
  const val = parseInt(newPrice);
  if(isNaN(val)){ alert('Enter a valid number'); return; }
  await fetch(`/api/admin/products/${id}`, {
    method: 'PUT', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ price: val })
  });
  await fetchProducts();
}
async function deleteProduct(id){
  if(!confirm('Delete this product?')) return;
  await fetch(`/api/admin/products/${id}`, { method: 'DELETE' });
  await fetchProducts();
}
async function addProduct(){
  const id = document.getElementById('newId').value.trim();
  const name = document.getElementById('newName').value.trim();
  const price = parseInt(document.getElementById('newPrice').value);
  if(!id || !name || isNaN(price)){ alert('Fill all fields with a valid price'); return; }
  await fetch('/api/admin/products', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ id, name, price })
  });
  closeAddProductModal();
  fetchProducts();
}
async function fetchStats(){
  const r = await fetch('/api/admin/stats');
  const d = await r.json();
  document.getElementById('statTotalProducts').textContent = d.total_products ?? '—';
}
async function loadAnalytics(){
  const r = await fetch('/api/sales/today');
  const d = await r.json();
  document.getElementById('salesDateDisplay').textContent = d.date;
  document.getElementById('totalQuantityDisplay').textContent = d.total_quantity || 0;
  document.getElementById('totalSalesDisplay').textContent = `₱${d.total_sales || 0}`;
}
async function setTheme(theme){
  const r = await fetch('/admin/set_theme', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ theme })
  });
  if(r.ok){
    document.documentElement.setAttribute('data-theme', theme);
    document.querySelectorAll('.theme-btn').forEach(b => b.classList.toggle('active', b.dataset.setTheme === theme));
    document.getElementById('themeMsg').textContent = '✓ Saved — refresh POS to apply';
    setTimeout(()=>{ document.getElementById('themeMsg').textContent = ''; }, 3000);
  }
}
document.querySelectorAll('.theme-btn').forEach(b => b.onclick = () => setTheme(b.dataset.setTheme));

function openAddProductModal(){ document.getElementById('addProductModal').classList.add('open'); }
function closeAddProductModal(){ document.getElementById('addProductModal').classList.remove('open'); }
document.getElementById('addProductModal').addEventListener('click', e => {
  if(e.target.id === 'addProductModal') closeAddProductModal();
});

function showSection(name){
  ['inventory','analytics','theme'].forEach(s => {
    document.getElementById(s+'Section').classList.toggle('active', s === name);
  });
  document.querySelectorAll('.nav-item').forEach(b => b.classList.toggle('active', b.dataset.tab === name));
  if(name === 'inventory') fetchProducts();
  if(name === 'analytics') loadAnalytics();
}
document.querySelectorAll('.nav-item').forEach(b => { b.onclick = () => showSection(b.dataset.tab); });

document.getElementById('openAddModal').onclick = openAddProductModal;
document.getElementById('clearSearchBtn').onclick = () => {
  document.getElementById('searchProducts').value = '';
  currentFiltered = [...allProducts];
  renderProductList(currentFiltered);
};
document.getElementById('searchProducts').addEventListener('input', e => {
  const q = e.target.value.toLowerCase().trim();
  currentFiltered = !q ? [...allProducts] : allProducts.filter(p =>
    p.name.toLowerCase().includes(q) || String(p.id).includes(q)
  );
  renderProductList(currentFiltered);
});

function escapeHtml(str){
  return String(str).replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[m]);
}

fetchProducts();
</script>
</body>
</html>
"""
    return render_template_string(admin_html.replace("__BASE_CSS__", BASE_CSS))

# ---------------------------
# Admin API endpoints
# ---------------------------
@app.route('/api/admin/stats', methods=['GET'])
@admin_ip_required
def admin_stats():
    try:
        resp = supabase.table('product').select('id', count='exact').execute()
        return jsonify({"total_products": len(resp.data)})
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
        return jsonify({"date": now_ph.strftime("%B %d, %Y"), "total_sales": total_sales, "total_quantity": total_quantity})
    except Exception as e:
        return jsonify({"date": ph_now().strftime("%B %d, %Y"), "total_sales": 0, "total_quantity": 0}), 200

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)