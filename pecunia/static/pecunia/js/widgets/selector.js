import {debounce} from "../util.js";
import {getAsJson} from '../api.js';
import {Component, createDiv} from "../nodeUtil.js";

export class Selector extends Component {
  constructor(type) {
    super(createDiv({class: 'search-wrapper'}));
    this.type = type;
    this.state = {items: [], highlighted: -1};

    this.suggestionList = document.createElement('ul');
    this.suggestionList.className = 'search-suggestions';
    this.suggestionList.id = 'item-suggestions-' //+ index; FIXME
    this.suggestionList.style.display = "none";

    this.inputField = document.createElement('input');
    this.inputField.setAttribute('type', 'text');
    this.inputField.setAttribute('placeholder', `Search ${this.type}…`);
    this.inputField.setAttribute('role', 'combobox');
    this.inputField.setAttribute('aria-autocomplete', 'list');
    this.inputField.setAttribute('aria-expanded', 'false');
    this.inputField.setAttribute('aria-controls', this.suggestionList.id);

    this.node.append(this.inputField, this.suggestionList);

    this.inputField.addEventListener('input', debounce(this.doSearch.bind(this)));
    this.inputField.addEventListener('keydown', this.onKeyDown.bind(this));

    // fermer au clic extérieur
    document.addEventListener('click', (ev) => {
      if (!this.node.contains(ev.target)) this.hideList();
    });
  }

  get elementId() {
    return this.inputField.getAttribute('data-item-id');
  }

  enable() {
    this.inputField.disabled = false;
  }

  disable() {
    this.inputField.disabled = true;
  }

  hideList() {
    this.suggestionList.style.display = "none";
    this.inputField.setAttribute('aria-expanded', 'false');
    this.inputField.removeAttribute('aria-activedescendant');
    this.state.highlighted = -1;
  };

  showList() {
    this.suggestionList.style.display = "block";
    this.inputField.setAttribute('aria-expanded', 'true');
  };

  render(items) {
    this.suggestionList.innerHTML = '';
    this.state.items = items || [];
    this.state.highlighted = -1;

    if (!items || Object.keys(items).length === 0) {
      const li = document.createElement('li');
      li.className = 'empty';
      li.textContent = 'Aucun résultat';
      li.setAttribute('aria-disabled', 'true');
      this.suggestionList.append(li);
      this.showList();
      return;
    }

    for (const [idx, item] of Object.entries(items)) {
      const li = document.createElement('li');
      li.id = `${this.suggestionList.id}-opt-${idx}`;
      li.setAttribute('role', 'option');
      li.setAttribute('aria-selected', 'false');

      const liContent = document.createElement('div');
      const labelDiv = document.createElement('div');
      const labelSpan = document.createElement('span');
      const qidSpan = document.createElement('span');
      labelDiv.append(labelSpan, qidSpan);
      labelSpan.textContent = item['labels']['en'] ?? "-";
      qidSpan.textContent = `(Q${idx})`;

      const descDiv = document.createElement('div');
      descDiv.textContent = item['descriptions']['en'] ?? "-";
      liContent.append(labelDiv, descDiv);
      li.append(liContent);
      li.dataset.index = idx;

      li.addEventListener('mouseenter', () => this.highlight(idx));
      li.addEventListener('mousedown', (e) => {
        e.preventDefault();
        this.select(idx);
      });

      this.suggestionList.append(li);
    }

    this.showList();
  };

  highlight(idx) {
    const prev = this.suggestionList.querySelector('[aria-selected="true"]');
    if (prev) prev.setAttribute('aria-selected', 'false');

    this.state.highlighted = idx;

    const li = this.suggestionList.querySelector(`#${this.suggestionList.id}-opt-${idx}`);
    if (li) {
      li.setAttribute('aria-selected', 'true');
      this.inputField.setAttribute('aria-activedescendant', li.id);
      const liRect = li.getBoundingClientRect();
      const listRect = this.suggestionList.getBoundingClientRect();
      if (liRect.top < listRect.top || liRect.bottom > listRect.bottom) {
        li.scrollIntoView({block: 'nearest'});
      }
    }
  };

  showValue(label, id) {
    this.inputField.value = (label ?? "-") + ` (${id})`;
    this.inputField.dataset.itemId = id;
  }

  select(idx) {
    const item = this.state.items[idx];
    if (!item) return;
    this.showValue(item['labels']['en'], idx);
    this.hideList();
    this.node.dispatchEvent(new CustomEvent('selectionchanged-' + this.type, {
      bubbles: true,
      detail: {id: idx, label: (item['labels']['en'] ?? "-") + ` (${idx})`}
    }));
  };

  onKeyDown(e) {
    if (this.suggestionList.style.display === "none" && (e.key === 'ArrowDown' || e.key === 'ArrowUp')) {
      if (this.state.items.length) this.showList();
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        if (!Object.keys(this.state.items).length) return;
        this.highlight((this.state.highlighted + 1) % Object.keys(this.state.items).length);
        break;
      case 'ArrowUp':
        e.preventDefault();
        if (!Object.keys(this.state.items).length) return;
        this.highlight((this.state.highlighted - 1 + Object.keys(this.state.items).length) % Object.keys(this.state.items).length);
        break;
      case 'Enter':
        if (this.suggestionList.style.display === "block" && this.state.highlighted >= 0) {
          e.preventDefault();
          this.select(this.state.highlighted);
        }
        break;
      case 'Escape':
        this.hideList();
        break;
    }
  };

  async doSearch() {
    const q = this.inputField.value.trim();
    if (!q) {
      this.hideList();
      return;
    }
    try {
      const items = await getAsJson(
        `/api/${this.type}/?fields=labels,descriptions&label_like=` + encodeURIComponent(q),
        `Unable to search items for ${q}.`
      );

      const result = {};
      for (const [id, item] of Object.entries(items)) {
        result[id] = item;
      }

      this.render(result);
    } catch (err) {
      // en cas d’erreur, afficher une ligne d’état
      this.render([]);
      console.error(err);
    }
  };
}
