import {SingleDropZone, Token} from "./dragAndDrop.js";
import {
  CollapsibleGroupItemComponent,
  Component,
  createButton,
  createCollapsible,
  createDiv,
  createInput,
  createLabel,
  createSelect,
  GroupComponent,
  GroupItemComponent
} from "../nodeUtil.js";
import {Selector} from "../widgets/selector.js";
import {getAsJson} from "../api.js";

class Term extends GroupItemComponent {
  constructor() {
    super(createDiv(), 'term');
    this.select = createSelect(["label", "description", "alias"]);

    this.langInput = createInput({class: 'lang-code-input', type: 'text'});
    this.langInput.value = 'en';
    this.textInput = createInput({type: 'text'});

    this.node.append(this.select, this.langInput, this.textInput);
  }

  aggregate() {
    return {
      type: this.select.value,
      langCode: this.langInput.value,
      value: this.textInput.value
    };
  }

  toString() {
    return `${this.select.value}: (${this.langInput.value}) ${this.textInput.value}`;
  }
}

class TermEditor extends GroupComponent {
  constructor() {
    super(
      undefined,
      createDiv({class: 'bordered-content'}),
      'Add new term',
      Term,
      'term'
    );
  }
}

class Snak extends Component {
  /**
   *
   * @param {DragAndDropEnv} env
   */
  constructor(env) {
    super(createDiv({class: 'snak-div'}));
    this.snakTypeRadio = createDiv();
    const id = env.radioId;
    env.radioId++;
    const valueInput = createInput({
      'id': `snaktype-${id}-1`,
      'type': 'radio',
      'name': `snaktype-${id}`,
      'value': 'value',
      'checked': true,
    });
    const valueLabel = createLabel('Value', {'for': `snaktype-${id}-1`})
    const someValueInput = createInput({
      'id': `snaktype-${id}-2`,
      'type': 'radio',
      'name': `snaktype-${id}`,
      'value': 'somevalue'
    });
    const unknownLabel = createLabel('Unknown value', {'for': `snaktype-${id}-2`})
    const noValueInput = createInput({
      'id': `snaktype-${id}-3`,
      'type': 'radio',
      'name': `snaktype-${id}`,
      'value': 'novalue'
    });
    const noLabel = createLabel('No value', {'for': `snaktype-${id}-3`});
    this.snakTypeRadio.append(valueInput, valueLabel, someValueInput, unknownLabel, noValueInput, noLabel);
    this.node.prepend(this.snakTypeRadio);

    valueInput.addEventListener('click', () => this.enableInput());
    someValueInput.addEventListener('click', () => this.disableInput());
    noValueInput.addEventListener('click', () => this.disableInput());
  }

  get snakType() {
    return this.snakTypeRadio.querySelector('input:checked').value;
  }

  enableInput() {

  }

  disableInput() {
  }

  aggregate() {

  }
}

class ItemSnak extends Snak {
  constructor(env) {
    super(env);
    this.dropZone = new SingleDropZone(env, {});
    this.selector = new Selector('items');
    this.node.append(this.dropZone.node, this.selector.node);
    this.node.addEventListener('selectionchanged-items', event => {
      event.stopPropagation();
      this.node.dispatchEvent(new CustomEvent('newlinkeduntagged', {
        bubbles: true,
        detail: {
          id: this.selector.elementId,
          label: this.selector.state.items[this.selector.elementId]['labels']['en'], // FIXME not clean
          dropzone: this.dropZone
        }
      }));
    });
  }

  enableInput() {
    this.dropZone.enable();
    this.selector.enable();
  }

  disableInput() {
    this.dropZone.disable();
    this.selector.disable();
  }

  aggregate() {
    return {
      type: 'Item',
      value: this.snakType === 'value' ? {item: this.dropZone.token} : undefined,
      snakType: this.snakType,
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
    this.node.append(this.input);
  }

  enableInput() {
    this.input.disabled = false;
  }

  disableInput() {
    this.input.disabled = true;
  }

  aggregate() {
    return {
      type: 'StringValue',
      value: this.snakType === 'value' ? {value: this.input.value} : undefined,
      snakType: this.snakType,
    };
  }
}

class UrlValueSnak extends Snak {
  constructor(env) {
    super(env);
    this.input = createInput({type: 'text'});
    this.node.append(this.input);
  }

  enableInput() {
    this.input.disabled = false;
  }

  disableInput() {
    this.input.disabled = true;
  }

  aggregate() {
    return {
      type: 'UrlValue',
      value: this.snakType === 'value' ? {value: this.input.value} : undefined,
      snakType: this.snakType,
    };
  }
}

class QuantityValueSnak extends Snak {
  constructor(env) {
    super(env);
    this.input = createInput({type: 'text'});
    this.node.append(this.input);
  }

  enableInput() {
    this.input.disabled = false;
  }

  disableInput() {
    this.input.disabled = true;
  }

  aggregate() {
    return {
      type: 'QuantityValue',
      value: this.snakType === 'value' ? {number: this.input.value} : undefined,
      snakType: this.snakType,
    };
  }
}

class TimeValueSnak extends Snak {
  constructor(env) {
    super(env);
    this.time = createInput({
      type: 'text',
      pattern: '^(?:(?:(\\d\\d?)\\/)?(0?[1-9]|1[012])\\/)?(\\d+)(?: (B?CE))?$'
    });
    this.node.append(this.time);
  }

  enableInput() {
    this.time.disabled = false;
  }

  disableInput() {
    this.time.disabled = true;
  }

  aggregate() {
    const time = this.time.value;
    const groups = time.match(/^(?:(?:(\d\d?)\/)?(0?[1-9]|1[012])\/)?(\d+)(?: (B?CE))?$/);
    const year = groups[3];
    const month = groups[2] ?? "01";
    const day = groups[1] ?? "01";
    const sign = groups[4] === "BCE" ? "-" : "+";
    let precision = 11;
    if (groups[1] !== undefined)
      precision = 9;
    else if (groups[2] !== undefined)
      precision = 10;

    return {
      type: 'TimeValue',
      value: this.snakType === 'value' ? {
        time: `${sign}${year}-${month}-${day}`,
        precision: precision
      } : undefined,
      snakType: this.snakType,
    };
  }
}

class GlobeCoordinateValueSnak extends Snak {
  constructor(env) {
    super(env);
    this.latitudeInput = createInput({type: 'text'});
    this.longitudeInput = createInput({type: 'text'});
    this.node.append(this.latitudeInput, this.longitudeInput);
  }

  enableInput() {
    this.latitudeInput.disabled = false;
    this.longitudeInput.disabled = false;
  }

  disableInput() {
    this.latitudeInput.disabled = true;
    this.longitudeInput.disabled = true;
  }

  aggregate() {
    return {
      type: 'GlobeCoordinatesValue',
      value: {
        latitude: this.latitudeInput.value,
        longitude: this.longitudeInput.value
      } ? this.snakType === 'value' : undefined,
      snakType: this.snakType,
    };
  }
}

class MonolingualTextValueSnak extends Snak {
  constructor(env) {
    super(env);
    this.languageInput = createInput({type: 'text', placeholder: 'Language code'});
    this.textInput = createInput({type: 'text', placeholder: 'Text'});
    this.node.append(this.languageInput, this.textInput);
  }

  enableInput() {
    this.languageInput.disabled = false;
    this.textInput.disabled = false;
  }

  disableInput() {
    this.languageInput.disabled = true;
    this.textInput.disabled = true;
  }

  aggregate() {
    return {
      type: 'MonolingualTextValue',
      value: {
        language: this.languageInput.value,
        value: this.textInput.value
      } ? this.snakType === 'value' : undefined,
      snakType: this.snakType,
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

class Reference extends GroupItemComponent {
  constructor(env) {
    super(createDiv({class: 'reference-cell'}), 'reference');

    const propertyDiv = createDiv({class: 'property-cell'});
    this.propertySelector = new Selector('properties');
    propertyDiv.append(this.propertySelector.node);
    this.node.append(propertyDiv);

    this.node.addEventListener('selectionchanged-properties', async event => {
      event.stopPropagation();
      const data = await getAsJson(`/api/properties/${this.propertySelector.elementId}`, `Erreur de chargement des informations sur la propriété ${this.propertySelector.elementId}.`);
      if (this.snak)
        this.snak.node.remove();
      this.snak = createSnakFromDatatype(data.type, env);
      this.node.append(this.snak.node);
    });
  }

  aggregate() {
    return {
      property: this.propertySelector.elementId, snak: this.snak.aggregate()
    };
  }
}

class ReferenceRecord extends GroupComponent {
  constructor(env) {
    super(
      env,
      createDiv({class: 'reference-record-cell'}),
      'add',
      Reference,
      'reference' // FIXME Filtrer les références qui n’ont pas de propriété sélectionné
    );
  }
}

class Qualifier extends Component {
  constructor(env) {
    super(createDiv({class: 'qualifier-cell'}));

    const propertyDiv = createDiv({
      class: 'property-cell'
    });
    this.propertySelector = new Selector('properties');
    propertyDiv.append(this.propertySelector.node);
    this.node.append(propertyDiv);

    this.node.addEventListener('selectionchanged-properties', async event => {
      event.stopPropagation();
      const data = await getAsJson(`/api/properties/${this.propertySelector.elementId}`, `Erreur de chargement des informations sur la propriété ${this.propertySelector.elementId}.`);
      if (this.snak)
        this.snak.node.remove();
      this.snak = createSnakFromDatatype(data.type, env);
      this.node.append(this.snak.node);
    });
  }

  aggregate() {
    return {
      property: this.propertySelector.elementId, snak: this.snak.aggregate()
    };
  }
}

class Statement extends Component {
  constructor(env, datatype) {
    super(createDiv({class: 'bordered-content'}));

    this.mainSnak = createSnakFromDatatype(datatype, env);

    const valueDiv = createDiv({class: ''});
    valueDiv.append(this.mainSnak.node);
    this.node.append(valueDiv);

    // FIXME
    // const deleteDiv = createDiv({
    //   class: 'delete-div'
    // });
    // const deleteButton = createButton('delete', {type: 'button', class: 'btn-delete-statement'});
    // deleteDiv.append(deleteButton);
    // this._node.append(deleteDiv);

    // FIXME Hériter deux fois de EditorComponent ???
    this.qualifiers = [];
    const qualifierDiv = createDiv({
      class: 'qualifiers-div'
    })
    const addQualifierButton = createButton('add qualifier', {
      type: 'button',
      class: 'btn-add-qualifier progressive'
    });
    addQualifierButton.addEventListener('click', _ => {
      const qualifier = new Qualifier(env);
      this.qualifiers.push(qualifier);
      addQualifierButton.before(qualifier.node);
    });

    qualifierDiv.append(addQualifierButton);
    this.node.append(...createCollapsible('Qualifiers', qualifierDiv));

    this.referenceRecords = [];
    const referenceRecordDiv = createDiv({
      class: 'reference-records-div'
    });

    const addReferenceRecordButton = createButton('add reference', {
      type: 'button',
      class: 'btn-add-reference-record progressive'
    });
    addReferenceRecordButton.addEventListener('click', _ => {
      const referenceRecord = new ReferenceRecord(env);
      this.referenceRecords.push(referenceRecord);
      addReferenceRecordButton.before(referenceRecord.node);
    });
    referenceRecordDiv.append(addReferenceRecordButton);
    this.node.append(referenceRecordDiv);
  }

  aggregate() {
    return {
      mainSnak: this.mainSnak.aggregate(),
      qualifiers: this.qualifiers.filter(qualifier => qualifier.propertySelector.elementId !== null).map(qualifier => qualifier.aggregate()),
      referenceRecords: this.referenceRecords.map(record => record.aggregate()) // FIXME Filtrer si pas de références valides dans le record
    };
  }

  toString() {
    return JSON.stringify(this.aggregate());
  }
}

class StatementGroup extends CollapsibleGroupItemComponent {
  constructor(env) {
    const div = createDiv();
    super(createDiv({class: 'bordered-content'}), 'statementgroup', div);

    this.statements = [];
    this.propertySelector = new Selector('properties');
    div.append(this.propertySelector.node);

    const newValueButton = createButton('New value', {
      type: 'button',
      class: 'btn-add-value progressive'
    });

    const createStatement = (datatype, env) => {
      const statement = new Statement(env, datatype);
      this.statements.push(statement);
      newValueDiv.before(statement.node);
    };

    newValueButton.addEventListener('click', () => createStatement(this.datatype, env));
    const newValueDiv = createDiv({class: 'bordered-content'});
    newValueDiv.append(newValueButton);
    newValueDiv.style.display = 'none';

    div.append(newValueDiv);

    // Ajouter un listener : lorsqu’on sélectionne une propriété, ajouter un statement.
    this.node.addEventListener('selectionchanged-properties', async event => {
      this.statements.forEach(statement => statement.node.remove());
      this.statements = [];
      const data = await getAsJson(`/api/properties/${this.propertySelector.elementId}`, `Erreur de chargement des informations sur la propriété ${this.propertySelector.elementId}.`);
      this.datatype = data.type;
      // TODO Refresh au changement de propriété
      createStatement(this.datatype, env);
      newValueDiv.style.display = 'block';
      this.collapseButton.firstChild.textContent = event.detail.label;
    });
  }

  aggregate() {
    return {
      property: this.propertySelector.elementId,
      statements: this.statements.map(statement => statement.aggregate())
    };
  }
}

class StatementEditor extends GroupComponent {
  constructor(env) {
    super(
      env,
      createDiv({class: 'bordered-content'}),
      'Add new statement',
      StatementGroup,
      'statementgroup',
      statementGroup => statementGroup.propertySelector.elementId !== null
    );
  }
}

class Schema extends CollapsibleGroupItemComponent {
  constructor(env) {
    const content = createDiv({class: 'bordered-content'});
    super(createDiv(), 'schema', content);
    /**
     *
     * @type {SingleDropZone}
     */
    this.dropZone = new SingleDropZone(env, {
      condition: token => token.reconciliationType === Token.UNKNOWN,
      msg: 'This token cannot be used here as it will reconcile with the UNKNOWN value.'
    });
    this.dropZone.schemaDropZone = true;
    this.dropZone.node.classList.add('schema-drop-zone');
    this.termEditor = new TermEditor();
    this.statementEditor = new StatementEditor(env);

    content.append(
      this.dropZone.node,
      ...createCollapsible('Terms', this.termEditor.node),
      ...createCollapsible('Statements', this.statementEditor.node)
    );
    this.node.addEventListener('addedtoken', event => {
      if (event.detail.dropZone !== this.dropZone) return;
      this.collapseButton.firstChild.textContent = event.detail.token.text;
    })
  }

  get token() {
    return this.dropZone.token;
  }

  aggregate() {
    return {
      token: this.dropZone.token,
      terms: this.termEditor.aggregate(),
      statements: this.statementEditor.aggregate()
    };
  }
}

export default class SchemaEditor extends GroupComponent {
  constructor(env) {
    super(
      env,
      createDiv(),
      'New schema',
      Schema,
      'schema',
      schema => schema.token !== undefined
    );
  }
}