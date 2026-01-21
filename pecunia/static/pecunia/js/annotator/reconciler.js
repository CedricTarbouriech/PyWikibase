import {MultiDropZone, SingleDropZone, Token} from "./dragAndDrop.js";
import {Selector} from "../widgets/selector.js";
import {
  Component,
  createButton,
  createCollapsible,
  createDeleteButton,
  createDiv,
  createSpan,
  deleteListener
} from "../nodeUtil.js";


/**
 * Represents a link between a token and an entity.
 */
class Link extends Component {
  constructor(env, dropZones) {
    super(createDiv({class: 'linked-entity'}));
    this.dropZone = new SingleDropZone(env, {reconciliationType: 'linked'});
    this.selector = new Selector('items');

    const deleteButton = createDeleteButton('link', this);
    this.node.append(deleteButton, this.dropZone.node, createSpan(' — '), this.selector.node);

    for (const otherDropZone of dropZones) {
      this.dropZone.addDisjointDropZone(otherDropZone);
      otherDropZone.addDisjointDropZone(this.dropZone);
    }
  }

  aggregate() {
    return {
      token: this.dropZone.token,
      qid: this.selector.elementId
    };
  }

  toString() {
    return `${this.dropZone.token.toString()} <-> ${this.selector.elementId}`;
  }
}

class LinkGroup extends Component {
  constructor(env, dropzones) {
    super(createDiv());
    this.env = env;
    this.dropzones = dropzones;
    this.links = [];

    const linkedEntitiesDiv = createDiv();
    this.newLinkButton = createButton('New link', {type: 'button', class: 'progressive'});
    this.newLinkButton.addEventListener('click', () => this._createLink());

    this.node.addEventListener('linkremoved', event => deleteListener(event, this.links));
    this.node.append(linkedEntitiesDiv, this.newLinkButton);
  }

  _createLink() {
    const link = new Link(this.env, this.dropzones.concat(this.links.map(link => link.dropZone)));
    this.newLinkButton.before(link.node);
    this.links.push(link);
    return link;
  }

  getTokenFor(itemId) {
    for (const link of this.links) {
      if (link.selector.elementId === itemId)
        return link.dropZone.token;
    }
    return undefined;
  }

  /**
   *
   * @param {Token} token
   * @param itemId
   */
  linkToken(token, itemId) {
    const link = this._createLink();
    link.dropZone.add(token);
    link.selector.showValue(token.text, itemId);
  }

  aggregate() {
    return this.links.map(link => link.aggregate()).filter(link => link.token !== undefined && link.qid !== null);
  }
}

export default class Reconciler extends Component {
  constructor(env) {
    super(createDiv());

    /**
     *
     * @type {MultiDropZone}
     */
    this.newEntitiesDropZone = new MultiDropZone(env, {reconciliationType: Token.NEW});
    this.newEntitiesDropZone.node.append(createSpan('Drop here to create a new item'));

    this.linkGroup = new LinkGroup(env, [this.newEntitiesDropZone]);

    this.node.append(
      ...createCollapsible('New items', this.newEntitiesDropZone.node),
      ...createCollapsible('Linked items', this.linkGroup._node)
    );
  }

  linkToken(token, itemId) {
    this.linkGroup.linkToken(token, itemId);
  }

  getTokenFor(itemId) {
    return this.linkGroup.getTokenFor(itemId);
  }

  aggregate() {
    return {
      newItems: this.newEntitiesDropZone.aggregate(),
      linkedItems: this.linkGroup.aggregate()
    };
  }
}