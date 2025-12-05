(function () {
  const STORAGE_KEY = "kbg_consent_v1";

  const defaultConsent = {
    essential: true,
    statistics: false,
    marketing: false,
    external_media: false,
    timestamp: null
  };

  function readConsent() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      return { ...defaultConsent, ...parsed, essential: true };
    } catch (e) {
      return null;
    }
  }

  function saveConsent(consent) {
    const payload = {
      ...defaultConsent,
      ...consent,
      essential: true,
      timestamp: new Date().toISOString()
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    // optional cookie mirror (simple)
    document.cookie = `${STORAGE_KEY}=${encodeURIComponent(JSON.stringify(payload))}; Path=/; Max-Age=31536000; SameSite=Lax`;
    return payload;
  }

  function getCheckboxes() {
    return Array.from(document.querySelectorAll("[data-consent-toggle]"));
  }

  function syncUI(consent) {
    getCheckboxes().forEach(cb => {
      const key = cb.getAttribute("data-consent-toggle");
      cb.checked = !!consent[key];
    });

    // service status texts (optional simple sync)
    document.querySelectorAll(".cookie-service").forEach(service => {
      const title = service.querySelector(".cookie-service__title")?.textContent?.toLowerCase() || "";
      const status = service.querySelector(".cookie-service__status");
      if (!status) return;

      if (title.includes("analytics")) status.textContent = consent.statistics ? "An" : "Aus";
      if (title.includes("meta pixel")) status.textContent = consent.marketing ? "An" : "Aus";
      if (title.includes("google maps")) status.textContent = consent.external_media ? "An" : "Aus";
    });
  }

  // ==== Script loader gate ====
  function loadScriptOnce(id, src) {
    if (document.getElementById(id)) return;
    const s = document.createElement("script");
    s.id = id;
    s.async = true;
    s.src = src;
    document.head.appendChild(s);
  }

  function enableGoogleAnalytics() {
    // Replace with your Measurement ID
    const GA_ID = "G-9VW6BK2ZWT";

    loadScriptOnce("kbg-ga-gtag", `https://www.googletagmanager.com/gtag/js?id=${GA_ID}`);

    window.dataLayer = window.dataLayer || [];
    function gtag(){ window.dataLayer.push(arguments); }
    window.gtag = window.gtag || gtag;

    window.gtag('js', new Date());
    window.gtag('config', GA_ID);
  }

  function enableMetaPixel() {
    // Replace with your Pixel ID if you have one
    const PIXEL_ID = "YOUR_META_PIXEL_ID";
    if (!PIXEL_ID || PIXEL_ID === "YOUR_META_PIXEL_ID") return;

    if (window.fbq) return;

    !(function(f,b,e,v,n,t,s){
      if(f.fbq)return;n=f.fbq=function(){n.callMethod?
      n.callMethod.apply(n,arguments):n.queue.push(arguments)};
      if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
      n.queue=[];t=b.createElement(e);t.async=!0;
      t.src=v;s=b.getElementsByTagName(e)[0];
      s.parentNode.insertBefore(t,s)
    })(window, document,'script','https://connect.facebook.net/en_US/fbevents.js');

    window.fbq('init', PIXEL_ID);
    window.fbq('track', 'PageView');
  }

  // ==== Google Maps gate ====
  function updateFooterMap(consent) {
    const host = document.querySelector("[data-gmaps-host]");
    if (!host) return;

    const placeholder = host.querySelector("[data-gmaps-placeholder]");
    const iframe = host.querySelector("iframe[data-gmaps-iframe]");

    if (consent.external_media) {
      if (placeholder) placeholder.hidden = true;
      if (iframe) iframe.hidden = false;
    } else {
      if (iframe) iframe.hidden = true;
      if (placeholder) placeholder.hidden = false;
    }
  }

  function applyConsent(consent) {
    syncUI(consent);

    if (consent.statistics) enableGoogleAnalytics();
    if (consent.marketing) enableMetaPixel();

    updateFooterMap(consent);
  }

  // ==== Modal UI ====
  function initModal() {
      const modal = document.getElementById("cookieModal");
      if (!modal) return;

      const viewMain = modal.querySelector('[data-cookie-view="main"]');
      const viewDetails = modal.querySelector('[data-cookie-view="details"]');

      const ANIM_MS = 500;

      function showView(which) {
        if (which === "details") {
          viewMain.hidden = true;
          viewDetails.hidden = false;
        } else {
          viewDetails.hidden = true;
          viewMain.hidden = false;
        }
      }

      function openModal(view = "main") {
        showView(view);
        modal.classList.add("is-open");
        document.body.style.overflow = "hidden";
      }

      function closeModal() {
        modal.classList.remove("is-open");

        // overflow erst nach Fade zurücksetzen
        window.setTimeout(() => {
          if (!modal.classList.contains("is-open")) {
            document.body.style.overflow = "";
          }
        }, ANIM_MS);
      }

      // open links
      document.querySelectorAll("[data-cookie-open]").forEach(el => {
        el.addEventListener("click", (e) => {
          e.preventDefault();
          openModal("details");
        });
      });

      // close
      modal.querySelectorAll("[data-cookie-close]").forEach(btn => {
        btn.addEventListener("click", closeModal);
      });

      // Buttons
      const btnAcceptAll = modal.querySelector("[data-cookie-accept-all]");
      const btnEssential = modal.querySelector("[data-cookie-accept-essential]");
      const btnOpenDetails = modal.querySelector("[data-cookie-open-details]");
      const btnSave = modal.querySelector("[data-cookie-save]");
      const btnBack = modal.querySelector("[data-cookie-back]");

      if (btnAcceptAll) btnAcceptAll.addEventListener("click", () => {
        const consent = saveConsent({
          statistics: true,
          marketing: true,
          external_media: true
        });
        applyConsent(consent);
        closeModal();
      });

      if (btnEssential) btnEssential.addEventListener("click", () => {
        const consent = saveConsent({
          statistics: false,
          marketing: false,
          external_media: false
        });
        applyConsent(consent);
        closeModal();
      });

      if (btnOpenDetails) btnOpenDetails.addEventListener("click", () => {
        showView("details");
      });

      if (btnBack) btnBack.addEventListener("click", () => {
        showView("main");
      });

      if (btnSave) btnSave.addEventListener("click", () => {
        const consent = collectConsentFromUI();
        const saved = saveConsent(consent);
        applyConsent(saved);
        closeModal();
      });

      // Checkbox changes (live sync)
      function collectConsentFromUI() {
        const c = { ...defaultConsent };
        getCheckboxes().forEach(cb => {
          const key = cb.getAttribute("data-consent-toggle");
          c[key] = cb.checked;
        });
        return c;
      }

      getCheckboxes().forEach(cb => {
        cb.addEventListener("change", () => {
          const temp = collectConsentFromUI();
          syncUI(temp);
          updateFooterMap(temp);
        });
      });

      // ===== Accordion: only one open + Ausklappen/Einklappen Text =====
      const triggers = Array.from(modal.querySelectorAll("[data-acc-trigger]"));

      function updateAccTexts() {
        triggers.forEach(tr => {
          const key = tr.getAttribute("data-acc-trigger");
          const panel = modal.querySelector(`[data-acc-panel="${key}"]`);
          const textEl = modal.querySelector(`[data-acc-toggle-text="${key}"]`);
          if (!textEl || !panel) return;
          textEl.textContent = panel.hidden ? "Ausklappen" : "Einklappen";
        });
      }

      triggers.forEach(tr => {
        tr.addEventListener("click", (e) => {
          // Clicking on switch should not toggle accordion
          if (e.target.closest(".cookie-switch")) return;

          const key = tr.getAttribute("data-acc-trigger");
          const panel = modal.querySelector(`[data-acc-panel="${key}"]`);
          if (!panel) return;

          // close others
          triggers.forEach(other => {
            const ok = other.getAttribute("data-acc-trigger");
            const op = modal.querySelector(`[data-acc-panel="${ok}"]`);
            if (op && op !== panel) op.hidden = true;
          });

          panel.hidden = !panel.hidden;
          updateAccTexts();
        });
      });

      // Initial show if no consent
      const existing = readConsent();
      if (!existing) {
        openModal("main");
      } else {
        applyConsent(existing);
      }

      // Initial accordion texts
      updateAccTexts();
  }

  document.addEventListener("DOMContentLoaded", initModal);
})();
