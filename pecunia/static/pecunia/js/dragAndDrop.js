import {createDiv} from "./nodeUtil.js";

export class Token {
  /**
   *
   * @param {string} tagId
   * @param {string} tokenId
   * @param {string} text
   */
  constructor(tagId, tokenId, text) {
    this.tagId = tagId;
    this.tokenId = tokenId
    this.text = text;
  }

  get node() {
    const span = document.createElement('span');
    span.classList.add('entity-token');
    span.setAttribute('draggable', 'true');
    span.setAttribute('data-entity-id', this.tagId);
    span.setAttribute('data-token-id', this.tokenId);
    span.textContent = this.text;
    return span;
  }
}

export class DragAndDropEnv {
  constructor() {
    this.draggedToken = null;
  }
}

export class Pool {
  constructor() {
    this.tokens = {};
    this._node = document.createElement('div');
    this._node.className = 'pool';
  }

  get node() {
    return this._node;
  }

  get(id) {
    return this.tokens[id];
  }

  /**
   *
   * @param {Token} token
   */
  add(token) {
    this.tokens[token.tagId] = token;
  }

  has(id) {
    return id in this.tokens;
  }

  refresh() {
    this._node.innerHTML = "";
    for (const token of Object.values(this.tokens)) {
      this._node.append(token.node);
    }
  }

  aggregate() {
    return this.tokens;
  }
}

class DropZone {
  constructor(env) {
    this.env = env;
    this.disjointDropZones = [];
  }

  addDisjointDropZone(dropZone) {
    this.disjointDropZones.push(dropZone);
  }
}

export class MultiDropZone extends DropZone {
  constructor(env) {
    super(env);
    this.tokens = [];
    this._node = createDiv({
      class: 'drop-zone multi-drop'
    });

    this._node.addEventListener('drop', _ => {
      const token = this.env.draggedToken;
      if (this.tokens.includes(token)) return;

      for (const disjointDropZone of this.disjointDropZones) {
        disjointDropZone.remove(token);
        disjointDropZone.refresh();
      }

      this.add(token);
      this.env.draggedToken = null;
      this.refresh();
    });
  }

  aggregate() {
    return this.tokens;
  }

  get node() {
    return this._node;
  }

  /**
   *
   * @param {Token} token
   */
  add(token) {
    this.tokens.push(token);
    this._node.append(token.node);
  }

  /**
   *
   * @param {Token} token
   */
  remove(token) {
    const index = this.tokens.indexOf(token);
    if (index !== -1)
      this.tokens.splice(index, 1);
  }

  refresh() {
    this._node.innerHTML = "";
    this._node.append(...this.tokens.map(token => token.node));
  }
}

export class SingleDropZone extends DropZone {
  constructor(env) {
    super(env);
    this.env = env;
    this._node = document.createElement('span');
    this._node.classList.add('drop-zone', 'single-drop');
    this._node.addEventListener('drop', event => {
      const token = this.env.draggedToken;
      for (const disjointDropZone of this.disjointDropZones) {
        disjointDropZone.remove(token);
        disjointDropZone.refresh();
      }

      this.add(token);
      this.refresh();
    });
  }

  /**
   *
   * @param {Token} token
   */
  add(token) {
    this.token = token;
  }

  /**
   *
   * @param {Token} token
   */
  remove(token) {
    if (this.token === token) {
      this.token = null;
    }
  }

  get node() {
    return this._node;
  }

  refresh() {
    this._node.innerHTML = "";
    if (this.token) {
      this._node.append(this.token.node);
    }
  }
}
