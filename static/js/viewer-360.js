/**
 * AURA LUXURY JEWELLERY - 360° INTERACTIVE PRODUCT ROTATION VIEWER
 * Features:
 * - Multi-angle actual frame sequence navigation
 * - Mouse drag left/right rotation
 * - Mobile touch swipe rotation
 * - Autoplay / Pause 360 rotation
 * - Scrubbing range slider with real-time degree and frame indicators
 * - Zoom in / Zoom out controls
 * - Fullscreen mode support
 */

class JewelleryViewer360 {
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    if (!this.container) return;

    this.canvasArea = this.container.querySelector('.viewer-360-canvas-area');
    this.imgElement = this.container.querySelector('.viewer-360-image');
    this.scrubber = this.container.querySelector('.viewer-scrubber-slider');
    this.frameDisplay = this.container.querySelector('.viewer-frame-display');
    this.playBtn = this.container.querySelector('.btn-360-play');
    this.zoomInBtn = this.container.querySelector('.btn-360-zoom-in');
    this.zoomOutBtn = this.container.querySelector('.btn-360-zoom-out');
    this.fullscreenBtn = this.container.querySelector('.btn-360-fullscreen');
    this.resetBtn = this.container.querySelector('.btn-360-reset');

    // Read frames array from data attribute
    const framesData = this.container.getAttribute('data-frames');
    this.frames = framesData ? JSON.parse(framesData) : [];
    this.totalFrames = this.frames.length || 24;
    this.currentIndex = 0;

    // Drag / Touch state
    this.isDragging = false;
    this.startX = 0;
    this.dragThreshold = options.dragSensitivity || 10; // Pixels per frame shift

    // Auto-rotate state
    this.isPlaying = false;
    this.playInterval = null;
    this.playbackSpeed = options.speed || 80; // ms per frame

    // Zoom state
    this.currentZoom = 1.0;
    this.minZoom = 0.8;
    this.maxZoom = 2.5;

    // Preload image objects in memory for buttery smooth dragging
    this.preloadedImages = [];
    this.preloadFrames();

    this.bindEvents();
    this.updateViewer();
  }

  preloadFrames() {
    this.frames.forEach((src, idx) => {
      const img = new Image();
      img.src = src;
      this.preloadedImages.push(img);
    });
  }

  bindEvents() {
    // Mouse events
    if (this.canvasArea) {
      this.canvasArea.addEventListener('mousedown', (e) => this.onStartDrag(e.clientX));
      window.addEventListener('mousemove', (e) => this.onDrag(e.clientX));
      window.addEventListener('mouseup', () => this.onEndDrag());

      // Touch events
      this.canvasArea.addEventListener('touchstart', (e) => {
        if (e.touches.length === 1) {
          this.onStartDrag(e.touches[0].clientX);
        }
      }, { passive: true });

      window.addEventListener('touchmove', (e) => {
        if (this.isDragging && e.touches.length === 1) {
          this.onDrag(e.touches[0].clientX);
        }
      }, { passive: true });

      window.addEventListener('touchend', () => this.onEndDrag());

      // Wheel Zoom
      this.canvasArea.addEventListener('wheel', (e) => {
        e.preventDefault();
        if (e.deltaY < 0) {
          this.zoom(0.15);
        } else {
          this.zoom(-0.15);
        }
      }, { passive: false });
    }

    // Scrubber slider
    if (this.scrubber) {
      this.scrubber.max = this.totalFrames - 1;
      this.scrubber.addEventListener('input', (e) => {
        this.pause();
        this.currentIndex = parseInt(e.target.value, 10);
        this.updateViewer();
      });
    }

    // Play / Pause button
    if (this.playBtn) {
      this.playBtn.addEventListener('click', () => this.togglePlay());
    }

    // Zoom controls
    if (this.zoomInBtn) {
      this.zoomInBtn.addEventListener('click', () => this.zoom(0.25));
    }
    if (this.zoomOutBtn) {
      this.zoomOutBtn.addEventListener('click', () => this.zoom(-0.25));
    }
    if (this.resetBtn) {
      this.resetBtn.addEventListener('click', () => this.resetView());
    }

    // Fullscreen button
    if (this.fullscreenBtn) {
      this.fullscreenBtn.addEventListener('click', () => this.toggleFullscreen());
    }
  }

  onStartDrag(clientX) {
    this.pause();
    this.isDragging = true;
    this.startX = clientX;
  }

  onDrag(clientX) {
    if (!this.isDragging) return;
    const deltaX = clientX - this.startX;

    if (Math.abs(deltaX) >= this.dragThreshold) {
      const framesToMove = Math.floor(deltaX / this.dragThreshold);
      this.currentIndex = (this.currentIndex - framesToMove) % this.totalFrames;
      if (this.currentIndex < 0) this.currentIndex += this.totalFrames;

      this.startX = clientX;
      this.updateViewer();
    }
  }

  onEndDrag() {
    this.isDragging = false;
  }

  togglePlay() {
    if (this.isPlaying) {
      this.pause();
    } else {
      this.play();
    }
  }

  play() {
    this.isPlaying = true;
    if (this.playBtn) {
      this.playBtn.innerHTML = '<i class="bi bi-pause-fill"></i>';
      this.playBtn.title = "Pause 360 Rotation";
    }
    this.playInterval = setInterval(() => {
      this.currentIndex = (this.currentIndex + 1) % this.totalFrames;
      this.updateViewer();
    }, this.playbackSpeed);
  }

  pause() {
    this.isPlaying = false;
    if (this.playInterval) {
      clearInterval(this.playInterval);
      this.playInterval = null;
    }
    if (this.playBtn) {
      this.playBtn.innerHTML = '<i class="bi bi-play-fill"></i>';
      this.playBtn.title = "Play 360 Rotation";
    }
  }

  zoom(factor) {
    this.currentZoom = Math.max(this.minZoom, Math.min(this.maxZoom, this.currentZoom + factor));
    if (this.imgElement) {
      this.imgElement.style.transform = `scale(${this.currentZoom})`;
    }
  }

  resetView() {
    this.pause();
    this.currentZoom = 1.0;
    this.currentIndex = 0;
    if (this.imgElement) {
      this.imgElement.style.transform = 'scale(1.0)';
    }
    this.updateViewer();
  }

  toggleFullscreen() {
    if (!document.fullscreenElement) {
      if (this.container.requestFullscreen) {
        this.container.requestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
  }

  updateViewer() {
    if (this.frames.length > 0 && this.imgElement) {
      const src = this.frames[this.currentIndex];
      if (src && this.imgElement.src !== src) {
        this.imgElement.src = src;
      }
    }

    if (this.scrubber) {
      this.scrubber.value = this.currentIndex;
    }

    if (this.frameDisplay) {
      const degree = Math.round((this.currentIndex / this.totalFrames) * 360);
      this.frameDisplay.textContent = `${degree}° (${this.currentIndex + 1}/${this.totalFrames})`;
    }
  }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  const viewerElement = document.getElementById('jewellery360Viewer');
  if (viewerElement) {
    window.jewelleryViewer = new JewelleryViewer360('jewellery360Viewer');
  }
});

