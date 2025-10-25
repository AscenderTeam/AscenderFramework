# Ascender Framework Documentation Homepage

This is the beautiful, modern homepage for the Ascender Framework documentation, integrated with MkDocs Material theme.

## Features

### Modern Libraries Used
- **AOS (Animate On Scroll)**: Smooth scroll-triggered animations for all sections
- **Particles.js**: Interactive particle background with gradient colors matching the Ascender logo
- **GSAP + ScrollTrigger**: Advanced animations and scroll-based effects
- **Material for MkDocs**: Base theme with dark/light mode support

### Design Highlights
- Gradient text using Ascender logo's color palette
- Animated floating background
- Interactive particle effects
- Smooth scroll animations
- 3D tilt effects on hover
- Ripple button effects
- Responsive design for all screen sizes
- Full dark/light theme support

### Color Palette (from Ascender Logo)
- Red: #FD0100
- Magenta: #ED0189
- Pink: #DA04F6
- Blue: #7872FA
- Cyan: #02FEEE
- Purple: #6413CF
- Orange: #FD8403
- Cyan Alt: #0BA3C8

## File Structure

```
docs/
├── overrides/
│   ├── main.html                  # Base template override
│   ├── home.html                  # Homepage template
│   └── partials/
│       └── home-content.html      # Homepage content partial
├── assets/
│   ├── stylesheets/
│   │   └── home.css              # Homepage styles
│   └── javascripts/
│       └── home.js               # Homepage animations & effects
└── index.md                       # Homepage markdown (uses home.html template)
```

## How It Works

1. `index.md` specifies `template: home.html` in its frontmatter
2. `home.html` extends MkDocs Material's base template
3. It loads custom CSS and modern animation libraries (AOS, Particles.js, GSAP)
4. The content is rendered from `partials/home-content.html`
5. All animations are initialized in `home.js`

## Running the Documentation

```bash
# Install MkDocs and Material theme
pip install mkdocs-material mkdocs-awesome-pages-plugin mkdocstrings[python]

# Serve locally
mkdocs serve

# Build static site
mkdocs build
```

## Customization

### Changing Colors
Edit the CSS variables in `docs/assets/stylesheets/home.css`:
```css
:root {
    --gradient-primary: linear-gradient(...);
    --gradient-secondary: linear-gradient(...);
    --gradient-accent: linear-gradient(...);
}
```

### Adjusting Animations
Modify animation timings in `docs/assets/javascripts/home.js`:
```javascript
AOS.init({
    duration: 800,  // Animation duration
    delay: 0,       // Delay before animation
    once: true      // Animate only once
});
```

### Particle Effects
Customize particles in `home.js`:
```javascript
particles: {
    number: {
        value: 80  // Number of particles
    },
    color: {
        value: [...]  // Particle colors
    }
}
```

## Browser Compatibility
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Responsive design works on mobile, tablet, and desktop
- Graceful degradation for older browsers

## Performance
- All libraries loaded from CDN for caching
- Animations use CSS transforms and opacity for GPU acceleration
- Particles optimized for 60fps
- Lazy loading for scroll-triggered animations
