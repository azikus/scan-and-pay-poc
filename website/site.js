(() => {
  'use strict';
  const root = document.getElementById('az-scan-pay');
  if (!root || root.dataset.initialized) return;
  root.dataset.initialized = 'true';
  const $ = s => root.querySelector(s);
  const $$ = s => [...root.querySelectorAll(s)];
  const assetBase = new URL($('.sp-mobile-image img').getAttribute('src'), document.baseURI).href.replace(/[^/]+$/, '');
  const asset = name => assetBase + name;
  const steps = [
    ['Capture with confidence.', 'Take a photo or import an image. The latest build also detects and straightens paper on device. You choose when to send it for extraction.', 'Native capture screen with a synthetic invoice'],
    ['Keep the important details.', 'Adjust the crop, rotate the document or return to the original photo. Only an explicit Send uploads the selected image for extraction.', 'Native crop and rotate controls on a synthetic invoice'],
    ['AI proposes. You review.', 'Check extracted values against the image, correct a field and complete missing details. The original result remains separate from your edits.', 'Editable payment review with synthetic recipient and amount'],
    ['One deliberate final check.', 'Review the recipient, amount, destination and reference together. Confirming saves this PoC’s reviewed draft; no payment is executed.', 'Confirmation summary for a synthetic payment draft'],
    ['A clear finish.', 'The review is saved and the app is ready for another document. The live companion follows the confirmed completion state.', 'Native completion screen after a simulated review']
  ];
  let step = 0, appearance = 'dark';
  const animateImage = img => { img.classList.remove('sp-change'); requestAnimationFrame(() => img.classList.add('sp-change')); };
  function updateMobile() {
    $$('[data-step]').forEach((b,i) => { b.setAttribute('aria-selected', String(i === step)); b.tabIndex = i === step ? 0 : -1; });
    const img = $('.sp-mobile-image img');
    img.src = asset(appearance + '-' + String(step + 1).padStart(2,'0') + '.webp');
    img.alt = steps[step][2];
    $('.sp-mobile-image').setAttribute('aria-label', 'Enlarge: ' + steps[step][2]);
    $('[data-step-title]').textContent = steps[step][0];
    $('[data-step-description]').textContent = steps[step][1];
    $('#sp-mobile-panel').setAttribute('aria-labelledby', 'sp-step-' + step);
    animateImage(img);
  }
  $$('[data-step]').forEach(b => b.addEventListener('click', () => {step = Number(b.dataset.step); updateMobile();}));
  $$('[data-appearance]').forEach(b => b.addEventListener('click', () => {
    appearance = b.dataset.appearance;
    $$('[data-appearance]').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
    updateMobile();
  }));
  const spatial = [
    ['See demo accounts, available balances and the scanning area together in one interface.', 'Spatial banking dashboard with demo accounts and activity'],
    ['A detected sample invoice is brought forward for review before the next action.', 'Detected invoice in the spatial banking app preview'],
    ['Review the recipient and amount, then choose the demo account to use.', 'Spatial payment review and demo account selection'],
    ['A simulated receipt records the demo outcome and the updated pretend balance.', 'Simulated payment receipt in the spatial banking app'],
    ['The completed demo payment joins the activity view, keeping the journey in context.', 'Spatial banking transaction history with demo activity']
  ];
  $$('[data-spatial]').forEach(b => b.addEventListener('click', () => {
    const n = Number(b.dataset.spatial);
    $$('[data-spatial]').forEach(x => { x.setAttribute('aria-selected', String(x === b)); x.tabIndex = x === b ? 0 : -1; });
    const img = $('#sp-spatial-screen'); img.src = asset('spatial-' + String(n+1).padStart(2,'0') + '.webp'); img.alt = 'Native Mac UI preview: ' + spatial[n][1];
    img.closest('button').setAttribute('aria-label','Enlarge: ' + spatial[n][1]);
    $('[data-spatial-description]').textContent = spatial[n][0];
    $('#sp-spatial-panel').setAttribute('aria-labelledby',b.id); animateImage(img);
  }));
  $$('[role=tablist]').forEach(list => list.addEventListener('keydown', e => {
    if (!['ArrowRight','ArrowLeft','ArrowDown','ArrowUp','Home','End'].includes(e.key)) return;
    const buttons = [...list.querySelectorAll('[role=tab]')];
    let n = buttons.indexOf(document.activeElement); if(n < 0) return;
    e.preventDefault();
    if(e.key === 'Home') n = 0; else if(e.key === 'End') n = buttons.length-1; else n = (n + (['ArrowRight','ArrowDown'].includes(e.key) ? 1 : -1) + buttons.length) % buttons.length;
    buttons[n].click(); buttons[n].focus();
  }));
  const dialog = $('.sp-lightbox'); let opener;
  $$('[data-enlarge]').forEach(button => button.addEventListener('click', () => {
    opener = button; const image = button.querySelector('img');
    dialog.querySelector('img').src = image.src; dialog.querySelector('img').alt = image.alt;
    dialog.querySelector('p').textContent = image.alt;
    dialog.showModal();
  }));
  $('.sp-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', e => {if(e.target === dialog) dialog.close();});
  dialog.addEventListener('close', () => {if(opener) opener.focus();});
  if ('IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const observer = new IntersectionObserver(entries => entries.forEach(e => {
      if(e.isIntersecting){e.target.classList.remove('sp-pending');observer.unobserve(e.target);}
    }), {threshold:0.035});
    $$('.sp-reveal').forEach(el => {el.classList.add('sp-pending');observer.observe(el);});
  }
})();
