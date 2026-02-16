---
layout: home

hero:
  name: "envoic"
  text: "Environment Scanner"
  tagline: "Discover and report every virtual environment on your system."
  image:
    src: /envoic.png
    alt: "envoic"
  actions:
    - theme: brand
      text: "Get Started"
      link: /guide/getting-started
    - theme: alt
      text: "View on GitHub"
      link: https://github.com/mahimailabs/envoic

---

<div class="scan-command">
  <!-- <p class="scan-command-label">Quick run</p> -->
  <div class="scan-command-ring">
    <pre><code>uvx envoic scan .</code></pre>
  </div>
</div>

<style>
.scan-command {
  width: min(520px, 46vw);
  min-width: 280px;
  margin: 1.5rem auto 0;
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
  padding: 1rem 1.15rem;
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
  .scan-command {
    width: calc(100vw - 2.5rem);
    min-width: 0;
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
</style>
