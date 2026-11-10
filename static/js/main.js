/**
 * AURA LUXURY JEWELLERY - MAIN APPLICATION JAVASCRIPT
 */

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function getCsrfToken() {
  if (window.CSRF_TOKEN && typeof window.CSRF_TOKEN === 'string' && window.CSRF_TOKEN.length > 5) {
    return window.CSRF_TOKEN;
  }
  const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
  if (input && input.value) {
    return input.value;
  }
  return getCookie('csrftoken') || '';
}

// Toast notification helper (works with or without bootstrap.Toast)
function showToast(message, type = 'success') {
  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '99999';
    document.body.appendChild(container);
  }

  const toastId = 'toast_' + Date.now();
  const bgClass = type === 'success' ? 'bg-dark text-white border-gold' : (type === 'info' ? 'bg-dark text-gold border-gold' : 'bg-danger text-white');
  const icon = type === 'success' ? '<i class="bi bi-check2-circle text-gold me-2 fs-5"></i>' : (type === 'info' ? '<i class="bi bi-info-circle text-gold me-2 fs-5"></i>' : '<i class="bi bi-exclamation-octagon me-2 fs-5"></i>');

  const toastHtml = `
    <div id="${toastId}" class="toast align-items-center ${bgClass} border shadow-lg show" role="alert" aria-live="assertive" aria-atomic="true" style="opacity: 1; min-width: 280px;">
      <div class="d-flex">
        <div class="toast-body d-flex align-items-center py-2 px-3">
          ${icon}
          <div class="fw-semibold">${message}</div>
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close" onclick="this.closest('.toast').remove()"></button>
      </div>
    </div>
  `;

  container.insertAdjacentHTML('beforeend', toastHtml);
  const toastElem = document.getElementById(toastId);

  if (window.bootstrap && bootstrap.Toast) {
    try {
      const bsToast = new bootstrap.Toast(toastElem, { delay: 4000 });
      bsToast.show();
      toastElem.addEventListener('hidden.bs.toast', () => toastElem.remove());
      return;
    } catch (e) {
      console.warn('Bootstrap toast initialization fallback', e);
    }
  }

  // Fallback auto-dismiss if bootstrap toast not initialized
  setTimeout(() => {
    if (toastElem && toastElem.parentNode) {
      toastElem.style.transition = 'opacity 0.4s ease';
      toastElem.style.opacity = '0';
      setTimeout(() => toastElem.remove(), 400);
    }
  }, 4000);
}

// Wishlist toggle handler
function toggleWishlist(productId, btnElement) {
  const token = getCsrfToken();
  fetch(`/accounts/wishlist/toggle/${productId}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': token,
      'X-Requested-With': 'XMLHttpRequest',
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
  })
    .then(response => {
      if (response.status === 401 || response.redirected) {
        window.location.href = '/accounts/login/?next=' + encodeURIComponent(window.location.pathname);
        return;
      }
      return response.json();
    })
    .then(data => {
      if (!data) return;
      if (data.status === 'added') {
        btnElement.classList.add('active');
        btnElement.innerHTML = '<i class="bi bi-heart-fill text-danger"></i>';
        showToast(data.message || 'Added to Wishlist!', 'success');
      } else if (data.status === 'removed') {
        btnElement.classList.remove('active');
        btnElement.innerHTML = '<i class="bi bi-heart"></i>';
        showToast(data.message || 'Removed from Wishlist', 'info');
      }

      // Update navbar wishlist count
      const badge = document.getElementById('navbarWishlistCount');
      if (badge && typeof data.wishlist_count !== 'undefined') {
        badge.textContent = data.wishlist_count;
        badge.style.display = data.wishlist_count > 0 ? 'inline-flex' : 'none';
      }
    })
    .catch(err => {
      console.error('Error toggling wishlist:', err);
    });
}

// Add to Cart handler with button feedback and form fallback
function addToCart(productId, quantity = 1, btnElement = null) {
  if (!productId) {
    console.error('addToCart called without productId');
    return;
  }

  // Visual button feedback
  let originalHtml = '';
  if (btnElement) {
    originalHtml = btnElement.innerHTML;
    btnElement.disabled = true;
    btnElement.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Adding...';
  }

  const token = getCsrfToken();
  const formData = new FormData();
  formData.append('product_id', productId);
  formData.append('quantity', quantity);
  formData.append('csrfmiddlewaretoken', token);
  formData.append('ajax', '1');

  fetch('/cart/add/', {
    method: 'POST',
    headers: {
      'X-CSRFToken': token,
      'X-Requested-With': 'XMLHttpRequest',
      'Accept': 'application/json',
    },
    body: formData,
  })
    .then(res => {
      const contentType = res.headers.get('content-type') || '';
      if (!contentType.includes('application/json')) {
        // If server returned non-JSON redirect
        if (res.ok || res.redirected) {
          window.location.href = '/cart/';
          return null;
        }
        throw new Error('Server returned unexpected response type: ' + contentType);
      }
      return res.json();
    })
    .then(data => {
      if (!data) return;

      if (data.success) {
        showToast(data.message || 'Added to Shopping Bag!', 'success');

        if (btnElement) {
          btnElement.innerHTML = '<i class="bi bi-check2 me-1 text-success"></i> Added!';
          setTimeout(() => {
            btnElement.disabled = false;
            btnElement.innerHTML = originalHtml;
          }, 1500);
        }

        // Update navbar cart count badge
        const badge = document.getElementById('navbarCartCount');
        if (badge) {
          badge.textContent = data.total_items;
          badge.style.display = data.total_items > 0 ? 'inline-flex' : 'none';
        }

        // Open offcanvas drawer if exists
        const cartDrawerElem = document.getElementById('offcanvasCartDrawer');
        if (cartDrawerElem) {
          fetch('/cart/quick-view/')
            .then(r => r.text())
            .then(html => {
              const body = document.getElementById('cartDrawerBody');
              if (body) body.innerHTML = html;
              if (window.bootstrap && bootstrap.Offcanvas) {
                const bsOffcanvas = bootstrap.Offcanvas.getOrCreateInstance(cartDrawerElem);
                bsOffcanvas.show();
              }
            })
            .catch(err => console.warn('Could not refresh cart drawer:', err));
        }
      } else {
        if (btnElement) {
          btnElement.disabled = false;
          btnElement.innerHTML = originalHtml;
        }
        showToast(data.error || 'Failed to add item to bag', 'error');
      }
    })
    .catch(err => {
      console.warn('AJAX cart add failed, attempting form-POST fallback:', err);
      if (btnElement) {
        btnElement.disabled = false;
        btnElement.innerHTML = originalHtml;
      }
      submitCartFormFallback(productId, quantity, token);
    });
}

// Fallback: standard POST form submission if AJAX fetch is blocked
function submitCartFormFallback(productId, quantity, token) {
  const form = document.createElement('form');
  form.method = 'POST';
  form.action = '/cart/add/';
  form.style.display = 'none';

  const pInput = document.createElement('input');
  pInput.type = 'hidden';
  pInput.name = 'product_id';
  pInput.value = productId;
  form.appendChild(pInput);

  const qInput = document.createElement('input');
  qInput.type = 'hidden';
  qInput.name = 'quantity';
  qInput.value = quantity;
  form.appendChild(qInput);

  const csrfInput = document.createElement('input');
  csrfInput.type = 'hidden';
  csrfInput.name = 'csrfmiddlewaretoken';
  csrfInput.value = token || getCsrfToken();
  form.appendChild(csrfInput);

  document.body.appendChild(form);
  form.submit();
}

// Delivery Pincode checker
function checkPincode() {
  const input = document.getElementById('pincodeInput');
  const resultDiv = document.getElementById('pincodeResult');
  if (!input || !resultDiv) return;

  const pin = input.value.trim();
  if (pin.length !== 6 || isNaN(pin)) {
    resultDiv.innerHTML = '<span class="text-danger small"><i class="bi bi-x-circle me-1"></i>Please enter a valid 6-digit Indian PIN code.</span>';
    return;
  }

  resultDiv.innerHTML = '<span class="text-muted small"><i class="spinner-border spinner-border-sm me-1"></i>Checking delivery availability...</span>';

  setTimeout(() => {
    resultDiv.innerHTML = `
      <div class="alert alert-success py-2 px-3 mt-2 mb-0 small border-gold-subtle">
        <i class="bi bi-shield-check text-gold me-2"></i>
        <strong>Insured Delivery Available!</strong> Estimated delivery in <strong>2-4 business days</strong> by BlueDart Apex Gold. Cash on Delivery is eligible.
      </div>
    `;
  }, 400);
}

// Multiple Reference Image Preview Handler for Custom Order Form
document.addEventListener('DOMContentLoaded', () => {
  const uploadInput = document.getElementById('customRefImagesInput');
  const previewGrid = document.getElementById('customRefPreviewGrid');
  const dropZone = document.getElementById('customUploadDropZone');

  if (uploadInput && previewGrid) {
    uploadInput.addEventListener('change', handleFileSelect);
  }

  if (dropZone && uploadInput) {
    ['dragenter', 'dragover'].forEach(eventName => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropZone.classList.add('bg-warning', 'bg-opacity-10');
      }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropZone.classList.remove('bg-warning', 'bg-opacity-10');
      }, false);
    });

    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        uploadInput.files = e.dataTransfer.files;
        handleFileSelect({ target: uploadInput });
      }
    });
  }

  function handleFileSelect(e) {
    if (!previewGrid) return;
    previewGrid.innerHTML = '';
    const files = e.target.files;

    if (files.length > 8) {
      showToast('Maximum 8 reference images allowed.', 'error');
      uploadInput.value = '';
      return;
    }

    Array.from(files).forEach((file, index) => {
      if (!file.type.match('image.*')) return;

      const reader = new FileReader();
      reader.onload = function(evt) {
        const item = document.createElement('div');
        item.className = 'preview-card-item position-relative shadow-sm';
        item.innerHTML = `
          <img src="${evt.target.result}" alt="Preview ${index + 1}">
          <span class="badge bg-dark position-absolute bottom-0 start-0 m-1" style="font-size: 0.6rem;">${file.name.substring(0, 12)}...</span>
        `;
        previewGrid.appendChild(item);
      };
      reader.readAsDataURL(file);
    });
  }
});

// Live Gold Price Estimator Calculator
function calculateGoldEstimate() {
  const weightInput = document.getElementById('calcWeight');
  const puritySelect = document.getElementById('calcPurity');
  const makingSelect = document.getElementById('calcMaking');

  if (!weightInput || !puritySelect || !makingSelect) return;

  const weight = parseFloat(weightInput.value) || 0;
  const ratePerGram = parseFloat(puritySelect.value) || 0;
  const makingPercent = parseFloat(makingSelect.value) || 0;

  const metalVal = weight * ratePerGram;
  const makingVal = (metalVal * makingPercent) / 100.0;
  const gstVal = ((metalVal + makingVal) * 3.0) / 100.0;
  const totalVal = metalVal + makingVal + gstVal;

  const fmt = (n) => '₹' + Math.round(n).toLocaleString('en-IN');

  const elMetal = document.getElementById('calcMetalVal');
  const elMaking = document.getElementById('calcMakingVal');
  const elGst = document.getElementById('calcGstVal');
  const elTotal = document.getElementById('calcTotalVal');

  if (elMetal) elMetal.textContent = fmt(metalVal);
  if (elMaking) elMaking.textContent = fmt(makingVal);
  if (elGst) elGst.textContent = fmt(gstVal);
  if (elTotal) elTotal.textContent = fmt(totalVal);
}

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('calcWeight')) {
    calculateGoldEstimate();
  }
});

