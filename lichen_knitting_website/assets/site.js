/*!
 * 即墨区利晨针织厂官网 / Jimo Lichen Knitting Factory
 * assets/site.js — language switching, mobile navigation, inquiry helper.
 *
 * Design rules:
 *  - No network requests. Nothing is ever submitted or stored on a server.
 *  - Language preference only, stored in localStorage.
 *  - Every string that changes is declared in the HTML with data-zh / data-en,
 *    so the page is fully readable (Chinese) even with JavaScript disabled.
 */
(function () {
  "use strict";

  var STORAGE_KEY = "lichenLang";
  var DEFAULT_LANG = "zh";
  var lang = DEFAULT_LANG;

  /* ------------------------------------------------------------------ helpers */

  function read() {
    // A ?lang=en / ?lang=zh query string wins, so an English link can be shared
    // directly and search engines / ad links can point at a specific language.
    try {
      var q = new URLSearchParams(window.location.search).get("lang");
      if (q === "en" || q === "zh") return q;
    } catch (e) {
      /* URLSearchParams unsupported — fall through to storage */
    }
    try {
      var v = window.localStorage.getItem(STORAGE_KEY);
      return v === "en" || v === "zh" ? v : DEFAULT_LANG;
    } catch (e) {
      return DEFAULT_LANG;
    }
  }

  /** Reflect the current language in the address bar without reloading. */
  function syncUrl() {
    if (!window.history || !window.history.replaceState) return;
    try {
      var url = new URL(window.location.href);
      if (lang === "en") {
        url.searchParams.set("lang", "en");
      } else {
        url.searchParams.delete("lang");
      }
      window.history.replaceState(null, "", url.toString());
    } catch (e) {
      /* file:// or blocked history API — harmless */
    }
  }

  function save(v) {
    try {
      window.localStorage.setItem(STORAGE_KEY, v);
    } catch (e) {
      /* private mode / disabled storage — language simply is not remembered */
    }
  }

  /** Swap text of an element without destroying markup it may contain. */
  function setText(el, value) {
    if (value == null) return;
    if (el.children.length === 0) {
      el.textContent = value;
    } else {
      // Element has child markup: only touch its direct text nodes.
      var touched = false;
      for (var i = 0; i < el.childNodes.length; i++) {
        var node = el.childNodes[i];
        if (node.nodeType === 3 && node.nodeValue.trim() !== "") {
          node.nodeValue = value;
          touched = true;
          break;
        }
      }
      if (!touched) el.textContent = value;
    }
  }

  function pick(el, suffix) {
    suffix = suffix || "";
    var en = el.getAttribute("data-en" + suffix);
    var zh = el.getAttribute("data-zh" + suffix);
    if (lang === "en") return en != null ? en : zh;
    return zh != null ? zh : en;
  }

  /* --------------------------------------------------------------- translation */

  function translate() {
    var isEn = lang === "en";
    document.documentElement.lang = isEn ? "en" : "zh-CN";
    document.documentElement.setAttribute("data-lang", lang);

    /* <title> — explicit per-page English title, no fragile string surgery. */
    if (!document.documentElement.dataset.titleZh) {
      document.documentElement.dataset.titleZh = document.title.trim();
    }
    document.title =
      isEn && document.documentElement.dataset.titleEn
        ? document.documentElement.dataset.titleEn
        : document.documentElement.dataset.titleZh;

    /* Meta tags that carry data-zh / data-en. */
    document.querySelectorAll("meta[data-zh]").forEach(function (m) {
      var v = pick(m);
      if (v != null) m.setAttribute("content", v);
    });

    /* Plain text elements. */
    document.querySelectorAll("[data-zh][data-en]").forEach(function (el) {
      if (el.tagName === "META") return;
      if (el.hasAttribute("data-zh-html")) return; // handled below
      setText(el, pick(el));
    });

    /* Rich-text variants (must be marked with data-zh-html / data-en-html). */
    document.querySelectorAll("[data-zh-html]").forEach(function (el) {
      var v = isEn ? el.getAttribute("data-en-html") : el.getAttribute("data-zh-html");
      if (v != null) el.innerHTML = v;
    });

    /* Form placeholders. */
    document.querySelectorAll("[data-zh-placeholder]").forEach(function (el) {
      var v = isEn
        ? el.getAttribute("data-en-placeholder")
        : el.getAttribute("data-zh-placeholder");
      if (v != null) el.setAttribute("placeholder", v);
    });

    /* Accessible names. */
    document.querySelectorAll("[data-zh-aria]").forEach(function (el) {
      var v = isEn ? el.getAttribute("data-en-aria") : el.getAttribute("data-zh-aria");
      if (v != null) el.setAttribute("aria-label", v);
    });

    /* Image alternative text. */
    document.querySelectorAll("img[data-zh-alt]").forEach(function (el) {
      var v = isEn ? el.getAttribute("data-en-alt") : el.getAttribute("data-zh-alt");
      if (v != null) el.setAttribute("alt", v);
    });

    /* Language toggle button. */
    document.querySelectorAll(".lang").forEach(function (btn) {
      btn.textContent = isEn ? "中文" : "EN";
      btn.setAttribute(
        "aria-label",
        isEn ? "切换为中文 / Switch to Chinese" : "Switch to English / 切换为英文"
      );
      btn.setAttribute("aria-pressed", isEn ? "true" : "false");
      btn.setAttribute("title", isEn ? "切换为中文" : "Switch to English");
    });

    /* Let pages re-run anything language dependent. */
    document.dispatchEvent(
      new CustomEvent("languagechange", { detail: { lang: lang } })
    );
  }

  /* ----------------------------------------------------------------- navigation */

  function setActiveNav() {
    var here = location.pathname.split("/").pop() || "index.html";
    document.querySelectorAll(".navlinks a[href]").forEach(function (a) {
      var target = a.getAttribute("href").split("#")[0];
      var isActive = target === here;
      a.classList.toggle("active", isActive);
      if (isActive) {
        a.setAttribute("aria-current", "page");
      } else {
        a.removeAttribute("aria-current");
      }
    });
  }

  function initMobileNav() {
    var btn = document.querySelector(".menu-btn");
    var links = document.querySelector(".navlinks");
    if (!btn || !links) return;
    if (!links.id) links.id = "primary-navigation";
    btn.setAttribute("aria-controls", links.id);
    btn.setAttribute("aria-expanded", "false");

    function setOpen(open) {
      links.classList.toggle("open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.setAttribute(
        "aria-label",
        open ? "关闭导航 / Close navigation" : "打开导航 / Open navigation"
      );
      document.body.classList.toggle("nav-open", open);
    }

    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      setOpen(btn.getAttribute("aria-expanded") !== "true");
    });

    links.addEventListener("click", function (e) {
      if (e.target.closest("a")) setOpen(false);
    });

    document.addEventListener("click", function (e) {
      if (links.classList.contains("open") && !e.target.closest(".nav")) setOpen(false);
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && links.classList.contains("open")) {
        setOpen(false);
        btn.focus();
      }
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 760 && links.classList.contains("open")) setOpen(false);
    });

    setOpen(false);
  }

  /* ------------------------------------------------------------ copy buttons */
  function initCopyButtons() {
    document.querySelectorAll("[data-copy]").forEach(function (btn) {
      function idleLabel() {
        btn.textContent = lang === "en" ? "Copy WeChat ID" : "复制微信号";
      }
      btn.addEventListener("click", function () {
        var value = btn.getAttribute("data-copy");
        copyText(value).then(
          function () {
            btn.classList.add("copied");
            btn.textContent = lang === "en" ? "Copied" : "已复制";
            setTimeout(function () {
              btn.classList.remove("copied");
              idleLabel();
            }, 2200);
          },
          function () {
            window.prompt(lang === "en" ? "Copy our WeChat ID:" : "请复制微信号：", value);
          }
        );
      });
      // Keep the idle label correct after a language switch.
      document.addEventListener("languagechange", function () {
        if (!btn.classList.contains("copied")) idleLabel();
      });
    });
  }

  /* -------------------------------------------------------------- inquiry helper */

  function inquiryLines(form) {
    var isEn = lang === "en";
    var d = new FormData(form);
    var select = form.querySelector("select[name='product']");
    var product = d.get("product") || "";
    if (select && select.options.length) {
      var chosen = select.options[select.selectedIndex];
      var localized =
        chosen && (isEn ? chosen.getAttribute("data-en") : chosen.getAttribute("data-zh"));
      if (localized) product = localized;
    }
    var rows = [
      [isEn ? "Name" : "客户姓名", d.get("name")],
      [isEn ? "Phone / WeChat" : "联系电话/微信", d.get("contact")],
      [isEn ? "Product type" : "产品类型", product],
      [isEn ? "Quantity" : "订单数量", d.get("quantity")],
      [
        isEn ? "Composition / weight / specifications" : "成分/克重/规格",
        d.get("spec"),
      ],
      [isEn ? "Details" : "详细需求", d.get("details")],
    ];
    var head = isEn
      ? "Website inquiry - please contact me by phone or WeChat:"
      : "官网客户询价（请通过电话/微信联系）：";
    var out = [head];
    rows.forEach(function (r) {
      var v = (r[1] == null ? "" : String(r[1])).trim();
      if (v) out.push(r[0] + ": " + v);
    });
    return out.join("\n"); // real newlines (previous version emitted a literal backslash-n)
  }

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      try {
        var ta = document.createElement("textarea");
        ta.value = text;
        ta.setAttribute("readonly", "");
        ta.style.position = "fixed";
        ta.style.top = "-1000px";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        var ok = document.execCommand("copy");
        document.body.removeChild(ta);
        ok ? resolve() : reject(new Error("copy failed"));
      } catch (err) {
        reject(err);
      }
    });
  }

  function initInquiry() {
    var form = document.querySelector("form[data-inquiry]");
    if (!form) return;
    var box = document.getElementById("inquiry-result");
    var copyBtn = document.getElementById("copy-inquiry");
    var live = document.getElementById("inquiry-status");

    function isEn() {
      return lang === "en";
    }

    function announce(msg) {
      if (live) live.textContent = msg;
    }

    function showNotice() {
      if (!box) return;
      box.classList.remove("hidden");
      box.setAttribute("role", "status");
      box.innerHTML = isEn()
        ? '<strong>Nothing was sent.</strong> This is a static website: the form does not submit to a server and does not store your details anywhere. Please copy the text below and send it to us by phone or WeChat: <a href="tel:13210025853">13210025853</a>.'
        : '<strong>本表单不会自动发送。</strong>本网站为静态展示站点，表单不会提交到服务器，也不会保存您的信息。请复制下方内容，通过电话或微信发送给工厂：<a href="tel:13210025853">13210025853</a>。';
      if (copyBtn) copyBtn.disabled = false;
      announce(
        isEn() ? "Inquiry details prepared. Nothing was sent." : "询价内容已整理，尚未发送。"
      );
    }

    function doCopy() {
      var text = inquiryLines(form);
      copyText(text).then(
        function () {
          if (copyBtn) {
            copyBtn.textContent = isEn() ? "Copied" : "已复制";
            announce(isEn() ? "Inquiry details copied." : "询价内容已复制。");
            setTimeout(function () {
              copyBtn.textContent = isEn() ? "Copy Inquiry Details" : "复制询价内容";
            }, 2200);
          }
        },
        function () {
          // Clipboard blocked (e.g. file:// in some browsers) — offer manual copy.
          window.prompt(isEn() ? "Copy the inquiry details:" : "请手动复制询价内容：", text);
        }
      );
    }

    form.addEventListener("submit", function (e) {
      e.preventDefault(); // never pretend to send
      showNotice();
    });

    if (copyBtn) {
      copyBtn.addEventListener("click", function () {
        if (typeof form.reportValidity === "function" && !form.reportValidity()) return;
        showNotice();
        doCopy();
      });
    }

    // Keep the notice honest when the language is switched.
    document.addEventListener("languagechange", function () {
      if (box && !box.classList.contains("hidden")) showNotice();
    });
  }

  /* -------------------------------------------------------------------- boot */

  function boot() {
    lang = read();
    setActiveNav();
    initMobileNav();
    initInquiry();
    initCopyButtons();
    translate();
    syncUrl();

    document.querySelectorAll(".lang").forEach(function (btn) {
      btn.addEventListener("click", function () {
        lang = lang === "zh" ? "en" : "zh";
        save(lang);
        translate();
        syncUrl();
      });
    });

    var year = document.getElementById("year");
    if (year) year.textContent = new Date().getFullYear();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();