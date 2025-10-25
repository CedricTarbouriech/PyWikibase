import {DragAndDropEnv} from './dragAndDrop.js';
import Annotator from './annotator.js';
import Reconciler from './reconcilier.js';
import SchemaEditor from './schemaEditor.js';
import {createCollapsible, createDiv} from "./nodeUtil.js";
import {postAsJson} from "/static/wikibase/js/api.js";

class Application {
  constructor(id) {
    this.node = document.getElementById(id);
    this.node.className = "columns";
    this.node.style.padding = "10px";

    const column1 = createDiv({class: 'column-1'});
    const column2 = createDiv({class: 'column-2'});
    this.node.append(column1, column2);

    /// Création de l’annotateur et ajout dans la première colonne
    this.annotator = new Annotator();
    column1.append(this.annotator.node);

    const dragAndDropEnv = new DragAndDropEnv();

    this.reconciler = new Reconciler(dragAndDropEnv);
    column2.append(...createCollapsible('Reconciler', this.reconciler.node));

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

    document.addEventListener('refreshtokens', event => {
      this.reconciler.refresh();
      this.schemaEditor.refresh();
    });
  }

  aggregate() {
    return {
      entities: this.annotator.aggregate(),
      reconciliations: this.reconciler.aggregate(),
      schemata: this.schemaEditor.aggregate()
    };
  }

  start() {
    this.annotator.updateTokensFromText();
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const app = new Application('app');
  const body = document.getElementsByTagName('body')[0];
  body.style.display = 'block';
  const submitButton = document.getElementById('submit');
  const testButton = document.createElement('button');
  testButton.type = 'button';
  testButton.textContent='Test';

  testButton.addEventListener('click', async _ => {
    const aggregations = app.aggregate();
    console.log(aggregations);
    console.log(await postAsJson('/api/annotator', 'Marche pas', {document: app.node.getAttribute('data-document-id'), ...aggregations}));
  });
  submitButton.before(testButton);
  app.start();
});