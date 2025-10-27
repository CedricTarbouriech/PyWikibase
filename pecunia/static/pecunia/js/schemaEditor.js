import {SingleDropZone} from "./dragAndDrop.js";
import {createButton, createDiv, createInput} from "./nodeUtil.js";
import {Selector} from "./selector.js";
import {getAsJson} from "./api.js";

class Term {
  constructor() {
    this._node = document.createElement('div');
    this.select = document.createElement('select');

    const option1 = document.createElement('option');
    const option2 = document.createElement('option');
    const option3 = document.createElement('option');
    option1.textContent = "label";
    option2.textContent = "description";
    option3.textContent = "alias";
    this.select.append(option1, option2, option3);

    this.langInput = document.createElement('input');
    this.langInput.classList.add('lang-code-input');
    this.textInput = document.createElement('input');

    const deleteButton = createButton('X', {
      type: 'button',
      style: 'margin-right: 10px'
    })

    deleteButton.addEventListener('click', _ => {
      this._node.dispatchEvent(new CustomEvent('termremoved', {
        bubbles: true,
        detail: {term: this}
      }));
      this._node.remove();
    });

    this._node.append(deleteButton, this.select, this.langInput, this.textInput);
  }

  get node() {
    return this._node;
  }

  aggregate() {
    return {
      type: this.select.value, langCode: this.langInput.value, value: this.textInput.value
    };
  }
}

class TermEditor {
  constructor() {
    this._node = document.createElement('div');
    this.terms = [];

    const newTermButton = document.createElement('button');
    newTermButton.setAttribute('type', 'button');
    newTermButton.textContent = "Add new term";
    this._node.append(newTermButton);

    newTermButton.addEventListener('click', event => {
      const term = new Term();
      this.terms.push(term);
      newTermButton.before(term.node);
    });

    this._node.addEventListener('termremoved', event => {
      const term = event.detail.term;
      const index = this.terms.indexOf(term);
      if (index > -1)
        this.terms.splice(index, 1);
    });
  }

  aggregate() {
    return this.terms.map(term => term.aggregate());
  }

  get node() {
    return this._node;
  }
}

class Snak {
  constructor(env) {
    this._node = createDiv({
      class: 'snak-cell'
    });
  }

  get node() {
    return this._node;
  }
}

class ItemSnak extends Snak {
  constructor(env) {
    super(env);
    this.dropZone = new SingleDropZone(env);
    this._node.append(this.dropZone.node);
  }

  aggregate() {
    return {
      type: 'Item',
      value: {item: this.dropZone.token}
    };
  }
}

class PropertySnak extends Snak {
  constructor(env) {
    super(env);

  }
}

class StringValueSnak extends Snak {
  constructor(env) {
    super(env);
    this.input = createInput({type: 'text'});
    this._node.append(this.input);
  }

  aggregate() {
    return {
      type: 'StringValue',
      value: {value: this.input.value}
    };
  }
}

class UrlValueSnak extends Snak {
  constructor(env) {
    super(env);
    this.input = createInput({type: 'text'});
    this._node.append(this.input);
  }

  aggregate() {
    return {
      type: 'UrlValue',
      value: {value: this.input.value}
    };
  }
}

class QuantityValueSnak extends Snak {
  constructor(env) {
    super(env);
    this.input = createInput({type: 'text'});
    this._node.append(this.input);
  }

  aggregate() {
    return {
      type: 'QuantityValue',
      value: {number: this.input.value}
    };
  }
}

class TimeValueSnak extends Snak {
  constructor(env) {
    super(env);
  }
}

class GlobeCoordinateValueSnak extends Snak {
  constructor(env) {
    super(env);
    this.latitudeInput = createInput({type: 'text'});
    this.longitudeInput = createInput({type: 'text'});
    this._node.append(this.latitudeInput, this.longitudeInput);
  }

  aggregate() {
    return {
      type: 'GlobeCoordinatesValue',
      value: {
        latitude: this.latitudeInput.value,
        longitude: this.longitudeInput.value
      }
    };
  }
}

class MonolingualTextValueSnak extends Snak {
  constructor(env) {
    super(env);
    this.languageInput = createInput({type: 'text', placeholder: 'Language code'});
    this.textInput = createInput({type: 'text', placeholder: 'Text'});
    this._node.append(this.languageInput, this.textInput);
  }

  aggregate() {
    return {
      type: 'MonolingualTextValue',
      value: {
        language: this.languageInput.value,
        value: this.textInput.value
      }
    };
  }
}

function createSnakFromDatatype(datatype, env) {
  switch (datatype) {
    case 'Item':
      return new ItemSnak(env);
    case 'Property':
      return new PropertySnak(env);
    case 'StringValue':
      return new StringValueSnak(env);
    case 'UrlValue':
      return new UrlValueSnak(env);
    case 'QuantityValue':
      return new QuantityValueSnak(env);
    case 'TimeValue':
      return new TimeValueSnak(env);
    case 'GlobeCoordinateValue':
      return new GlobeCoordinateValueSnak(env);
    case 'MonolingualTextValue':
      return new MonolingualTextValueSnak(env);
    default:
      throw new Error(`Unknown datatype for the statement creation: ${datatype}.`)
  }
}

class Reference {
  constructor(env) {
    this._node = createDiv({
      class: 'reference-cell'
    });

    const propertyDiv = createDiv({
      class: 'property-cell'
    });
    this.propertySelector = new Selector('properties');
    propertyDiv.append(this.propertySelector.node);
    this._node.append(propertyDiv);

    this._node.addEventListener('propertyselected', async event => {
      event.stopPropagation();
      const data = await getAsJson(`/api/properties/${this.propertySelector.elementId}`, `Erreur de chargement des informations sur la propriété ${this.propertySelector.elementId}.`);
      this.snak = createSnakFromDatatype(data.type, env);
      this._node.append(this.snak.node);
    });
  }

  get node() {
    return this._node;
  }

  aggregate() {
    return {
      property: this.propertySelector.elementId, snak: this.snak.aggregate()
    };
  }
}

class ReferenceRecord {
  constructor(env) {
    this._node = createDiv({
      class: 'reference-record-cell'
    });

    const addReferenceButton = createButton('add', {
      type: 'button', class: 'add-reference-button'
    })
    this._node.append(addReferenceButton);

    this.references = [];
    addReferenceButton.addEventListener('click', _ => {
      const reference = new Reference(env);
      this.references.push(reference);
      addReferenceButton.before(reference.node);
    });
  }

  get node() {
    return this._node;
  }

  aggregate() {
    return this.references.map(reference => reference.aggregate());
  }
}

class Qualifier {
  constructor(env) {
    this._node = createDiv({
      class: 'qualifier-cell'
    });

    const propertyDiv = createDiv({
      class: 'property-cell'
    });
    this.propertySelector = new Selector('properties');
    propertyDiv.append(this.propertySelector.node);
    this._node.append(propertyDiv);

    this._node.addEventListener('propertyselected', async event => {
      event.stopPropagation();
      const data = await getAsJson(`/api/properties/${this.propertySelector.elementId}`, `Erreur de chargement des informations sur la propriété ${this.propertySelector.elementId}.`);
      this.snak = createSnakFromDatatype(data.type, env);
      this._node.append(this.snak.node);
    });
  }

  get node() {
    return this._node;
  }

  aggregate() {
    return {
      property: this.propertySelector.elementId, snak: this.snak.aggregate()
    };
  }
}

class Statement {
  constructor(env, datatype) {
    this._node = createDiv({
      class: ''
    });

    this.mainSnak = createSnakFromDatatype(datatype, env);

    const valueDiv = createDiv({
      class: ''
    });
    valueDiv.append(this.mainSnak.node);
    this._node.append(valueDiv);

    // FIXME
    // const deleteDiv = createDiv({
    //   class: 'delete-div'
    // });
    // const deleteButton = createButton('delete', {type: 'button', class: 'btn-delete-statement'});
    // deleteDiv.append(deleteButton);
    // this._node.append(deleteDiv);


    this.qualifiers = [];
    const qualifierDiv = createDiv({
      class: 'qualifiers-div'
    })
    const addQualifierButton = createButton('add qualifier', {type: 'button', class: 'btn-add-qualifier'});
    addQualifierButton.addEventListener('click', _ => {
      const qualifier = new Qualifier(env);
      this.qualifiers.push(qualifier);
      addQualifierButton.before(qualifier.node);
    });

    qualifierDiv.append(addQualifierButton);
    this._node.append(qualifierDiv);

    this.referenceRecords = [];
    const referenceRecordDiv = createDiv({
      class: 'reference-records-div'
    });

    const addReferenceRecordButton = createButton('add reference', {type: 'button', class: 'btn-add-reference-record'});
    addReferenceRecordButton.addEventListener('click', _ => {
      const referenceRecord = new ReferenceRecord(env);
      this.referenceRecords.push(referenceRecord);
      addReferenceRecordButton.before(referenceRecord.node);
    });
    referenceRecordDiv.append(addReferenceRecordButton);
    this._node.append(referenceRecordDiv);
  }

  aggregate() {
    return {
      mainSnak: this.mainSnak.aggregate(),
      qualifiers: this.qualifiers.map(qualifier => qualifier.aggregate()),
      referenceRecords: this.referenceRecords.map(record => record.aggregate())
    };
  }

  get node() {
    return this._node;
  }
}

class StatementGroup {
  constructor(env) {
    this._node = createDiv({
      class: '',
      style: 'border: 2px solid'
    });

    const propertyDiv = createDiv({
      class: ''
    });
    this.statements = [];
    this.propertySelector = new Selector('properties');
    propertyDiv.append(this.propertySelector.node);
    this._node.append(propertyDiv);

    const newValueDiv = createDiv({class: 'new-value-cell'});
    const newValueButton = createButton('New value', {type: 'button', class: 'btn-add-value'});
    newValueDiv.append(newValueButton);
    newValueDiv.style.display = 'none';
    this._node.append(newValueDiv);

    const createStatement = (datatype, env) => {
      const statement = new Statement(env, datatype);
      this.statements.push(statement);
      newValueDiv.before(statement.node);
    };

    newValueButton.addEventListener('click', _ => {
      createStatement(this.datatype, env);
    });

    // Ajouter un listener : lorsqu’on sélectionne une propriété, ajouter un statement.
    this._node.addEventListener('propertyselected', async _ => {
      this.statements.forEach(statement => statement.node.remove());
      this.statements = [];
      const data = await getAsJson(`/api/properties/${this.propertySelector.elementId}`, `Erreur de chargement des informations sur la propriété ${this.propertySelector.elementId}.`);
      this.datatype = data.type;
      // TODO Refresh au changement de propriété
      createStatement(this.datatype, env);
      newValueDiv.style.display = 'block';
    });
  }

  aggregate() {
    return {
      property: this.propertySelector.elementId,
      statements: this.statements.map(statement => statement.aggregate())
    };
  }

  get node() {
    return this._node;
  }
}

class StatementEditor {
  constructor(env) {
    this._node = document.createElement('div');
    this.statementGroups = [];

    const newStatementButton = createButton('Add new statement', {
      type: 'button'
    });

    newStatementButton.addEventListener('click', _ => {
      const statementGroup = new StatementGroup(env);
      this.statementGroups.push(statementGroup);
      newStatementButton.before(statementGroup.node);
    });

    this._node.addEventListener('statementgroupremoved', event => {
      const statementGroup = event.detail.statementGroup;
      const index = this.statementGroups.indexOf(statementGroup);
      if (index > -1)
        this.statementGroups.splice(index, 1);
    });
    this._node.append(newStatementButton);
  }

  get node() {
    return this._node;
  }

  aggregate() {
    return this.statementGroups.map(group => group.aggregate());
  }

  refresh() {
    // TODO Implement
  }
}

class Item {
  constructor(env) {
    this._node = document.createElement('div');
    this.dropZone = new SingleDropZone(env);
    this.termEditor = new TermEditor();
    this.statementEditor = new StatementEditor(env);
    const deleteButton = createButton('X', {
      type: 'button',
      style: 'margin-right: 10px;'
    });

    deleteButton.addEventListener('click', _ => {
      this._node.dispatchEvent(new CustomEvent('itemremoved', {
        bubbles: true,
        detail: {item: this}
      }));
      this._node.remove();
    });

    this._node.append(deleteButton, this.dropZone.node, this.termEditor.node, this.statementEditor.node);
  }

  get token() {
    return this.dropZone.token;
  }

  get node() {
    return this._node;
  }

  refresh() {
    this.dropZone.refresh();
    this.statementEditor.refresh();
  }

  aggregate() {
    return {
      token: this.dropZone.token,
      terms: this.termEditor.aggregate(),
      statements: this.statementEditor.aggregate()
    };
  }
}

export default class SchemaEditor {
  constructor(env) {
    this._node = document.createElement('div');
    this.items = [];

    const newItemButton = createButton('New item', {
      type: 'button'
    });
    newItemButton.addEventListener('click', _ => {
      const item = new Item(env);
      this.items.push(item);
      newItemButton.before(item.node);
    });

    this._node.addEventListener('itemremoved', event => {
      const item = event.detail.item;
      const index = this.items.indexOf(item);
      if (index > -1)
        this.items.splice(index, 1);
    });

    this._node.append(newItemButton);
  }

  get node() {
    return this._node;
  }

  refresh() {
    for (const item of this.items) {
      item.refresh();
    }
  }

  aggregate() {
    return this.items.filter(item => item.token !== undefined).map(item => item.aggregate());
  }
}