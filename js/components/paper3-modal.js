(function () {
  'use strict';

  // -- Config (change endpoint here if you switch form providers) --
  var FORMSPREE_ENDPOINT = 'https://formspree.io/f/mykvjjek';

  var STORAGE_KEY  = 'eap_p3_seen';
  var EXPIRY_MS    = 7 * 24 * 60 * 60 * 1000; // 7 days

  // -- Persistence helpers ------------------------------------

  function hasSeenRecently() {
    try {
      var val = localStorage.getItem(STORAGE_KEY);
      if (!val) return false;
      return (Date.now() - parseInt(val, 10)) < EXPIRY_MS;
    } catch (e) {
      // Cookie fallback
      return document.cookie.split(';').some(function (c) {
        return c.trim().indexOf(STORAGE_KEY + '=') === 0;
      });
    }
  }

  function markSeen() {
    try {
      localStorage.setItem(STORAGE_KEY, String(Date.now()));
    } catch (e) {
      // Cookie fallback
      var d = new Date(Date.now() + EXPIRY_MS);
      document.cookie = STORAGE_KEY + '=1; expires=' + d.toUTCString() + '; path=/';
    }
  }

  // -- Modal HTML ---------------------------------------------

  function buildModalHTML() {
    return [
      '<div id="eap-modal-overlay" class="eap-modal__overlay"',
      '  role="dialog" aria-modal="true" aria-labelledby="eap-modal-heading">',
      '  <div class="eap-modal__dialog" id="eap-modal-dialog">',
      '    <button class="eap-modal__close" id="eap-modal-close"',
      '      aria-label="Close this dialog">&#x2715;</button>',

      /* ---- Step 1: Teaser ---- */
      '    <div class="eap-modal__step eap-modal__step--active" id="eap-step-1">',
      '      <span class="eap-modal__badge">Group Revision &mdash; 3rd June 2026</span>',
      '      <h2 class="eap-modal__title" id="eap-modal-heading">',
      '        Paper 3 Group Revision Sessions</h2>',
      '      <p class="eap-modal__subtitle">',
      '        I\'m running two live online sessions on Paper 3 exam technique',
      '        &mdash; one for AQA, one for Edexcel A &mdash; the day before',
      '        the exam. Each session is packed with high-value tips and',
      '        technique for the areas that commonly come up.</p>',
      '      <div class="eap-modal__actions">',
      '        <button class="eap-modal__btn" id="eap-btn-details">See details</button>',
      '        <button class="eap-modal__btn eap-modal__btn--alt"',
      '          id="eap-btn-register-1">Register interest</button>',
      '      </div>',
      '    </div>',

      /* ---- Step 2: Details ---- */
      '    <div class="eap-modal__step" id="eap-step-2">',
      '      <span class="eap-modal__badge">Wednesday 3rd June 2026 &mdash; Live Online</span>',
      '      <h2 class="eap-modal__title">Session Details</h2>',
      '      <div class="eap-modal__session">',
      '        <div class="eap-modal__session-board">AQA</div>',
      '        <div class="eap-modal__session-time">11:00 &ndash; 12:00 BST</div>',
      '        <p class="eap-modal__session-desc">Navigating the difficult',
      '          multiple-choice questions, plus exam technique and tips for',
      '          the 10, 15 and 25-mark questions. Covers the high-value topics',
      '          that commonly come up in Paper 3.</p>',
      '      </div>',
      '      <div class="eap-modal__session">',
      '        <div class="eap-modal__session-board">Edexcel A</div>',
      '        <div class="eap-modal__session-time">14:00 &ndash; 15:00 BST</div>',
      '        <p class="eap-modal__session-desc">Exam technique for the 5, 8,',
      '          12 and 25-mark questions, focused on the high-value points that',
      '          commonly appear in Paper 3.</p>',
      '      </div>',
      '      <div class="eap-modal__price">',
      '        &pound;20 per student &nbsp;&middot;&nbsp; 1 hour',
      '        &nbsp;&middot;&nbsp; Live online (Zoom)',
      '      </div>',
      '      <div class="eap-modal__actions">',
      '        <button class="eap-modal__btn" id="eap-btn-register-2">',
      '          Register my interest</button>',
      '      </div>',
      '    </div>',

      /* ---- Step 3: Registration form ---- */
      '    <div class="eap-modal__step" id="eap-step-3">',
      '      <span class="eap-modal__badge">Register Interest</span>',
      '      <h2 class="eap-modal__title">Reserve your spot</h2>',
      '      <p class="eap-modal__subtitle">No payment now &mdash; once I know',
      '        the numbers I\'ll send a Stripe payment link and the Zoom joining',
      '        link closer to the time.</p>',
      '      <form id="eap-modal-form" novalidate>',
      '        <div class="eap-modal__form-group" id="eap-field-name">',
      '          <label class="eap-modal__label" for="eap-name">',
      '            Name <span aria-hidden="true">*</span></label>',
      '          <input class="eap-modal__input" type="text" id="eap-name"',
      '            name="name" autocomplete="name" required>',
      '          <span class="eap-modal__error-msg" id="eap-err-name" role="alert">',
      '            Please enter your name.</span>',
      '        </div>',
      '        <div class="eap-modal__form-group" id="eap-field-email">',
      '          <label class="eap-modal__label" for="eap-email">',
      '            Email <span aria-hidden="true">*</span></label>',
      '          <input class="eap-modal__input" type="email" id="eap-email"',
      '            name="email" autocomplete="email" required>',
      '          <span class="eap-modal__error-msg" id="eap-err-email" role="alert">',
      '            Please enter a valid email address.</span>',
      '        </div>',
      '        <div class="eap-modal__form-group" id="eap-field-board">',
      '          <label class="eap-modal__label" for="eap-board">',
      '            Exam board <span aria-hidden="true">*</span></label>',
      '          <select class="eap-modal__select" id="eap-board"',
      '            name="exam_board" required>',
      '            <option value="">&#8212; Please select &#8212;</option>',
      '            <option value="AQA">AQA</option>',
      '            <option value="Edexcel A">Edexcel A</option>',
      '            <option value="Both / Not sure">Both / Not sure</option>',
      '          </select>',
      '          <span class="eap-modal__error-msg" id="eap-err-board" role="alert">',
      '            Please select your exam board.</span>',
      '        </div>',
      '        <div class="eap-modal__form-group" id="eap-field-consent">',
      '          <div class="eap-modal__consent-row">',
      '            <input class="eap-modal__consent-checkbox" type="checkbox"',
      '              id="eap-consent" name="consent" required>',
      '            <label class="eap-modal__consent-label" for="eap-consent">',
      '              By registering you agree that I can email you about this',
      '              revision session. <span aria-hidden="true">*</span></label>',
      '          </div>',
      '          <span class="eap-modal__error-msg" id="eap-err-consent" role="alert">',
      '            Please tick the consent box to continue.</span>',
      '        </div>',
      '        <input type="hidden" name="_subject"',
      '          value="New Paper 3 session interest">',
      '        <div class="eap-modal__actions">',
      '          <button class="eap-modal__btn" type="submit" id="eap-submit">',
      '            Register my interest</button>',
      '        </div>',
      '        <div class="eap-modal__submit-error" id="eap-submit-error" role="alert">',
      '          Something went wrong &mdash; please try again, or email me at',
      '          <a href="mailto:eliotking01@gmail.com">eliotking01@gmail.com</a>.',
      '        </div>',
      '      </form>',
      '    </div>',

      /* ---- Step 4: Confirmation ---- */
      '    <div class="eap-modal__step" id="eap-step-4">',
      '      <div class="eap-modal__confirm-check" aria-hidden="true">&#10003;</div>',
      '      <h2 class="eap-modal__title">You\'re registered!</h2>',
      '      <p class="eap-modal__subtitle">',
      '        Thank you &mdash; I\'ll be in touch closer to the time with a',
      '        Stripe payment link and the Zoom joining link, once I know the',
      '        numbers. <strong>Registering is not yet a payment.</strong></p>',
      '      <p class="eap-modal__confirm-note">',
      '        Looking for extra support before the exam? You can also',
      '        <a href="/tutoring.html">book a 1-on-1 tutoring session</a> or',
      '        <a href="/marking.html">submit a practice paper for marking</a>',
      '        via the site.</p>',
      '      <div class="eap-modal__actions">',
      '        <button class="eap-modal__btn eap-modal__btn--alt" id="eap-btn-close-confirm">',
      '          Close</button>',
      '      </div>',
      '    </div>',

      '  </div>',
      '</div>'
    ].join('\n');
  }

  // -- Tab HTML -----------------------------------------------

  function buildTabHTML() {
    return '<button id="eap-tab-btn" class="eap-tab"' +
      ' aria-label="View Paper 3 group revision sessions">' +
      'Paper 3 Sessions' +
      '</button>';
  }

  // -- Validation helpers -------------------------------------

  function isValidEmail(val) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val.trim());
  }

  function setFieldValid(fieldEl, errEl) {
    fieldEl.classList.remove('eap-modal__field--invalid');
    errEl.classList.remove('eap-modal__error-msg--visible');
  }

  function setFieldInvalid(fieldEl, errEl) {
    fieldEl.classList.add('eap-modal__field--invalid');
    errEl.classList.add('eap-modal__error-msg--visible');
  }

  function validateForm() {
    var ok = true;

    var nameField = document.getElementById('eap-field-name');
    var nameInput = document.getElementById('eap-name');
    var nameErr   = document.getElementById('eap-err-name');
    if (!nameInput.value.trim()) {
      setFieldInvalid(nameField, nameErr); ok = false;
    } else {
      setFieldValid(nameField, nameErr);
    }

    var emailField = document.getElementById('eap-field-email');
    var emailInput = document.getElementById('eap-email');
    var emailErr   = document.getElementById('eap-err-email');
    if (!isValidEmail(emailInput.value)) {
      setFieldInvalid(emailField, emailErr); ok = false;
    } else {
      setFieldValid(emailField, emailErr);
    }

    var boardField = document.getElementById('eap-field-board');
    var boardInput = document.getElementById('eap-board');
    var boardErr   = document.getElementById('eap-err-board');
    if (!boardInput.value) {
      setFieldInvalid(boardField, boardErr); ok = false;
    } else {
      setFieldValid(boardField, boardErr);
    }

    var consentField = document.getElementById('eap-field-consent');
    var consentInput = document.getElementById('eap-consent');
    var consentErr   = document.getElementById('eap-err-consent');
    if (!consentInput.checked) {
      setFieldInvalid(consentField, consentErr); ok = false;
    } else {
      setFieldValid(consentField, consentErr);
    }

    return ok;
  }

  // -- Step navigation ----------------------------------------

  function showStep(n) {
    var steps = document.querySelectorAll('.eap-modal__step');
    for (var i = 0; i < steps.length; i++) {
      steps[i].classList.remove('eap-modal__step--active');
    }
    var target = document.getElementById('eap-step-' + n);
    if (target) {
      target.classList.add('eap-modal__step--active');
      var firstFocusable = target.querySelector(
        'button,input,select,textarea,a[href],[tabindex]:not([tabindex="-1"])'
      );
      if (firstFocusable) firstFocusable.focus();
    }
  }

  // -- Focus trap ---------------------------------------------

  var FOCUSABLE_SELECTORS =
    'a[href],button:not([disabled]),input:not([disabled]),' +
    'select:not([disabled]),textarea:not([disabled]),' +
    '[tabindex]:not([tabindex="-1"])';

  function trapFocus(e) {
    if (e.key !== 'Tab') return;
    var dialog = document.getElementById('eap-modal-dialog');
    var focusable = Array.prototype.slice.call(
      dialog.querySelectorAll(FOCUSABLE_SELECTORS)
    );
    if (!focusable.length) return;
    var first = focusable[0];
    var last  = focusable[focusable.length - 1];
    if (e.shiftKey) {
      if (document.activeElement === first) {
        e.preventDefault();
        last.focus();
      }
    } else {
      if (document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  }

  // -- Open / Close -------------------------------------------

  var previouslyFocused = null;
  var modalIsOpen = false;

  function openModal() {
    var overlay = document.getElementById('eap-modal-overlay');
    if (!overlay || modalIsOpen) return;

    // Always open at step 1 (whether auto-triggered or via tab)
    var steps = document.querySelectorAll('.eap-modal__step');
    for (var i = 0; i < steps.length; i++) {
      steps[i].classList.remove('eap-modal__step--active');
    }
    document.getElementById('eap-step-1').classList.add('eap-modal__step--active');

    modalIsOpen = true;
    previouslyFocused = document.activeElement;
    overlay.classList.add('eap-modal__overlay--visible');
    document.body.style.overflow = 'hidden';
    document.addEventListener('keydown', handleKeydown);

    // Hide tab while modal is open
    var tab = document.getElementById('eap-tab-btn');
    if (tab) tab.classList.add('eap-tab--hidden');

    var dialog = document.getElementById('eap-modal-dialog');
    var first  = dialog.querySelector(FOCUSABLE_SELECTORS);
    if (first) first.focus();
  }

  function closeModal() {
    var overlay = document.getElementById('eap-modal-overlay');
    if (!overlay) return;
    modalIsOpen = false;
    overlay.classList.remove('eap-modal__overlay--visible');
    document.body.style.overflow = '';
    document.removeEventListener('keydown', handleKeydown);

    // Restore tab
    var tab = document.getElementById('eap-tab-btn');
    if (tab) tab.classList.remove('eap-tab--hidden');

    if (previouslyFocused && previouslyFocused.focus) {
      previouslyFocused.focus();
    }
  }

  function handleKeydown(e) {
    if (e.key === 'Escape') {
      e.preventDefault();
      closeModal();
    } else if (e.key === 'Tab') {
      trapFocus(e);
    }
  }

  // -- Form submission ----------------------------------------

  function handleSubmit(e) {
    e.preventDefault();
    if (!validateForm()) return;

    var submitBtn   = document.getElementById('eap-submit');
    var errorBanner = document.getElementById('eap-submit-error');

    submitBtn.disabled = true;
    submitBtn.textContent = 'Sending…';
    errorBanner.classList.remove('eap-modal__submit-error--visible');

    var payload = {
      name:       document.getElementById('eap-name').value.trim(),
      email:      document.getElementById('eap-email').value.trim(),
      exam_board: document.getElementById('eap-board').value,
      consent:    'Yes — agreed to be emailed about this session',
      _subject:   'New Paper 3 session interest'
    };

    fetch(FORMSPREE_ENDPOINT, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body:    JSON.stringify(payload)
    })
      .then(function (res) {
        if (res.ok) {
          showStep(4);
        } else {
          throw new Error('Non-OK response');
        }
      })
      .catch(function () {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Register my interest';
        errorBanner.classList.add('eap-modal__submit-error--visible');
      });
  }

  // -- Wire up events -----------------------------------------

  function bindEvents() {
    // Close button
    document.getElementById('eap-modal-close')
      .addEventListener('click', closeModal);

    // Backdrop click (click on overlay, not dialog)
    document.getElementById('eap-modal-overlay')
      .addEventListener('click', function (e) {
        if (e.target === e.currentTarget) closeModal();
      });

    // Step 1 → Step 2 (See details)
    document.getElementById('eap-btn-details')
      .addEventListener('click', function () { showStep(2); });

    // Step 1 → Step 3 (Register interest — skip details)
    document.getElementById('eap-btn-register-1')
      .addEventListener('click', function () { showStep(3); });

    // Step 2 → Step 3
    document.getElementById('eap-btn-register-2')
      .addEventListener('click', function () { showStep(3); });

    // Form submit
    document.getElementById('eap-modal-form')
      .addEventListener('submit', handleSubmit);

    // Step 4 close
    document.getElementById('eap-btn-close-confirm')
      .addEventListener('click', closeModal);

    // Persistent tab reopens at step 1 (not gated by localStorage)
    document.getElementById('eap-tab-btn')
      .addEventListener('click', openModal);
  }

  // -- Inject CSS ---------------------------------------------

  function injectCSS() {
    var link  = document.createElement('link');
    link.rel  = 'stylesheet';
    link.href = '/css/paper3-modal.css';
    document.head.appendChild(link);
  }

  // -- Init ---------------------------------------------------
  // The modal + tab are always injected so the tab works for all visitors.
  // The automatic first-visit open is gated on the localStorage flag.

  function init() {
    injectCSS();
    document.body.insertAdjacentHTML('beforeend', buildModalHTML());
    document.body.insertAdjacentHTML('beforeend', buildTabHTML());
    bindEvents();

    if (!hasSeenRecently()) {
      markSeen();
      // Show after page settle (is-preload removed at window.load + 100ms)
      window.addEventListener('load', function () {
        setTimeout(openModal, 500);
      });
      // Guard: if load already fired (script loaded late), show shortly
      if (document.readyState === 'complete') {
        setTimeout(openModal, 200);
      }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
}());
