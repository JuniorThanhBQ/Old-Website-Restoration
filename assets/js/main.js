(function () {
  "use strict";

  var root = document.documentElement;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  var THEME_KEY = "jth-theme";
  var ROOM_PARAM = "room";
  var syncRoom = null;
  var resetShareLabel = null;
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
    }
  }

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    themeButtons.forEach(function (btn) {
      btn.setAttribute("aria-pressed", String(btn.dataset.setTheme === theme));
    });
    if (themeColorMeta) {
      themeColorMeta.setAttribute("content", theme === "then" ? "#0B0C0E" : "#EEF3F7");
    }
    if (typeof syncRoom === "function") {
      syncRoom();
    }
  }

  var storedTheme = readStored(THEME_KEY);
  var prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

  // a room can be sent to someone: ?room=then / ?room=now outranks the saved choice
  function roomFromUrl() {
    var room = null;
    try {
      room = new URLSearchParams(window.location.search).get(ROOM_PARAM);
    } catch (err) {
    }
    return room === "then" || room === "now" ? room : null;
  }

  function roomUrl(theme) {
    try {
      var url = new URL(window.location.href);
      url.searchParams.set(ROOM_PARAM, theme);
      return url.toString();
    } catch (err) {
      return window.location.href;
    }
  }

  function reflectRoomInUrl(theme) {
    if (!window.history || typeof window.history.replaceState !== "function") return;
    try {
      window.history.replaceState(null, "", roomUrl(theme));
    } catch (err) {
    }
  }

  applyTheme(roomFromUrl() ||
    (storedTheme === "then" || storedTheme === "now" ? storedTheme : prefersDark ? "then" : "now"));

  themeButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var next = btn.dataset.setTheme;
      applyTheme(next);
      store(THEME_KEY, next);
      reflectRoomInUrl(next);
      if (typeof resetShareLabel === "function") resetShareLabel();
    });
  });

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

  var yearEl = document.getElementById("year");
  if (yearEl) {
    yearEl.textContent = String(new Date().getFullYear());
  }

  var capsuleDate = document.getElementById("capsule-date");
  if (capsuleDate) {
    try {
      var firstSeen = readStored("jth-first-seen");
      var firstDate = firstSeen ? new Date(firstSeen) : null;
      if (!firstDate || isNaN(firstDate.getTime())) {
        firstDate = new Date();
        store("jth-first-seen", firstDate.toISOString());
      }
      if (!isNaN(firstDate.getTime())) {
        capsuleDate.textContent = firstDate.toLocaleDateString("vi-VN", {
          day: "2-digit",
          month: "2-digit",
          year: "numeric"
        });
        var capsule = document.getElementById("capsule");
        if (capsule) {
          capsule.removeAttribute("hidden");
        }
      }
    } catch (err) {
    }
  }

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

  var header = document.getElementById("site-header");
  if (header) {
    var updateHeader = function () {
      header.classList.toggle("is-stuck", window.scrollY > 80);
    };
    updateHeader();
    window.addEventListener("scroll", updateHeader, { passive: true });
  }

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
      });
    }
  }

  var musicBtn = document.getElementById("music-toggle");
  var tracks = {
    now: document.getElementById("music-now"),
    then: document.getElementById("music-then")
  };

  if (musicBtn && tracks.now && tracks.then) {
    var pageTitle = document.title;
    var wantPlaying = false;
    var attempt = 0;
    var activeKey = null;
    var titleTimer = null;
    var eqFrame = null;
    var eqTimer = null;
    var contexts = {};
    var sources = {};
    var analysers = {};

    var liner = document.getElementById("liner");
    var linerSong = document.getElementById("liner-song");
    var linerArtist = document.getElementById("liner-artist");
    var bars = Array.prototype.slice.call(
      liner ? liner.querySelectorAll(".liner__eq i") : []
    );
    var analyserOff = {};

    tracks.now.volume = 0.42;
    tracks.then.volume = 0.42;

    function pad2(n) { return String(n).padStart(2, "0"); }
    function stamp(secs) {
      if (!isFinite(secs) || secs < 0) return "0:00";
      return Math.floor(secs / 60) + ":" + pad2(Math.floor(secs % 60));
    }

    function keyOf(el) {
      return el === tracks.now ? "now" : el === tracks.then ? "then" : null;
    }

    function ensureSrc(el) {
      if (!el.getAttribute("src") && el.dataset.src) el.src = el.dataset.src;
    }

    function currentKey() {
      var theme = root.getAttribute("data-theme");
      return theme === "then" ? "then" : "now";
    }

    function current() {
      return tracks[currentKey()];
    }

    function playingKey() {
      var keys = ["now", "then"];
      for (var i = 0; i < keys.length; i++) {
        var el = tracks[keys[i]];
        if (el && !el.paused && !el.ended) return keys[i];
      }
      return null;
    }

    function setPressed(on) {
      musicBtn.setAttribute("aria-pressed", String(on));
      musicBtn.setAttribute("aria-label", on ? "Tắt nhạc nền" : "Bật nhạc nền");
    }

    function ensureAnalyser(key) {
      var el = tracks[key];
      var Ctx = window.AudioContext || window.webkitAudioContext;
      if (!el || !Ctx || contexts[key] || analyserOff[key]) return;
      try {
        var ctx = new Ctx();
        var src = ctx.createMediaElementSource(el);
        var analyser = ctx.createAnalyser();
        src.connect(analyser);
        analyser.connect(ctx.destination);
        contexts[key] = ctx;
        sources[key] = src;
        analysers[key] = analyser;
      } catch (err) {
        analyserOff[key] = true;
      }
    }

    function stopLoops() {
      if (eqFrame !== null) {
        window.cancelAnimationFrame(eqFrame);
        eqFrame = null;
      }
      if (eqTimer !== null) {
        window.clearInterval(eqTimer);
        eqTimer = null;
      }
    }

    function updateBars(key, tick) {
      var analyser = key ? analysers[key] : null;
      var data = analyser ? new Uint8Array(analyser.frequencyBinCount) : null;
      if (analyser) analyser.getByteFrequencyData(data);
      bars.forEach(function (bar, i) {
        var level;
        if (analyser) {
          var at = Math.floor((i / bars.length) * data.length * 0.55);
          level = 0.08 + 0.92 * Math.min(1, (data[at] / 255) * 1.7);
        } else {
          level = 0.08 + 0.92 * (0.3 + 0.5 * Math.abs(Math.sin(tick + i * 0.7)));
        }
        bar.style.setProperty("--level", level.toFixed(2));
      });
    }

    function runEq() {
      if (!bars.length || !wantPlaying) return;
      if (reduceMotion.matches) {
        bars.forEach(function (bar, i) {
          bar.style.setProperty("--level", (0.12 + 0.75 * (0.2 + 0.16 * i)).toFixed(2));
        });
        return;
      }
      var tick = 0;
      var key = playingKey();
      if (key && analysers[key]) {
        var loop = function () {
          if (!wantPlaying) return;
          updateBars(key, tick);
          tick++;
          eqFrame = window.requestAnimationFrame(loop);
        };
        eqFrame = window.requestAnimationFrame(loop);
      } else {
        eqTimer = window.setInterval(function () {
          if (!wantPlaying) return;
          tick++;
          updateBars(null, tick);
        }, 120);
      }
    }

    function syncLiner() {
      if (!liner) return;
      var key = playingKey();
      if (wantPlaying && key) {
        if (liner.hidden || linerSong.textContent !== tracks[key].dataset.title) {
          linerSong.textContent = tracks[key].dataset.title || "";
          linerArtist.textContent = tracks[key].dataset.artist || "";
        }
        liner.hidden = false;
      } else {
        liner.hidden = true;
      }
    }

    function syncTitle() {
      var key = playingKey();
      if (key) {
        var el = tracks[key];
        document.title = stamp(el.currentTime) + " / " + stamp(el.duration);
        if (titleTimer === null) {
          titleTimer = window.setInterval(function () {
            var live = playingKey();
            if (live === null) {
              window.clearInterval(titleTimer);
              titleTimer = null;
              document.title = pageTitle;
              return;
            }
            var track = tracks[live];
            document.title = stamp(track.currentTime) + " / " + stamp(track.duration);
          }, 1000);
        }
      } else {
        if (titleTimer !== null) {
          window.clearInterval(titleTimer);
          titleTimer = null;
        }
        document.title = pageTitle;
      }
    }

    function sync() {
      setPressed(wantPlaying || playingKey() !== null);
      syncTitle();
      syncLiner();
      stopLoops();
      if (wantPlaying) runEq();
    }

    syncRoom = function () {
      var key = currentKey();
      if (key === activeKey) return;
      var outgoing = activeKey;
      activeKey = key;
      if (outgoing !== null) {
        var prev = tracks[outgoing];
        if (prev) prev.pause();
      }
      if (!wantPlaying) return;
      var next = tracks[key];
      if (!next) return;
      var mine = ++attempt;
      ensureSrc(next);
      var started = next.play();
      if (started && typeof started.catch === "function") {
        started.catch(function () {
          if (mine !== attempt) return;
          wantPlaying = false;
          sync();
        });
      }
      ensureAnalyser(key);
      sync();
    };

    function start() {
      var el = current();
      if (!el) return;
      var mine = ++attempt;
      wantPlaying = true;
      activeKey = keyOf(el) || currentKey();
      ensureSrc(el);
      var other = tracks[activeKey === "now" ? "then" : "now"];
      if (other) other.pause();
      var started = el.play();
      if (started && typeof started.catch === "function") {
        started.catch(function () {
          if (mine !== attempt) return;
          wantPlaying = false;
          sync();
        });
      }
      ensureAnalyser(activeKey);
      sync();
    }

    function stop() {
      wantPlaying = false;
      attempt++;
      tracks.now.pause();
      tracks.then.pause();
      sync();
    }

    ["now", "then"].forEach(function (key) {
      tracks[key].addEventListener("pause", sync);
      tracks[key].addEventListener("playing", sync);
    });

    // capture phase: the menu's own Escape listener runs on bubble and closes the sheet
    // first, so this handler must read the menu's state before it is mutated
    document.addEventListener("keydown", function (event) {
      if (event.key !== "Escape" || !liner || liner.hidden) return;
      if (!mobileMenu.hidden) return;
      liner.hidden = true;
    }, true);

    musicBtn.addEventListener("click", function () {
      if (wantPlaying) stop(); else start();
    });

    activeKey = currentKey();
  }

  var shareBtn = document.getElementById("liner-share");
  var shareLabel = document.getElementById("liner-share-text");
  var SHARE_IDLE = "Sao chép liên kết phòng này";
  if (shareBtn && shareLabel) {
    resetShareLabel = function () {
      shareLabel.textContent = SHARE_IDLE;
    };
    shareBtn.addEventListener("click", function () {
      var theme = root.getAttribute("data-theme") === "then" ? "then" : "now";
      var link = roomUrl(theme);
      // without the Clipboard API the address bar is the fallback, so put the room there
      var fallback = function () {
        reflectRoomInUrl(theme);
        shareLabel.textContent = "Liên kết đã hiện ở thanh địa chỉ";
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(link).then(function () {
          shareLabel.textContent = "Đã sao chép liên kết phòng này";
        }, fallback);
      } else {
        fallback();
      }
    });
  }
})();
