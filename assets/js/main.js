/* Junior Thành — progressive enhancement only.
   Every feature below degrades to a fully working, readable page. */
(function () {
  "use strict";

  var root = document.documentElement;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  /* ── theme ─────────────────────────────────────────────── */
  var THEME_KEY = "jth-theme";
  var themeButtons = Array.prototype.slice.call(
    document.querySelectorAll("[data-set-theme]")
  );
  var themeColorMeta = document.querySelector('meta[name="theme-color"]');

  function readStored(key) {
    try {
      return window.localStorage.getItem(key);
    } catch (err) {
      return null;
    }
  }

  function store(key, value) {
    try {
      window.localStorage.setItem(key, value);
    } catch (err) {
      /* private mode / quota — ignore */
    }
  }

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    themeButtons.forEach(function (btn) {
      btn.setAttribute("aria-pressed", String(btn.dataset.setTheme === theme));
    });
    if (themeColorMeta) {
      themeColorMeta.setAttribute("content", theme === "then" ? "#0B0C0E" : "#F4F0E8");
    }
  }

  var storedTheme = readStored(THEME_KEY);
  var prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  applyTheme(storedTheme === "then" || storedTheme === "now" ? storedTheme : prefersDark ? "then" : "now");

  themeButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var next = btn.dataset.setTheme;
      applyTheme(next);
      store(THEME_KEY, next);
    });
  });

  /* ── clock ─────────────────────────────────────────────── */
  var clocks = [
    { el: document.getElementById("hero-clock"), time: true },
    { el: document.getElementById("footer-clock"), time: true }
  ].filter(function (c) { return c.el; });

  function formatTime(date) {
    var h = date.getHours();
    var period = h >= 12 ? "PM" : "AM";
    var hour12 = h % 12 || 12;
    return (
      String(hour12).padStart(2, "0") +
      ":" +
      String(date.getMinutes()).padStart(2, "0") +
      ":" +
      String(date.getSeconds()).padStart(2, "0") +
      " " +
      period
    );
  }

  function tick() {
    var now = new Date();
    var label = formatTime(now);
    var iso = now.toISOString();
    clocks.forEach(function (c) {
      c.el.textContent = label;
      c.el.setAttribute("datetime", iso);
    });
  }

  if (clocks.length) {
    tick();
    window.setInterval(tick, 1000);
  }

  /* ── year ──────────────────────────────────────────────── */
  var yearEl = document.getElementById("year");
  if (yearEl) {
    yearEl.textContent = String(new Date().getFullYear());
  }

  /* ── mobile menu ───────────────────────────────────────── */
  var menuToggle = document.getElementById("menu-toggle");
  var mobileMenu = document.getElementById("mobile-menu");

  if (menuToggle && mobileMenu) {
    var setMenu = function (open) {
      menuToggle.setAttribute("aria-expanded", String(open));
      menuToggle.setAttribute("aria-label", open ? "Đóng menu" : "Mở menu");
      mobileMenu.hidden = !open;
      document.body.style.overflow = open ? "hidden" : "";
    };

    menuToggle.addEventListener("click", function () {
      setMenu(mobileMenu.hidden);
    });

    mobileMenu.addEventListener("click", function (event) {
      if (event.target.closest("a")) {
        setMenu(false);
      }
    });

    document.addEventListener("keydown", function (event) {
      if (event.key !== "Escape" || mobileMenu.hidden) {
        return;
      }
      setMenu(false);
      menuToggle.focus();
    });

    /* focus containment while the sheet is open */
    mobileMenu.addEventListener("keydown", function (event) {
      if (event.key !== "Tab") {
        return;
      }
      var focusable = mobileMenu.querySelectorAll("a[href]");
      if (!focusable.length) {
        return;
      }
      var first = focusable[0];
      var last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 992 && !mobileMenu.hidden) {
        setMenu(false);
      }
    });
  }

  /* ── header stuck state ────────────────────────────────── */
  var header = document.getElementById("site-header");
  if (header) {
    var updateHeader = function () {
      header.classList.toggle("is-stuck", window.scrollY > 80);
    };
    updateHeader();
    window.addEventListener("scroll", updateHeader, { passive: true });
  }

  /* ── scroll progress ───────────────────────────────────── */
  var progressBar = document.getElementById("scroll-progress-bar");
  if (progressBar) {
    var updateProgress = function () {
      var max = document.documentElement.scrollHeight - window.innerHeight;
      var ratio = max > 0 ? window.scrollY / max : 0;
      progressBar.style.width = Math.min(100, Math.max(0, ratio * 100)) + "%";
    };
    updateProgress();
    window.addEventListener("scroll", updateProgress, { passive: true });
    window.addEventListener("resize", updateProgress);
  }

  /* ── active nav ────────────────────────────────────────── */
  var navLinks = Array.prototype.slice.call(document.querySelectorAll(".nav__link"));
  var sections = navLinks
    .map(function (link) {
      var id = link.getAttribute("href");
      return id && id.length > 1 ? document.querySelector(id) : null;
    })
    .filter(Boolean);

  if (navLinks.length && sections.length && "IntersectionObserver" in window) {
    var setCurrent = function (id) {
      navLinks.forEach(function (link) {
        if (link.getAttribute("href") === "#" + id) {
          link.setAttribute("aria-current", "true");
        } else {
          link.removeAttribute("aria-current");
        }
      });
    };

    var navObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            setCurrent(entry.target.id);
          }
        });
      },
      { rootMargin: "-45% 0px -50% 0px", threshold: 0 }
    );
    sections.forEach(function (section) { navObserver.observe(section); });
  }

  /* ── reveal on scroll ──────────────────────────────────── */
  var revealTargets = Array.prototype.slice.call(
    document.querySelectorAll(
      ".section-head, .about__prose > *, .quote-card, .portrait, .role-card, " +
      ".interlude__quote, .ikigai, .goals__quotes, .faq-item, .faq__outro, .aside-card"
    )
  );
  revealTargets.forEach(function (el, index) {
    el.classList.add("reveal");
    el.setAttribute("data-delay", String(index % 4));
  });

  if ("IntersectionObserver" in window && !reduceMotion.matches) {
    var revealObserver = new IntersectionObserver(
      function (entries, observer) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-in");
            observer.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
    );
    revealTargets.forEach(function (el) { revealObserver.observe(el); });
  } else {
    revealTargets.forEach(function (el) { el.classList.add("is-in"); });
  }

  /* ── FAQ accordion ─────────────────────────────────────── */
  var triggers = Array.prototype.slice.call(document.querySelectorAll(".faq-item__trigger"));

  triggers.forEach(function (trigger) {
    var panel = document.getElementById(trigger.getAttribute("aria-controls"));
    if (!panel) {
      return;
    }

    trigger.addEventListener("click", function () {
      var open = trigger.getAttribute("aria-expanded") === "true";
      trigger.setAttribute("aria-expanded", String(!open));
      panel.hidden = open;
    });

    trigger.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && trigger.getAttribute("aria-expanded") === "true") {
        trigger.setAttribute("aria-expanded", "false");
        panel.hidden = true;
        trigger.focus();
      }
    });
  });

  /* ── hero video (lazy, motion- and data-aware) ─────────── */
  var video = document.getElementById("hero-video");
  var connection = navigator.connection || {};
  var saveData = connection.saveData === true;
  var slowLink = /^(slow-2g|2g)$/.test(connection.effectiveType || "");

  if (video && !reduceMotion.matches && !saveData && !slowLink && window.innerWidth >= 480) {
    var sources = [];
    if (video.dataset.srcWebm) {
      var webm = document.createElement("source");
      webm.src = video.dataset.srcWebm;
      webm.type = "video/webm";
      sources.push(webm);
    }
    if (video.dataset.src) {
      var mp4 = document.createElement("source");
      mp4.src = video.dataset.src;
      mp4.type = "video/mp4";
      sources.push(mp4);
    }
    sources.forEach(function (source) { video.appendChild(source); });

    video.addEventListener("playing", function () {
      video.classList.add("is-playing");
    });

    var play = video.play();
    if (play && typeof play.catch === "function") {
      play.catch(function () {
        /* autoplay blocked: the poster is the design, nothing to fix */
      });
    }
  }
})();
