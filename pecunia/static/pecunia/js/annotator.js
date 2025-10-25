import {debounce} from "./util.js";
import {Pool, Token} from "./dragAndDrop.js";
import {Stack} from "./stack.js";
import {createButton, createSpan} from "./nodeUtil.js";

/**
 * Returns the next free id for a new tag.
 * If text does not contain any tags, returns 1;
 * @param {string} text the text to search tags into
 * @returns {number} the next free id
 */
function getNextFreeTagId(text) {
  const ids = text.matchAll(/<w id="(\d+)">/g).map(m => parseInt(m[1]));
  return Math.max(...ids, 0) + 1;
}

function getNextFreeUntagId() {
  // TODO Implement
  return 1;
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

export default class Annotator {
  constructor() {
    this._node = document.getElementById('annotator');
    this.textArea = document.getElementById('id_text');
    this.textArea.addEventListener('input', debounce(_ => this.updateTokensFromText()));

    const buttonsDiv = document.createElement('div');
    this._node.append(buttonsDiv);

    let tagId = getNextFreeTagId(this.textArea.value);
    const tagButton = createButton('Tag entity', {
      id: 'tag-button', type: 'button'
    });
    tagButton.addEventListener('click', _ => {
      this.tag(this.textArea, tagId);
      this.textArea.dispatchEvent(new CustomEvent('input', {}));
      tagId++;
    });

    let untagId = getNextFreeUntagId();
    const newUntaggedEntityButton = createButton('Add untagged entity', {
      id: 'new-untagged-button', type: 'button'
    });
    newUntaggedEntityButton.addEventListener('click', _ => {
      const label = prompt('Please enter a tag label.');
      if (!label) return;
      this.untaggedEntitiesPool.add(new Token(untagId.toString(), `u${untagId}`, label));
      this.untaggedEntitiesPool.refresh();
      untagId++;
    });

    buttonsDiv.append(tagButton, newUntaggedEntityButton);

    this.taggedEntitiesPool = new Pool();
    this.untaggedEntitiesPool = new Pool();
    this._node.append(
      createSpan('Tagged entities'), this.taggedEntitiesPool.node,
      createSpan('Untagged entities'), this.untaggedEntitiesPool.node
    );
  }

  get node() {
    return this._node;
  }

  aggregate() {
    return {
      taggedEntities: this.taggedEntitiesPool.aggregate(),
      untaggedEntities: this.untaggedEntitiesPool.aggregate()
    };
  }

  updateTokensFromText() {
    const parser = new DOMParser();
    const doc = parser.parseFromString(`<xml>${this.textArea.value}</xml>`, 'application/xml');
    const wTags = doc.querySelectorAll('w');

    for (const wTag of wTags) {
      const tagId = wTag.getAttribute('id');
      if (tagId.length === 0) continue;
      if (this.taggedEntitiesPool.has(tagId)) {
        this.taggedEntitiesPool.get(tagId).text = wTag.textContent;
      } else {
        this.taggedEntitiesPool.add(new Token(tagId, `t${tagId}`, wTag.textContent));
      }
    }

    // TODO Prendre en charge si un élément est supprimé

    this.taggedEntitiesPool.refresh();
    document.dispatchEvent(new Event('refreshtokens'));
  }

  /**
   * Adds the w tag around the selected text. An id is added to the tag.
   * If the text begins or ends with spaces, trims the selection.
   * @param {HTMLTextAreaElement} textArea Text component in which the operations are done.
   * @param {int} tagId The numeric id added to the tag.
   */
  tag(textArea, tagId) {
    while (textArea.selectionStart < textArea.selectionEnd && textArea.value.at(textArea.selectionStart) === " ")
      textArea.selectionStart++;
    while (textArea.selectionStart < textArea.selectionEnd && textArea.value.at(textArea.selectionEnd - 1) === " ")
      textArea.selectionEnd--;
    const before = textArea.value.substring(0, textArea.selectionStart);
    const selection = textArea.value.substring(textArea.selectionStart, textArea.selectionEnd);
    const after = textArea.value.substring(textArea.selectionEnd);
    if (selection.length === 0) throw new Error("Empty selection!");
    // TODO vérifier que la sélection ne chevauche pas de balises
    textArea.value = `${before}<w id="${tagId}">${selection}</w>${after}`;
  }

  /**
   *
   * @param {string} tokenId
   * @return {Token}
   */
  getToken(tokenId) {
    const type = tokenId.charAt(0);
    const id = tokenId.slice(1);

    switch (type) {
      case "u":
        return this.untaggedEntitiesPool.get(id);
      case "t":
        return this.taggedEntitiesPool.get(id);
      default:
        throw new Error(`Unknown token type: ${type}!`);
    }
  }
}