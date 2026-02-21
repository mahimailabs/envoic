---
layout: home

hero:
  name: "envoic"
  text: "Environment Scanner"
  tagline: "Discover and manage Python virtualenvs and JavaScript node_modules."
  image:
    src: /envoic.png
    alt: "envoic"
  actions:
    - theme: brand
      text: "Python Guide"
      link: /guide/getting-started
    - theme: alt
      text: "JavaScript Guide"
      link: /guide/js-getting-started

---

<div class="scan-command-grid">
  <div class="scan-command">
    <p class="scan-command-subtitle">Python</p>
    <div class="scan-command-ring">
      <pre><code>uvx envoic scan .</code></pre>
    </div>
  </div>
  <div class="scan-command">
    <p class="scan-command-subtitle">JavaScript</p>
    <div class="scan-command-ring">
      <pre><code>npx envoic scan .</code></pre>
    </div>
  </div>
</div>

<style>
.scan-command-grid {
  width: min(920px, 92vw);
  margin: 0.75rem auto 0;
  padding-left: 0;
  display: flex;
  justify-content: space-between;
  align-items: stretch;
  gap: 0.85rem;
}

.scan-command {
  min-width: 0;
  width: 340px;
}

.scan-command-subtitle {
  margin: 0 0 0.45rem;
  font-size: 0.76rem;
  letter-spacing: 0.11em;
  text-transform: uppercase;
  font-weight: 700;
  color: var(--vp-c-text-2);
}

.scan-command-label {
  margin: 0 0 0.6rem;
  text-align: center;
  font-size: 0.78rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font-weight: 700;
  color: var(--vp-c-brand-1);
}

.scan-command-ring {
  --ring-angle: 0deg;
  padding: 1px;
  border-radius: 14px;
  background:
    conic-gradient(
      from var(--ring-angle),
      color-mix(in srgb, var(--vp-c-brand-1) 20%, var(--vp-c-divider)) 0deg 290deg,
      color-mix(in srgb, var(--vp-c-brand-1) 95%, white) 322deg 342deg,
      color-mix(in srgb, var(--vp-c-brand-1) 20%, var(--vp-c-divider)) 360deg
    );
  box-shadow: 0 10px 26px rgba(0, 0, 0, 0.06);
  animation: border-sweep 3s linear infinite;
}

.scan-command pre {
  margin: 0;
  padding: 0.9rem 1rem;
  border-radius: 13px;
  border: 0;
  background:
    linear-gradient(
      180deg,
      color-mix(in srgb, var(--vp-c-brand-soft) 36%, transparent),
      transparent 60%
    ),
    var(--vp-c-bg-soft);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.35);
  overflow: auto;
  min-height: 54px;
  display: flex;
  align-items: center;
}

.scan-command code {
  display: block;
  overflow-x: auto;
  font-size: 0.98rem;
  font-weight: 600;
  letter-spacing: 0.01em;
  color: var(--vp-c-text-1);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}

@media (max-width: 768px) {
  .scan-command-grid {
    width: calc(100vw - 2.5rem);
    display: grid;
    grid-template-columns: 1fr;
    gap: 0.8rem;
    padding-left: 0;
  }

  .scan-command {
    width: 100%;
  }

  .scan-command pre {
    padding: 0.9rem 1rem;
  }
}

@keyframes border-sweep {
  to { --ring-angle: 1turn; }
}

@property --ring-angle {
  syntax: "<angle>";
  initial-value: 0deg;
  inherits: false;
}

@media (prefers-reduced-motion: reduce) {
  .scan-command-ring {
    animation: none;
  }
}

.VPHome {
  --vp-button-alt-bg: #facc15;
  --vp-button-alt-text: #1f2937;
  --vp-button-alt-hover-bg: #eab308;
  --vp-button-alt-hover-text: #111827;
}
</style>
