# Sidebar Design Options for ArcReactor

This document outlines 4 beautiful sidebar design options available in the AEGIS Protocol CSS framework.

## How to Apply

Add one of these classes to the `<body>` tag in your base template:

```html
<body class="sidebar-modern">  <!-- or sidebar-glass, sidebar-minimal, sidebar-vibrant -->
```

---

## Option 1: Modern Gradient (sidebar-modern)
**Best for:** Professional, corporate environments

### Features:
- Dark gradient background (navy to dark slate)
- Smooth hover animations with left border accent
- Active items get gradient background
- Clean 4px left border indicator
- Subtle transform on hover (slides right 4px)

### Color Scheme:
- Background: Dark navy gradient (#1e293b → #0f172a)
- Accent: Indigo (#4f46e5)
- Hover: Semi-transparent indigo
- Active: Gradient with indigo/blue tones

### CSS Class: `sidebar-modern`

---

## Option 2: Glassmorphism (sidebar-glass)
**Best for:** Modern, futuristic interfaces

### Features:
- Frosted glass effect with backdrop blur
- Semi-transparent white overlays
- Subtle border highlights
- Floating card appearance for nav items
- Elegant shadow effects on hover

### Color Scheme:
- Background: Transparent white with blur
- Borders: Subtle white (10% opacity)
- Hover: Enhanced glow with colored shadow
- Active: Deeper indigo tint

### CSS Class: `sidebar-glass`

---

## Option 3: Minimal Elegant (sidebar-minimal)
**Best for:** Clean, distraction-free workspaces

### Features:
- Pure white background
- Subtle grey hover states
- Inset accent bar for active items
- Lightweight typography
- Maximized content space

### Color Scheme:
- Background: Pure white
- Text: Grey (#6b7280)
- Hover: Light grey (#f3f4f6)
- Active: Light indigo with bold inset bar

### CSS Class: `sidebar-minimal`

---

## Option 4: Vibrant Cards (sidebar-vibrant)
**Best for:** Creative, engaging user experiences

### Features:
- Bold gradient background (indigo)
- White text on colored cards
- Scale animation on hover
- Strong visual hierarchy
- Icon backgrounds for emphasis

### Color Scheme:
- Background: Vibrant indigo gradient (#6366f1 → #4f46e5)
- Cards: Semi-transparent white
- Active: Solid white with indigo text
- Icons: Highlighted backgrounds

### CSS Class: `sidebar-vibrant`

---

## Grievance Desk Color Coding

The grievance desk now automatically color-codes rows based on status:

### Status Colors:
- **Submitted / Pending**: Yellow background (#fef3c7) with amber left border
- **Under Review / In Progress**: Blue background (#dbeafe) with blue left border
- **Resolved**: Green background (#dcfce7) with green left border

### Implementation:
These colors are automatically applied via the `grievance-row-{{ grievance.status }}` CSS classes.

---

## Quick Comparison

| Feature | Modern | Glass | Minimal | Vibrant |
|---------|--------|-------|---------|---------|
| Visual Weight | Medium | Light | Ultra Light | Heavy |
| Animation | Moderate | Subtle | Minimal | Bold |
| Best Use | Business | Tech | Productivity | Creative |
| Accessibility | ★★★★★ | ★★★★☆ | ★★★★★ | ★★★☆☆ |

---

## Recommendation

- **For corporate/academic settings**: Use `sidebar-modern` or `sidebar-minimal`
- **For tech startups**: Use `sidebar-glass`
- **For creative agencies**: Use `sidebar-vibrant`

Currently, the default style is already applied. To switch, simply add the class name to the body tag in the base template.
