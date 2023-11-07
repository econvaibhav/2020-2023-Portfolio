'use strict';
(() => {
  document.documentElement.classList.add('js');
  const cards = [...document.querySelectorAll('.project-card')];
  const search = document.querySelector('#project-search');
  const subject = document.querySelector('#subject-filter');
  const method = document.querySelector('#method-filter');
  const count = document.querySelector('#result-count');
  const empty = document.querySelector('#empty-state');
  const lensButtons = [...document.querySelectorAll('[data-lens]')];
  let currentLens = 'substance';
  function filterCards() {
    let shown = 0;
    const words = (search?.value || '').toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    for (const card of cards) {
      const subjectOK = !subject.value || card.dataset.subjects.split('|').includes(subject.value);
      const methodOK = !method.value || card.dataset.methods.split('|').includes(method.value);
      const searchOK = words.every(word => card.dataset.search.includes(word));
      card.hidden = !(subjectOK && methodOK && searchOK);
      if (!card.hidden) shown++;
    }
    count.textContent = `${shown} of ${cards.length} projects · ${currentLens === 'substance' ? 'substance' : 'methods'} view`;
    empty.hidden = shown !== 0;
  }
  function setLens(lens) {
    currentLens = lens;
    for (const button of lensButtons) button.setAttribute('aria-pressed', String(button.dataset.lens === lens));
    for (const card of cards) for (const body of card.querySelectorAll('.lens-content')) body.hidden = body.dataset.view !== lens;
    filterCards();
  }
  if (cards.length) {
    search.addEventListener('input', filterCards);
    subject.addEventListener('change', filterCards);
    method.addEventListener('change', filterCards);
    lensButtons.forEach(button => button.addEventListener('click', () => setLens(button.dataset.lens)));
    document.querySelector('#reset-filters').addEventListener('click', () => { search.value = ''; subject.value = ''; method.value = ''; filterCards(); });
    setLens('substance');
  }
  const selected = new Map();
  const tray = document.querySelector('#compare-tray');
  const trayText = document.querySelector('#compare-status');
  const compareButton = document.querySelector('#compare-open');
  const compareDialog = document.querySelector('#compare-dialog');
  const compareBody = document.querySelector('#compare-body');
  const checks = [...document.querySelectorAll('[data-compare]')];
  function updateComparison() {
    tray.hidden = !selected.size;
    trayText.textContent = selected.size === 1 ? '1 selected · choose one more project' : '2 projects · two kinds of evidence';
    compareButton.disabled = selected.size !== 2;
    checks.forEach(box => { box.disabled = selected.size === 2 && !selected.has(box.dataset.compare); });
  }
  checks.forEach(box => box.addEventListener('change', () => {
    if (box.checked) selected.set(box.dataset.compare, box.closest('.project-card'));
    else selected.delete(box.dataset.compare);
    updateComparison();
  }));
  document.querySelector('#compare-clear')?.addEventListener('click', () => {
    selected.clear(); checks.forEach(box => { box.checked = false; box.disabled = false; }); updateComparison();
  });
  function textEl(tag, text, className) {
    const el = document.createElement(tag); el.textContent = text; if (className) el.className = className; return el;
  }
  compareButton?.addEventListener('click', () => {
    if (selected.size !== 2 || !compareDialog.showModal) return;
    compareBody.replaceChildren();
    for (const card of selected.values()) {
      const article = document.createElement('article');
      article.append(textEl('span', card.dataset.area, 'eyebrow'), textEl('h3', card.dataset.title));
      [['Substance', card.dataset.substance], ['Methods', card.dataset.methodtext], ['The connection', card.dataset.bridge], ['Available evidence', card.dataset.evidence]].forEach(([heading, body]) => article.append(textEl('h4', heading), textEl('p', body)));
      const a = textEl('a', 'Open project →'); a.href = card.querySelector('h3 a').getAttribute('href'); article.append(a);
      compareBody.append(article);
    }
    compareDialog.showModal();
  });
  const zoomDialog = document.querySelector('#zoom-dialog');
  const zoomImage = document.querySelector('#zoom-image');
  const zoomCaption = document.querySelector('#zoom-caption');
  document.querySelectorAll('[data-zoom]').forEach(a => a.addEventListener('click', e => {
    if (!zoomDialog?.showModal || e.ctrlKey || e.metaKey || e.shiftKey) return;
    e.preventDefault(); zoomImage.src = a.getAttribute('href'); zoomImage.alt = a.querySelector('img')?.alt || '';
    zoomCaption.textContent = a.dataset.caption || ''; zoomDialog.showModal();
  }));
  document.querySelectorAll('dialog').forEach(dialog => {
    dialog.querySelector('[data-close]')?.addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => {
      if (event.target !== dialog) return;
      const r = dialog.getBoundingClientRect();
      if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close();
    });
  });
  document.querySelectorAll('[data-reader-toggle]').forEach(button => button.addEventListener('click', () => {
    const reader = document.querySelector('.reader');
    const hidden = reader.classList.toggle(`hide-${button.dataset.readerToggle}`);
    button.setAttribute('aria-pressed', String(!hidden));
    button.textContent = `${hidden ? 'Show' : 'Hide'} ${button.dataset.readerToggle === 'code' ? 'code' : 'saved outputs'}`;
  }));
})();
