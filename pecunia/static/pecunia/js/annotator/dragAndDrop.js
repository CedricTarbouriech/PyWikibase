import {Component, createDiv, createSpan} from "../nodeUtil.js";

/**
 * @typedef {'tagged' | 'untagged'} TokenType
 * @typedef {'unused' | 'unknown' | 'new' | 'linked'} ReconciliationType
 */


const MAX_LENGTH = 75

/**
 *
 */
export class Token {
  /**
   *
   * @type {TokenType}
   */
  static TAGGED = 'tagged';
  /**
   *
   * @type {TokenType}
   */
  static UNTAGGED = 'untagged';

  /**
   *
   * @type {ReconciliationType}
   */
  static UNUSED = 'unused';
  /**
   *
   * @type {ReconciliationType}
   */
  static UNKNOWN = 'unknown';
  /**
   *
   * @type {ReconciliationType}
   */
  static NEW = 'new';
  /**
   *
   * @type {ReconciliationType}
   */
  static LINKED = 'linked';

  /**
   * @param {TokenType} type
   * @param {string} tagId
   * @param {string} tokenId
   * @param {string} text
   */
  constructor(type, tagId, tokenId, text) {
    this.type = type;
    this.tagId = tagId;
    this.tokenId = tokenId;
    this._text = text;
    /**
     *
     * @type {ReconciliationType}
     * @private
     */
    this._reconciliationType = 'unused';
    this.usedIn = new Map();
  }

  getNode(container) {
    if (this.usedIn.has(container)) {
      return this.usedIn.get(container);
    }
    const span = document.createElement('span');
    span.classList.add('entity-token');
    if (this._reconciliationType) {
      span.classList.add('entity-token-' + this._reconciliationType);
    }
    span.setAttribute('draggable', 'true');
    span.setAttribute('data-entity-id', this.tagId);
    span.setAttribute('data-token-id', this.tokenId);
    span.textContent = this._text.substring(0, MAX_LENGTH); // TODO Indiquer avec des points de suspension lorsqu’il y a eu une réduction du texte.
    this.usedIn.set(container, span);
    return span;
  }

  usedInSchema() {
    for (const node of this.usedIn.keys()) {
      if (node.schemaDropZone) return true;
    }
    return false;
  }

  get text() {
    return this._text.substring(0, MAX_LENGTH);
  }

  set text(text) {
    this._text = text;
    for (const node of this.usedIn.values()) {
      node.textContent = this._text.substring(0, MAX_LENGTH);
    }
  }

  /**
   *
   * @returns {ReconciliationType}
   */
  get reconciliationType() {
    return this._reconciliationType;
  }

  /**
   *
   * @param {ReconciliationType} reconciliationType
   */
  set reconciliationType(reconciliationType) {
    for (const node of this.usedIn.values()) {
      node.classList.remove('entity-token-' + this._reconciliationType);
      node.classList.add('entity-token-' + reconciliationType);
    }
    this._reconciliationType = reconciliationType;
  }

  removeFrom(container) {
    this.usedIn.get(container).remove();
    this.usedIn.delete(container);
  }

  delete() {
    for (const container of this.usedIn.keys()) {
      this.removeFrom(container);
    }
  }

  toString() {
    return `Token ${this.tokenId}: ${this.text.substring(0, 15)}`;
  }
}

export class DragAndDropEnv {
  constructor() {
    /**
     *
     * @type {Token}
     */
    this.draggedToken = null;
    this.radioId = 0; // FIXME Remove
  }
}

export class Pool extends Component {
  constructor() {
    super(createDiv({class: 'pool'}));
    /**
     *
     * @type {Record<string, Token>}
     */
    this.tokens = {};
  }

  /**
   *
   * @param id
   */
  get(id) {
    return this.tokens[id];
  }

  /**
   *
   * @param {Token} token
   */
  add(token) {
    this.tokens[token.tagId] = token;
    this.node.append(token.getNode(this));
  }

  has(id) {
    return id in this.tokens;
  }

  aggregate() {
    return this.tokens;
  }
}

class DropZone extends Component {
  /**
   *
   * @param {DragAndDropEnv} env
   * @param node
   */
  constructor(env, node) {
    super(node);
    this.env = env;
    /**
     *
     * @type {DropZone[]}
     */
    this.disjointDropZones = [];
  }

  remove(token) {
    throw new Error('Not implemented!');
  }

  addDisjointDropZone(dropZone) {
    this.disjointDropZones.push(dropZone);
  }
}

export class DeleteDropZone extends DropZone {
  /**
   *
   * @param {DragAndDropEnv} env
   */
  constructor(env) {
    super(env, createDiv({
      class: 'drop-zone multi-drop delete-drop'
    }));

    this.node.append(createSpan('Drop here to delete untagged tokens'));
    this.node.addEventListener('drop', event => {
      const token = this.env.draggedToken;
      if (token.type !== Token.UNTAGGED) {
        alert('Only untagged tokens can be deleted!');
        event.preventDefault();
        return;
      }
      if (!confirm('Are you sure you want to delete this token?')) {
        event.preventDefault();
        return;
      }
      token.delete();

      this.env.draggedToken = null;
    });
  }
}

export class MultiDropZone extends DropZone {
  /**
   *
   * @param env
   * @param {ReconciliationType} reconciliationType
   * @param {(Token) => boolean} condition
   * @param msg
   */
  constructor(env, {reconciliationType, condition, msg}) {
    super(env, createDiv({
      class: 'drop-zone multi-drop'
    }));
    /**
     *
     * @type {Token[]}
     */
    this.tokens = [];
    this.type = reconciliationType;
    this.node.addEventListener('drop', _ => {
      const token = this.env.draggedToken;
      if (condition && condition(token)) {
        alert(msg);
        this.env.draggedToken = null;
        return;
      }
      if (this.tokens.includes(token)) return;

      for (const disjointDropZone of this.disjointDropZones) {
        disjointDropZone.remove(token);
      }

      this.add(token);
      this.env.draggedToken = null;
    });
  }

  aggregate() {
    return this.tokens;
  }

  /**
   *
   * @param {Token} token
   */
  add(token) {
    this.tokens.push(token);
    if (this.type)
      token.reconciliationType = this.type;
    this.node.append(token.getNode(this));
  }

  /**
   *
   * @param {Token} token
   */
  remove(token) {
    const index = this.tokens.indexOf(token);
    if (index !== -1) {
      this.tokens.splice(index, 1);
      token.removeFrom(this);
    }
  }
}

export class SingleDropZone extends DropZone {
  /**
   *
   * @param env
   * @param reconciliationType
   * @param {(Token) => boolean} condition
   * @param msg
   */
  constructor(env, {reconciliationType, condition, msg}) {
    super(env, createSpan('', {class: 'drop-zone single-drop'}));
    this.reconciliationType = reconciliationType;
    this.isDisabled = false;
    this.node.addEventListener('drop', () => {
      if (this.isDisabled) return;
      const token = this.env.draggedToken;
      if (condition && condition(token)) {
        alert(msg);
        this.env.draggedToken = null;
        return;
      }

      this.add(token);
      this.node.dispatchEvent(new CustomEvent('addedtoken', {
        bubbles: true,
        detail: {token: token, dropZone: this}
      }));
      this.env.draggedToken = null;
    });
  }

  /**
   *
   * @param {Token} token
   */
  add(token) {
    this.remove();
    for (const disjointDropZone of this.disjointDropZones) {
      disjointDropZone.remove(token);
    }
    this.token = token;
    if (this.reconciliationType) {
      token.reconciliationType = this.reconciliationType;
    }
    this.node.append(this.token.getNode(this));
  }

  /**
   *
   */
  remove(token) {
    if ((!token && this.token) || (token && this.token === token)) {
      this.token.removeFrom(this);
      this.token = null;
    }
  }

  enable() {
    this.isDisabled = false;
    this.node.classList.remove('disabled');
  }

  disable() {
    this.isDisabled = true;
    this.node.classList.add('disabled');
    this.remove();
  }
}
