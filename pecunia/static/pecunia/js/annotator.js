'use strict';

import {Stack} from './stack.js';
// noinspection JSFileReferences
import {getAsJson, postAsJson} from '/static/wikibase/js/api.js';

function addTag(beginTag, endTag) {
  const textarea = document.querySelector('.annotator-text-field');
  let start = textarea.selectionStart;
  let end = textarea.selectionEnd;

  let selection = textarea.value.substring(start, end);
  let tagged = `${beginTag}${selection}${endTag}`;

  const {
    charOverlap,
    msgOverlap
  } = checkCharacterOverlap(textarea.value, selection, start);
  if (charOverlap || checkTagOverlap(textarea.value, selection)) {
    alert(`Erreur dans la sélection : ${msgOverlap}. Impossible d’ajouter les balises.`);
  } else {
    textarea.setRangeText(tagged, start, end, 'end');

    textarea.setSelectionRange(start + 3, start + selection.length + 3);
    textarea.focus();
    textarea.dispatchEvent(new Event('input'));
  }
}

function addWTag() {
  addTag('<w>', '</w>');
}

function addPersonTag() {
  addTag('<w type="person">', '</w>');
}

function addPlaceTag() {
  addTag('<w type="place">', '</w>');
}

function addResourceTag() {
  addTag('<w type="resource">', '</w>');
}

function parseAnnotationTextArea() {
  const textfield = document.querySelector('.annotator-text-field');
  if (!textfield) return;

  const textValue = textfield.value;
  let matchDiv = document.querySelector('div#matchResult');
  if (!matchDiv) {
    matchDiv = document.createElement('div');
    matchDiv.id = "matchResult";
    textfield.after(matchDiv);
  }
  if (document.querySelectorAll('#wbtn').length === 0) {
    const btns = document.createElement('div');
    btns.id = "wbtn";
    for (const [label, fn] of [['<w>', addWTag], ['Person', addPersonTag], ['Place', addPlaceTag], ['Resource', addResourceTag]]) {
      const btn = document.createElement('a');
      btn.classList.add('button');
      btn.textContent = label;
      btn.addEventListener('click', fn);
      btns.append(btn);
    }
    matchDiv.before(btns);
  }

  const parser = new DOMParser();
  const doc = parser.parseFromString(`<xml>${textValue}</xml>`, 'application/xml');
  const wElements = doc.querySelectorAll('w');

  if (wElements && wElements.length > 0) {
    let list = document.createElement('ul');

    wElements.forEach((w, index) => {
      if (w.hasAttribute("part")) return;
      const li = document.createElement('li');
      li.classList.add("typed");
      li.dataset.wIndex = index.toString();
      li.textContent = w.textContent || '';

      if (w.hasAttribute('type')) {
        li.classList.add(`type-${w.getAttribute('type')}`);
      }

      if (w.hasAttribute('qid')) {
        const qid = w.getAttribute('qid');
        const link = document.createElement('a');
        link.setAttribute('href', `/item/${qid}`);
        link.textContent = `Q${qid}`;
        li.append(' lié à ', link);
      } else {
        const newItemBtn = document.createElement('a');
        newItemBtn.setAttribute('href', '#');
        newItemBtn.textContent = 'créer un élément';

        const searchItemBtn = document.createElement('a');
        searchItemBtn.setAttribute('href', '#');
        searchItemBtn.textContent = 'chercher un élément';

        const actionSpan = document.createElement('span');
        actionSpan.append(' (', newItemBtn, ', ', searchItemBtn, ')');
        li.append(actionSpan);

        newItemBtn.addEventListener('click', async event => {
          event.preventDefault();

          if (!window.confirm("Are you sure you want to create a new item?")) return;

          const newItem = await postAsJson('/api/items/new',
            'Erreur lors de la création d’un item.',
            {
              statements: [
                {property: 'is_a', value: w.getAttribute('type')},
                // {property: 'in_document', value: parseInt(window.location.href.match(/(\d+)\/$/)[1], 10)}
              ]
            });
          const displayId = newItem.display_id;

          const idx = parseInt(event.target.closest('li').dataset.wIndex, 10);
          const targetW = wElements[idx];

          targetW.setAttribute('qid', displayId.toString());

          const serializer = new XMLSerializer();
          let xml = serializer.serializeToString(doc.documentElement);
          xml = xml.replace(/^<xml>/, '').replace(/<\/xml>$/, '')
          textfield.value = xml;
          textfield.dispatchEvent(new Event('input'))
        });

        function debounce(fn, wait = 250) {
          let t;
          return (...args) => {
            clearTimeout(t);
            t = setTimeout(() => fn(...args), wait);
          };
        }

        searchItemBtn.addEventListener('click', event => {
          event.preventDefault();

          const wrapper = document.createElement('div');
          wrapper.className = 'search-wrapper';

          const inputField = document.createElement('input');
          inputField.setAttribute('type', 'text');
          inputField.setAttribute('placeholder', 'Search…');

          const list = document.createElement('ul');
          list.className = 'search-suggestions';
          list.id = 'item-suggestions-' + index;
          list.hidden = true;

          inputField.setAttribute('role', 'combobox');
          inputField.setAttribute('aria-autocomplete', 'list');
          inputField.setAttribute('aria-expanded', 'false');
          inputField.setAttribute('aria-controls', list.id);

          const submitBtn = document.createElement('a');
          submitBtn.setAttribute('href', '#');
          submitBtn.className = "button";
          submitBtn.textContent = 'Submit';

          submitBtn.addEventListener('click', event => {
            event.preventDefault();
            const idx = parseInt(event.target.closest('li').dataset.wIndex, 10);
            const targetW = wElements[idx];
            const displayId = inputField.dataset.itemId;

            targetW.setAttribute('qid', displayId.toString());

            const serializer = new XMLSerializer();
            let xml = serializer.serializeToString(doc.documentElement);
            xml = xml.replace(/^<xml>/, '').replace(/<\/xml>$/, '')
            textfield.value = xml;
            textfield.dispatchEvent(new Event('input'))
          });

          const cancelBtn = document.createElement('a');
          cancelBtn.setAttribute('href', '#');
          cancelBtn.className = "button";
          cancelBtn.textContent = 'Cancel';

          cancelBtn.addEventListener('click', event => {
            event.preventDefault();
            console.log('test')
            wrapper.remove();
            actionSpan.style.display = '';
          });

          wrapper.append(inputField, submitBtn, cancelBtn, list);

          actionSpan.style.display = 'none';
          actionSpan.after(wrapper);

          const state = {items: [], highlighted: -1};

          const hideList = () => {
            list.hidden = true;
            inputField.setAttribute('aria-expanded', 'false');
            inputField.removeAttribute('aria-activedescendant');
            state.highlighted = -1;
          };

          const showList = () => {
            list.hidden = false;
            inputField.setAttribute('aria-expanded', 'true');
          };

          const render = (items) => {
            list.innerHTML = '';
            state.items = items || [];
            state.highlighted = -1;

            if (!items || Object.keys(items).length === 0) {
              const li = document.createElement('li');
              li.className = 'empty';
              li.textContent = 'Aucun résultat';
              li.setAttribute('aria-disabled', 'true');
              list.append(li);
              showList();
              return;
            }

            for (const [idx, item] of Object.entries(items)) {
              const li = document.createElement('li');
              li.id = `${list.id}-opt-${idx}`;
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

              li.addEventListener('mouseenter', () => highlight(idx));
              li.addEventListener('mousedown', (e) => {
                e.preventDefault();
                select(idx);
              });

              list.append(li);
            }

            showList();
          };

          const highlight = (idx) => {
            const prev = list.querySelector('[aria-selected="true"]');
            if (prev) prev.setAttribute('aria-selected', 'false');

            state.highlighted = idx;

            const li = list.querySelector(`#${list.id}-opt-${idx}`);
            if (li) {
              li.setAttribute('aria-selected', 'true');
              inputField.setAttribute('aria-activedescendant', li.id);
              const liRect = li.getBoundingClientRect();
              const listRect = list.getBoundingClientRect();
              if (liRect.top < listRect.top || liRect.bottom > listRect.bottom) {
                li.scrollIntoView({block: 'nearest'});
              }
            }
          };

          const select = (idx) => {
            const item = state.items[idx];
            if (!item) return;
            inputField.value = (item['labels']['en'] ?? "-") + ` (Q${idx})`;
            inputField.dataset.itemId = idx;
            hideList();
          };

          const onKeyDown = (e) => {
            if (list.hidden && (e.key === 'ArrowDown' || e.key === 'ArrowUp')) {
              if (state.items.length) showList();
            }

            switch (e.key) {
              case 'ArrowDown':
                e.preventDefault();
                if (!Object.keys(state.items).length) return;
                highlight((state.highlighted + 1) % Object.keys(state.items).length);
                break;
              case 'ArrowUp':
                e.preventDefault();
                if (!Object.keys(state.items).length) return;
                highlight((state.highlighted - 1 + Object.keys(state.items).length) % Object.keys(state.items).length);
                break;
              case 'Enter':
                if (!list.hidden && state.highlighted >= 0) {
                  e.preventDefault();
                  select(state.highlighted);
                }
                break;
              case 'Escape':
                hideList();
                break;
            }
          };

          const doSearch = async () => {
            const q = inputField.value.trim();
            if (!q) {
              hideList();
              return;
            }
            try {
              const items = await getAsJson(
                '/api/items/search/' + encodeURIComponent(q),
                `Unable to search items for ${q}.`
              );
              render(items);
            } catch (err) {
              // en cas d’erreur, afficher une ligne d’état
              render([]);
              console.error(err);
            }
          };

          const debouncedSearch = debounce(doSearch, 250);

          inputField.addEventListener('input', debouncedSearch);
          inputField.addEventListener('keydown', onKeyDown);

          // fermer au clic extérieur
          document.addEventListener('click', (ev) => {
            if (!wrapper.contains(ev.target)) hideList();
          });
        });
      }
      list.append(li);
    });

    matchDiv.textContent = 'Liste des éléments trouvés :';
    matchDiv.append(list);
  } else {
    matchDiv.textContent = 'Pas d’élément trouvé.';
  }
}

/**
 *
 * @param {string} text
 * @param {string} selection
 * @param {number} selectionStart
 * @returns {{charOverlap: boolean, msgOverlap: string}}
 */
function checkCharacterOverlap(text, selection, selectionStart) {
  let stack = new Stack();
  for (const c of selection) {
    if (c === "<") stack.push("<");
    else if (c === ">") {
      if (stack.isEmpty()) {
        return {charOverlap: true, msgOverlap: 'Fin de balise sélectionnée'};
      } else if (stack.top() === "<") {
        stack.pop();
      } else {
        return {charOverlap: true, msgOverlap: ''}; // Cette situation ne peut pas arriver.
      }
    }
  }

  if (!stack.isEmpty())
    return {'charOverlap': true, 'msgOverlap': 'Début de balise sélectionné'};

  for (let i = selectionStart - 1; i >= 0; i--) {
    if (text.at(i) === ">") break;
    if (text.at(i) === "<")
      return {charOverlap: true, msgOverlap: 'Intérieur d’une balise sélectionné'};
  }

  return {charOverlap: false, msgOverlap: ''};
}

function checkTagOverlap(text, selection) {
  let stack = new Stack();
  for (const c of selection) {
    if (c === "<") {
      // TODO Implementer
    }
  }
  return false;
}

let lastSelection = "";

// TODO: Faire en sorte que ça ne soit lancé que pour éditer les textes
document.addEventListener("DOMContentLoaded", () => {
  const annotatorTextField = document.querySelector('.annotator-text-field');
  annotatorTextField.addEventListener('input', parseAnnotationTextArea);
  annotatorTextField.addEventListener('selectionchange', function () {
    let selection = window.getSelection().toString();
    if (selection !== lastSelection) {
      const $warningSpan = document.querySelector('.warning-span');
      lastSelection = selection;
      if (selection.length > 0) {
        const {
          charOverlap,
          msgOverlap
        } = checkCharacterOverlap(annotatorTextField.value, selection, annotatorTextField.selectionStart);
        if (charOverlap || checkTagOverlap(annotatorTextField.value, selection)) {
          $warningSpan.textContent = `Erreur ! (${msgOverlap})`;
        } else {
          $warningSpan.textContent = "Pas d’erreur.";
        }
      } else {
        $warningSpan.textContent = "Pas d’erreur.";
      }
    }
  });

  annotatorTextField.dispatchEvent(new Event('input'));
});