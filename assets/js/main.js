// Copyright year
const yearEl = document.getElementById("year");
if (yearEl) yearEl.textContent = new Date().getFullYear();

// Mobile nav toggle
const nav = document.querySelector(".nav");
const toggle = document.querySelector(".nav__toggle");
if (toggle && nav) {
  toggle.addEventListener("click", () => {
    const open = nav.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", open);
  });
  document.addEventListener("click", (e) => {
    if (nav.classList.contains("is-open") && !nav.contains(e.target)) {
      nav.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
    }
  });

  nav.querySelectorAll(".nav__links a").forEach((link) => {
    link.addEventListener("click", () => {
      nav.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
    });
  });
}

// Active nav link on scroll
const sections = document.querySelectorAll("section[id]");
const navLinks = document.querySelectorAll('.nav__links a[href^="#"]');

if (sections.length && navLinks.length) {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          navLinks.forEach((a) => {
            a.classList.toggle("is-active", a.getAttribute("href") === `#${entry.target.id}`);
          });
        }
      });
    },
    { rootMargin: "-40% 0px -55% 0px" },
  );

  sections.forEach((s) => observer.observe(s));
}

// Scroll reveal — [data-reveal] sections are hidden in HTML/CSS immediately.
// Flush styles so the browser commits opacity:0 as the "from" state, then
// start observing in the next frame so transitions actually play.
document.body.getBoundingClientRect(); // flush style recalculation

requestAnimationFrame(() => {
  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          revealObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.08, rootMargin: "0px 0px -60px 0px" },
  );

  document.querySelectorAll("[data-reveal]").forEach((el) => revealObserver.observe(el));
});

// Page fade-out on same-origin navigation
document.addEventListener("click", (e) => {
  const a = e.target.closest("a[href]");
  if (!a) return;
  const href = a.getAttribute("href");
  const isExternal =
    a.target === "_blank" ||
    href.startsWith("http") ||
    href.startsWith("//") ||
    href.startsWith("mailto:") ||
    href.startsWith("#");
  if (isExternal) return;
  e.preventDefault();
  document.body.classList.add("is-leaving");
  setTimeout(() => {
    window.location.href = href;
  }, 200);
});

// When the browser restores this page from the back-forward cache, the body
// still has is-leaving (opacity:0). Remove it so the page fades back in.
window.addEventListener("pageshow", (e) => {
  if (e.persisted) {
    document.body.classList.remove("is-leaving");
  }
});

// Make the header logo disappear scrolling down.
const headerLogo = document.querySelector('.header-logo');
const hero = document.querySelector('.hero__content');

const observer = new IntersectionObserver(([entry]) => {
  headerLogo.classList.toggle('visible', !entry.isIntersecting);
}, { threshold: 0 });

observer.observe(hero);
