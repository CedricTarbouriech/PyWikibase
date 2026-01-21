import {DragAndDropEnv} from './dragAndDrop.js';
import TextEditor from './textEditor.js';
import Reconciler from './reconciler.js';
import SchemaEditor from './schemaEditor.js';
import {Component, createCollapsible, createDiv} from "../nodeUtil.js";
import {postAsJson} from "../api.js";

class Application extends Component {
  constructor(id) {
    super(document.getElementById(id));

    this._node.className = "split";
    this._node.addEventListener('dragstart', () => {
      this._node.classList.add('dragging');
    })
    this._node.addEventListener('dragend', () => {
      this._node.classList.remove('dragging');
    })

    const column1 = createDiv({id: 'split-0'});
    const column2 = createDiv({id: 'split-1'});
    this._node.append(column1, column2);

    Split(['#split-0', '#split-1']);

    /// Création de l’annotateur et ajout dans la première colonne
    const dragAndDropEnv = new DragAndDropEnv();

    this.annotator = new TextEditor(dragAndDropEnv);
    column1.append(this.annotator.node);

    this.reconciler = new Reconciler(dragAndDropEnv);
    column2.append(...createCollapsible('Reconciler', this.reconciler.node));

    column2.append(document.createElement('hr'));

    this.schemaEditor = new SchemaEditor(dragAndDropEnv);
    column2.append(...createCollapsible('Schema editor', this.schemaEditor.node));

    document.addEventListener('dragstart', event => {
      if (event.target.nodeName === 'SPAN' && event.target.closest('.entity-token')) {
        const span = event.target;
        const tokenId = span.getAttribute('data-token-id');
        dragAndDropEnv.draggedToken = this.annotator.getToken(tokenId);
      }
    });

    document.addEventListener('dragover', event => {
      event.preventDefault();
    });

    document.addEventListener('newlinkeduntagged', event => {
      const itemId = event.detail.id;
      const itemLabel = event.detail.label;
      let token = this.reconciler.getTokenFor(itemId);
      if (!token) {
        token = this.annotator.addUntaggedToken(itemLabel);
        this.reconciler.linkToken(token, itemId);
      }
      event.detail.dropzone.add(token);
    });
  }

  aggregate() {
    return {
      entities: this.annotator.aggregate(),
      reconciliations: this.reconciler.aggregate(),
      schemas: this.schemaEditor.aggregate() // FIXME Vérifier que tous les tokens utilisés sont réconciliés
    };
  }

  start() {
    this.annotator.updateTokensFromText();
  }
}

function generateList(label, iterable) {
  const list = document.createElement('ul');
  const listLabel = document.createElement('li');
  listLabel.textContent = label;

  for (const item of iterable) {
    const listElement = document.createElement('li');
    listElement.append(JSON.stringify(item));
    list.append(listElement);
  }
  return [listLabel, list];
}

document.addEventListener('DOMContentLoaded', () => {
  const app = new Application('app');
  const body = document.getElementsByTagName('body')[0];
  body.style.display = 'block';
  const submitButton = document.getElementById('submit');
  // submitButton.setAttribute('disabled', 'true');

  const testButton = document.createElement('button');
  testButton.type = 'button';
  testButton.className = 'progressive';
  testButton.textContent = 'Check';

  const sendButton = document.createElement('button');
  sendButton.type = 'button';
  sendButton.className = 'progressive';
  sendButton.textContent = 'Send';

  sendButton.addEventListener('click', async _ => {
    const aggregations = app.aggregate();
    console.log(aggregations);
    console.log(await postAsJson('/api/annotator', 'Marche pas', {document: app.node.getAttribute('data-document-id'), ...aggregations}));
  });

  const checkDiv = document.createElement('ul');

  app.node.after(document.createElement('hr'), checkDiv);

  testButton.addEventListener('click', async _ => {
    checkDiv.innerHTML = "";
    const aggregations = app.aggregate();
    console.log(aggregations);

    const entities = document.createElement('ul');
    const entitiesLabel = document.createElement('li');
    entitiesLabel.textContent = 'Entities';
    entities.append(
      ...generateList('Tagged entities', Object.values(aggregations.entities.taggedEntities)),
      ...generateList('Untagged entities', Object.values(aggregations.entities.untaggedEntities))
    );

    const reconciliations = document.createElement('ul');
    const reconciliationsLabel = document.createElement('li');
    reconciliationsLabel.textContent = 'Reconciliations';
    reconciliations.append(
      ...generateList('New items', Object.values(aggregations.reconciliations.newItems)),
      ...generateList('Linked items', Object.values(aggregations.reconciliations.linkedItems))
    );

    const schemas = document.createElement('ul');
    const schemasLabel = document.createElement('li');
    schemasLabel.textContent = 'Schemas';
    for (const schema of aggregations.schemas) {
      const item = document.createElement('li');
      item.textContent = schema.token.toString();
      const ul = document.createElement('ul');
      schemas.append(item, ul);
      ul.append(
        ...generateList('Terms', Object.values(schema.terms)),
        ...generateList('Statements', Object.values(schema.statements))
      );
    }

    checkDiv.append(entitiesLabel, entities, reconciliationsLabel, reconciliations, schemasLabel, schemas);
  });
  submitButton.addEventListener('click', event => {
    if (!window.confirm('Do you want to save? If you haven’t send data, it will be lost.')) event.preventDefault();
  });
  submitButton.before(testButton, sendButton);
  app.start();
});
