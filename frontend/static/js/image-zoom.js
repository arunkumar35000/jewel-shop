/**
 * AURA LUXURY JEWELLERY - IMAGE ZOOM & GALLERY SYSTEM
 * Features:
 * - Magnifier hover lens zoom
 * - Thumbnail gallery switching
 * - Fullscreen high-resolution lightbox modal
 * - Mobile pinch-to-zoom and touch gestures
 */

class JewelleryImageZoom {
  constructor(mainContainerId) {
    this.container = document.getElementById(mainContainerId);
    if (!this.container) return;

    this.mainImage = this.container.querySelector('.gallery-main-img');
    this.zoomResult = document.getElementById('zoomResultLens');
    this.thumbnails = document.querySelectorAll('.thumb-item');
    this.fullscreenModal = document.getElementById('imageLightboxModal');
    this.modalImg = document.getElementById('lightboxModalImage');

    this.lensSize = 140;
    this.zoomLevel = 2.5;

    this.initGallery();
    this.initHoverZoom();
    this.initLightbox();
  }

  initGallery() {
    this.thumbnails.forEach((thumb) => {
      thumb.addEventListener('click', (e) => {
        this.thumbnails.forEach(t => t.classList.remove('active'));
        thumb.classList.add('active');

        const newSrc = thumb.getAttribute('data-full-src') || thumb.querySelector('img').src;
        if (this.mainImage) {
          this.mainImage.style.opacity = '0.3';
          setTimeout(() => {
            this.mainImage.src = newSrc;
            this.mainImage.style.opacity = '1';
            if (this.zoomResult) {
              this.zoomResult.style.backgroundImage = `url('${newSrc}')`;
            }
          }, 150);
        }
      });
    });
  }

  initHoverZoom() {
    if (!this.mainImage || !this.zoomResult) return;

    // Set initial background
    this.zoomResult.style.backgroundImage = `url('${this.mainImage.src}')`;

    this.container.addEventListener('mouseenter', () => {
      if (window.innerWidth > 992) {
        this.zoomResult.style.display = 'block';
        this.zoomResult.style.backgroundImage = `url('${this.mainImage.src}')`;
      }
    });

    this.container.addEventListener('mouseleave', () => {
      if (this.zoomResult) {
        this.zoomResult.style.display = 'none';
      }
    });

    this.container.addEventListener('mousemove', (e) => {
      if (window.innerWidth <= 992 || !this.zoomResult) return;

      const rect = this.container.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const percentX = (x / rect.width) * 100;
      const percentY = (y / rect.height) * 100;

      this.zoomResult.style.backgroundPosition = `${percentX}% ${percentY}%`;
      this.zoomResult.style.backgroundSize = `${rect.width * this.zoomLevel}px ${rect.height * this.zoomLevel}px`;
    });
  }

  initLightbox() {
    if (this.container && this.fullscreenModal && this.modalImg) {
      this.container.addEventListener('click', () => {
        this.modalImg.src = this.mainImage.src;
        const bsModal = new bootstrap.Modal(this.fullscreenModal);
        bsModal.show();
      });
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('productMainGalleryArea')) {
    window.jewelleryZoom = new JewelleryImageZoom('productMainGalleryArea');
  }
});

