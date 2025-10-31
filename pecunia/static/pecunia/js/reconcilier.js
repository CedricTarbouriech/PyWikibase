import {MultiDropZone, SingleDropZone} from "./dragAndDrop.js";
import {Selector} from "./selector.js";
import {createButton, createCollapsible, createDiv} from "./nodeUtil.js";

/**
 * Represents a link between a token and an entity.
 */
class Link {
  constructor(env, dropZones) {
    this._node = document.createElement('div');
    this._node.classList.add('linked-entity');
    this.dropZone = new SingleDropZone(env);
    this.selector = new Selector('items');
    const deleteButton = createButton('X', {
      type: 'button',
      style: 'margin-right: 10px'
    });
    deleteButton.addEventListener('click', _ => {
      const confirmed = window.confirm("Are you sure?");
      if (!confirmed) return;

      this._node.dispatchEvent(new CustomEvent('linkremoved', {
        bubbles: true,
        detail: {link: this}
      }));
      this._node.remove();
    });

    this._node.append(deleteButton, this.dropZone.node, ' — ', this.selector.node);

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

  get node() {
    return this._node;
  }

  refresh() {
    this.dropZone.refresh();
  }
}

class LinkGroup {
  constructor(env, dropzones) {
    this._node = createDiv();
    this.links = [];

    const linkedEntitiesDiv = createDiv();
    const newLinkButton = createButton('New link', {type: 'button'});
    newLinkButton.addEventListener('click', _ => {
      const link = new Link(env, dropzones.concat(this.links.map(link => link.dropZone)));
      newLinkButton.before(link.node);
      this.links.push(link);
    });

    this._node.addEventListener('linkremoved', event => {
      const link = event.detail.link;
      const index = this.links.indexOf(link);
      if (index > -1)
        this.links.splice(index, 1);
    });

    this._node.append(linkedEntitiesDiv, newLinkButton);
  }

  aggregate() {
    return this.links.map(link => link.aggregate()).filter(link => link.token !== undefined && link.qid !== null);
  }

  get node() {
    return this._node;
  }

  refresh() {
    for (const link of this.links) {
      link.refresh();
    }
  }
}

export default class Reconcilier {
  constructor(env) {
    this._node = document.createElement('div');

    this.newEntitiesDropZone = new MultiDropZone(env);
    this.unknownEntitiesDropZone = new MultiDropZone(env);
    this.linkGroup = new LinkGroup(env, [this.newEntitiesDropZone, this.unknownEntitiesDropZone]);

    this._node.append(
      ...createCollapsible('New entities', this.newEntitiesDropZone.node),
      ...createCollapsible('Unknown entities', this.unknownEntitiesDropZone.node),
      ...createCollapsible('Linked entities', this.linkGroup._node)
    );

    this.newEntitiesDropZone.addDisjointDropZone(this.unknownEntitiesDropZone);
    this.unknownEntitiesDropZone.addDisjointDropZone(this.newEntitiesDropZone);
  }

  get node() {
    return this._node;
  }

  refresh() {
    this.newEntitiesDropZone.refresh();
    this.unknownEntitiesDropZone.refresh();
    this.linkGroup.refresh();
  }

  aggregate() {
    return {
      newEntities: this.newEntitiesDropZone.aggregate(),
      unknownEntities: this.unknownEntitiesDropZone.aggregate(),
      linkedEntities: this.linkGroup.aggregate()
    };
  }
}