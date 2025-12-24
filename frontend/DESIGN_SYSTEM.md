# SmartChimera Design System
## Inspired by Obys Agency

### 🎨 Design Philosophy

**Minimalista · Impactante · Negro Dominante**

Inspirado en [Obys Agency](https://obys.agency/), este diseño privilegia:
- **Fondo negro profundo** (#050505) con contraste máximo
- **Tipografía bold y uppercase** para impacto visual
- **Espacios amplios** (whitespace generoso)
- **Animaciones sutiles** pero fluidas
- **Hover effects** que sorprenden sin distraer

---

## 🎭 Color Palette

```css
/* Primary Colors */
Background:    #050505  (Negro profundo)
Foreground:    #FAFAFA  (Blanco casi puro)
Accent:        #34D399  (Verde esmeralda - para CTAs y estados activos)

/* Secondary Colors */
Card BG:       #0F0F0F  (Negro ligeramente más claro)
Border:        #262626  (Gris muy oscuro)
Muted Text:    #999999  (Gris medio para texto secundario)
```

---

## 📐 Typography

### Fuente Principal: **Inter**
- Weights: 300 (Light), 400 (Regular), 500 (Medium), 600 (Semibold), 700 (Bold), 800 (Extrabold), 900 (Black)

### Hierarchy:

```tsx
// Hero Headlines (estilo Obys)
<h1 className="obys-hero-text">
  // text-6xl md:text-8xl, font-black, uppercase, tracking-tighter
</h1>

// Section Titles
<h2 className="obys-section-title">
  // text-4xl md:text-6xl, font-bold, uppercase
</h2>

// Card Titles
<h3 className="text-2xl font-bold uppercase tracking-tight">

// Body Text
<p className="text-base leading-relaxed text-muted-foreground">
```

---

## 🧩 Components

### 1. **Cards (obys-card)**
```tsx
<div className="obys-card">
  // Border hover effect
  // Sombra con color accent al hover
  // Transición suave (500ms)
</div>
```

**Uso:** Dossiers, team cards, resultados

---

### 2. **Buttons (obys-button)**
```tsx
<button className="obys-button">
  // Padding: px-8 py-4
  // Uppercase + tracking-wider
  // Scale al hover (105%)
  // Transición: 300ms
</button>
```

**Estados:**
- Default: Blanco sobre negro
- Hover: Verde accent con escala
- Active: Verde más oscuro

---

### 3. **Links (obys-link)**
```tsx
<a className="obys-link">
  // Underline animado de izquierda a derecha
  // Color accent al hover
</a>
```

---

### 4. **Gradient Text**
```tsx
<span className="obys-gradient-text">
  // Gradiente animado blanco → accent → blanco
  // Loop infinito suave (8s)
</span>
```

**Uso:** Títulos hero, palabras clave

---

## 📏 Layout & Spacing

### Grid System
```css
.obys-grid {
  grid-template-columns: 1fr;
  gap: 2rem;
}

@media (min-width: 768px) {
  grid-template-columns: repeat(2, 1fr);
}

@media (min-width: 1024px) {
  grid-template-columns: repeat(3, 1fr);
}
```

### Container
```css
.obys-container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 6rem 1.5rem;
}

@media (min-width: 768px) {
  padding: 6rem 3rem;
}
```

### Dividers
```tsx
<div className="obys-divider">
  // Línea horizontal con gradiente
  // Transparente → border → transparente
</div>
```

---

## ✨ Animations

### 1. **Fade In**
```tsx
<div className="obys-fade-in">
  // Aparece desde abajo con fade
  // Duration: 1s
</div>
```

### 2. **Hover Scale**
```css
transition: transform 300ms;
hover: scale(1.05);
```

### 3. **Gradient Animation**
```css
background: linear-gradient(to right, white, accent, white);
background-size: 200% auto;
animation: gradient 8s ease infinite;
```

---

## 🎯 Component Examples

### Hero Section
```tsx
<div className="obys-container">
  <h1 className="obys-hero-text obys-gradient-text">
    SMART CHIMERA
  </h1>
  <h2 className="text-2xl md:text-4xl font-light uppercase text-muted-foreground">
    Team Assembly / Bus Factor Mitigation
  </h2>
  <p className="text-lg text-muted-foreground max-w-2xl">
    Define requirements. Guardian analyzes collaboration graphs.
    Optimal teams emerge. Risk minimized.
  </p>
</div>
```

### Team Card
```tsx
<Card className="obys-card">
  <CardHeader>
    <div className="flex items-center gap-3">
      <span className="text-xs font-bold text-muted-foreground">01</span>
      <div className="h-px flex-1 bg-border"></div>
    </div>
    <CardTitle className="text-2xl font-bold uppercase">
      THE SAFE BET
    </CardTitle>
  </CardHeader>
  <CardContent>
    <div className="text-4xl font-black text-accent">8.7</div>
    <div className="text-xs uppercase tracking-widest">SCORE</div>
  </CardContent>
</Card>
```

### Navigation Item
```tsx
<Link className="obys-link">
  Dashboard
</Link>
```

---

## 🚀 Usage Guidelines

### DO ✅
- Usar **UPPERCASE** para títulos y CTAs
- Mantener **espacios amplios** entre secciones
- Aplicar **transiciones suaves** (300-500ms)
- Usar **accent color** con moderación (solo para highlights)
- Priorizar **legibilidad** con contraste alto

### DON'T ❌
- No usar más de 2-3 colores simultáneos
- No animar todo (solo elementos clave)
- No reducir espaciado (genera claustrofobia)
- No usar fuentes decorativas
- No sobresaturar con accent color

---

## 📱 Responsive Breakpoints

```css
sm:  640px   // Mobile landscape
md:  768px   // Tablet
lg:  1024px  // Desktop
xl:  1280px  // Large desktop
2xl: 1536px  // Extra large
```

---

## 🎪 Live Demo

**Frontend:** http://localhost:5173  
**Backend:** http://localhost:8000/docs  
**Neo4j:** http://localhost:7474

---

## 🔧 Customization

Para ajustar colores, editar `frontend/src/index.css`:

```css
:root {
  --background: 0 0% 3%;        /* Negro principal */
  --accent: 142 76% 45%;        /* Verde esmeralda */
  --border: 0 0% 15%;           /* Bordes sutiles */
}
```

---

## 📚 References

- **Obys Agency:** https://obys.agency/
- **Awwwards:** Best design practices
- **Tailwind CSS:** Utility-first framework
- **Radix UI:** Accessible components
- **Inter Font:** Modern sans-serif

---

**Created:** December 7, 2025  
**Version:** 1.0 - Obys Inspired  
**Status:** ✅ Production Ready
