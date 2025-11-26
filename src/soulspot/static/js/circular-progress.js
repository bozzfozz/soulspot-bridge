/**
 * Circular Progress Indicator
 * 
 * Hey future me - creates beautiful circular progress indicators instead of boring bars!
 * Uses SVG for crisp rendering at any size. The circumference calculation is key - it's
 * based on the circle's radius (2 * PI * r). We animate the stroke-dashoffset to create
 * the progress effect. Way cooler than linear bars and saves space in compact UIs.
 */

class CircularProgress {
    constructor(element, options = {}) {
        this.element = element;
        this.options = {
            size: options.size || 60,
            strokeWidth: options.strokeWidth || 8,
            color: options.color || 'var(--primary)',
            bgColor: options.bgColor || 'rgba(255, 255, 255, 0.1)',
            showPercentage: options.showPercentage !== false,
            animate: options.animate !== false,
            ...options
        };
        
        this.progress = 0;
        this.init();
    }
    
    init() {
        const { size, strokeWidth } = this.options;
        const radius = (size - strokeWidth) / 2;
        const center = size / 2;
        
        // Create SVG
        this.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        this.svg.setAttribute('width', size);
        this.svg.setAttribute('height', size);
        this.svg.setAttribute('viewBox', `0 0 ${size} ${size}`);
        this.svg.style.transform = 'rotate(-90deg)'; // Start from top
        
        // Background circle
        const bgCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        bgCircle.setAttribute('cx', center);
        bgCircle.setAttribute('cy', center);
        bgCircle.setAttribute('r', radius);
        bgCircle.setAttribute('fill', 'none');
        bgCircle.setAttribute('stroke', this.options.bgColor);
        bgCircle.setAttribute('stroke-width', strokeWidth);
        
        // Progress circle
        this.progressCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        this.progressCircle.setAttribute('cx', center);
        this.progressCircle.setAttribute('cy', center);
        this.progressCircle.setAttribute('r', radius);
        this.progressCircle.setAttribute('fill', 'none');
        this.progressCircle.setAttribute('stroke', this.options.color);
        this.progressCircle.setAttribute('stroke-width', strokeWidth);
        this.progressCircle.setAttribute('stroke-linecap', 'round');
        
        // Calculate circumference
        this.circumference = 2 * Math.PI * radius;
        this.progressCircle.style.strokeDasharray = this.circumference;
        this.progressCircle.style.strokeDashoffset = this.circumference;
        
        if (this.options.animate) {
            this.progressCircle.style.transition = 'stroke-dashoffset 0.5s ease';
        }
        
        this.svg.appendChild(bgCircle);
        this.svg.appendChild(this.progressCircle);
        
        // Percentage text
        if (this.options.showPercentage) {
            this.percentageText = document.createElement('span');
            this.percentageText.className = 'circular-progress-percentage';
            this.percentageText.textContent = '0%';
            this.element.appendChild(this.percentageText);
        }
        
        this.element.appendChild(this.svg);
        this.element.classList.add('circular-progress-container');
    }
    
    setProgress(percent) {
        this.progress = Math.max(0, Math.min(100, percent));
        
        const offset = this.circumference - (this.progress / 100 * this.circumference);
        this.progressCircle.style.strokeDashoffset = offset;
        
        if (this.percentageText) {
            this.percentageText.textContent = `${Math.round(this.progress)}%`;
        }
        
        // Update aria-valuenow for accessibility
        this.element.setAttribute('role', 'progressbar');
        this.element.setAttribute('aria-valuenow', Math.round(this.progress));
        this.element.setAttribute('aria-valuemin', '0');
        this.element.setAttribute('aria-valuemax', '100');
    }
    
    getProgress() {
        return this.progress;
    }
    
    destroy() {
        this.element.innerHTML = '';
        this.element.classList.remove('circular-progress-container');
    }
}

// Auto-initialize circular progress from data attributes
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-circular-progress]').forEach(element => {
        const progress = parseFloat(element.dataset.circularProgress) || 0;
        const size = parseInt(element.dataset.size) || 60;
        const color = element.dataset.color || 'var(--primary)';
        
        const circular = new CircularProgress(element, { size, color });
        circular.setProgress(progress);
        
        // Store instance for later updates
        element._circularProgress = circular;
    });
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CircularProgress;
}
