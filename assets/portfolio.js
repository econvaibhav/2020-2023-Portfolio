'use strict';
(() => {
  document.documentElement.classList.add('js');
  const cards = [...document.querySelectorAll('.project-card')];
  const search = document.querySelector('#project-search');
  const filters = [...document.querySelectorAll('[data-category]')];
  const count = document.querySelector('#result-count');
  const empty = document.querySelector('#empty-state');
  const reset = document.querySelector('#reset-filters');
  let category = '';

  function filterCards() {
    const words = search.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    let shown = 0;
    cards.forEach(card => {
      const categoryOK = !category || card.dataset.categories.split('|').includes(category);
      const searchOK = words.every(word => card.dataset.search.includes(word));
      card.hidden = !(categoryOK && searchOK);
      if (!card.hidden) shown++;
    });
    count.textContent = shown === cards.length ? `${shown} projects` : `${shown} of ${cards.length} projects`;
    empty.hidden = shown !== 0;
    reset.hidden = !category && !search.value;
    filters.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.category === category)));
  }

  if (cards.length && search && count && empty && reset) {
    search.addEventListener('input', filterCards);
    filters.forEach(button => button.addEventListener('click', () => {
      category = button.dataset.category;
      filterCards();
    }));
    reset.addEventListener('click', () => {
      search.value = '';
      category = '';
      filterCards();
    });
    filterCards();
  }

  const zoom = document.querySelector('#zoom-dialog');
  const zoomImage = document.querySelector('#zoom-image');
  const zoomCaption = document.querySelector('#zoom-caption');
  document.querySelectorAll('[data-zoom]').forEach(anchor => anchor.addEventListener('click', event => {
    if (!zoom?.showModal || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    zoomImage.src = anchor.getAttribute('href');
    zoomImage.alt = anchor.querySelector('img')?.alt || '';
    zoomCaption.textContent = anchor.dataset.caption || '';
    zoom.showModal();
  }));
  document.querySelectorAll('dialog').forEach(dialog => {
    dialog.querySelector('[data-close]')?.addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => {
      if (event.target !== dialog) return;
      const box = dialog.getBoundingClientRect();
      if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
    });
  });

  document.querySelectorAll('[data-reader-toggle]').forEach(button => button.addEventListener('click', () => {
    const reader = document.querySelector('.reader');
    if (!reader) return;
    const hidden = reader.classList.toggle(`hide-${button.dataset.readerToggle}`);
    button.setAttribute('aria-pressed', String(!hidden));
    button.textContent = `${hidden ? 'Show' : 'Hide'} ${button.dataset.readerToggle === 'code' ? 'code' : 'saved outputs'}`;
  }));
})();
