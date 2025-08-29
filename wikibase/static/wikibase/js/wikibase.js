'use strict';

import {
  createQualifier,
  createStatement,
  fetchPropertyDataType,
  getAsJson,
  postAsJson,
  updateStatement
} from './api.js';
import {
  createPropertySelector,
  createSnakInput,
  createSubmitCancelButtons,
  generateElement,
  getValueFromInputTd,
  updateDivWithNewStatement
} from './util.js';


/**
 *
 * @param event
 */
async function addNewStatement(event) {
  event.preventDefault();

  const langCode = document.querySelector('body').dataset.lang;

  // Choose property
  const propertySelector = await createPropertySelector(langCode);

  const propertyDiv = generateElement('<div class="property-cell">');
  propertyDiv.append(propertySelector);
  const valueDiv = generateElement('<div class="value-cell">');
  const actionsDiv = generateElement('<div class="actions-cell">');
  const snakDiv = generateElement('<div class="snak-cell">');
  snakDiv.append(valueDiv, actionsDiv);
  const statementsDiv = generateElement('<div class="statement-group">');
  statementsDiv.append(propertyDiv, snakDiv);

  event.target.before(statementsDiv);

  propertySelector.addEventListener('change', async () => {
    const datatype = propertySelector.querySelector('option:checked').dataset.type;
    const {rankSelector, snakTypeSelector, snakInput} = await createSnakInput(langCode, datatype);
    valueDiv.replaceChildren();
    valueDiv.append(rankSelector, snakTypeSelector, snakInput);
  });

  const getSubmitHandler = async event => {
    event.preventDefault();

    const selectedOption = propertySelector.querySelector('option:checked');
    const datatype = selectedOption.dataset.type;
    const propertyId = selectedOption.value;
    const data = await createStatement(valueDiv.querySelector('.snak-type-selector').value,
      valueDiv.querySelector('.rank-selector').value, propertyId, document.querySelector('h1').dataset.itemId,
      getValueFromInputTd(datatype, valueDiv));
    statementsDiv.outerHTML = data.updatedHtml;
  };

  const getCancelHandler = event => {
    event.preventDefault();
    statementsDiv.remove();
  };

  createSubmitCancelButtons(actionsDiv, getSubmitHandler, getCancelHandler);
}

async function addnewSnak(event) {
  event.preventDefault();

  const langCode = document.querySelector('body').dataset.lang;

  const btn = event.target;
  const newValueDiv = btn.closest('.new-value-cell');

  const statementsDiv = btn.closest('.statement-group');
  const propertyId = statementsDiv.dataset.propertyId;

  const valueDiv = generateElement('<div class="value-cell">');
  const actionsDiv = generateElement('<div class="actions-cell">');
  const snakDiv = generateElement('<div class="snak-cell">');
  snakDiv.append(valueDiv, actionsDiv);
  newValueDiv.before(snakDiv);

  const propertyType = await fetchPropertyDataType(propertyId);
  const {rankSelector, snakTypeSelector, snakInput} = await createSnakInput(langCode, propertyType);
  valueDiv.replaceChildren();
  valueDiv.append(rankSelector, snakTypeSelector, snakInput);

  const getSubmitHandler = async event => {
    event.preventDefault();
    const data = await createStatement(snakTypeSelector.value, rankSelector.value, propertyId,
      document.querySelector('h1').dataset.itemId, getValueFromInputTd(propertyType, valueDiv));
    updateDivWithNewStatement(data.updatedHtml, snakDiv);
  };

  const getCancelHandler = event => {
    event.preventDefault();
    snakDiv.remove();
  };

  createSubmitCancelButtons(actionsDiv, getSubmitHandler, getCancelHandler);
}

async function editSnak(event) {
  event.preventDefault();

  const langCode = document.querySelector('body').dataset.lang;

  const btn = event.target;
  const snakDiv = btn.closest('.snak-cell');

  const originalHtml = snakDiv.innerHTML;
  const statementId = parseInt(snakDiv.dataset.statementId, 10);

  const {
    rank,
    mainSnak
  } = await getAsJson(`/api/statement/${statementId}`, "Erreur de chargement des données du statement.");
  const {propertyType, value, snak_type} = mainSnak;
  const valueDiv = snakDiv.querySelector('.value-cell');

  const {
    rankSelector,
    snakTypeSelector,
    snakInput
  } = await createSnakInput(langCode, propertyType, value, rank, snak_type);
  valueDiv.replaceChildren();
  valueDiv.append(rankSelector, snakTypeSelector, snakInput);

  const actionsDiv = snakDiv.querySelector('.actions-cell');

  const getSubmitHandler = async event => {
    event.preventDefault();

    const data = await updateStatement(statementId, rankSelector.value, snakTypeSelector.value,
      getValueFromInputTd(propertyType, valueDiv));
    updateDivWithNewStatement(data.updatedHtml, snakDiv);
  };

  const getCancelHandler = event => {
    event.preventDefault();
    snakDiv.innerHTML = originalHtml;
  };

  createSubmitCancelButtons(actionsDiv, getSubmitHandler, getCancelHandler);
}

async function deleteValue(event) {
  event.preventDefault();

  const btn = event.target;

  const snakDiv = btn.closest('.snak-cell');
  const statementDiv = snakDiv.closest('.statement-group');
  const statementId = snakDiv.dataset.statementId;

  const confirmed = window.confirm("Are you sure?");
  if (!confirmed) return;

  const data = await postAsJson('/api/statement/delete', `Erreur lors de la suppression du statement ${statementId}`, {statement_id: statementId});
  const statementNumber = data.number;
  if (statementNumber === 0) {
    statementDiv.remove();
  } else {
    snakDiv.remove();
  }
}

/**
 *
 * @param {HTMLElement} mapElement
 */
function generateLeafletMap(mapElement) {
  const id = mapElement.getAttribute('id');
  const latitude = parseFloat(mapElement.dataset.lat);
  const longitude = parseFloat(mapElement.dataset.lon);

  const map = L.map(id).setView([latitude, longitude], 6);
  L.tileLayer('https://dh.gu.se/tiles/imperium/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://imperium.ahlfeldt.se/">DARE</a>',
    maxZoom: 10
  }).addTo(map);
  L.marker([latitude, longitude]).addTo(map);
}

async function addNewQualifier(event) {
  event.preventDefault();

  const statementId = event.target.dataset.statementId;
  const langCode = document.querySelector('body').dataset.lang;

  // Choose property
  const propertySelector = await createPropertySelector(langCode);
  const propertyDiv = generateElement('<div class="qualifier-cell">');
  propertyDiv.append(propertySelector);

  const valueDiv = generateElement('<div class="qualifier-value-div">');
  const actionsDiv = generateElement('<div class="actions-cell">');
  const snakDiv = generateElement('<div class="snak-cell">');
  snakDiv.append(valueDiv, actionsDiv);
  propertyDiv.append(snakDiv);
  event.target.before(propertyDiv);

  propertySelector.addEventListener('change', async () => {
    const datatype = propertySelector.querySelector('option:checked').dataset.type;
    const {snakInput} = await createSnakInput(langCode, datatype);
    valueDiv.replaceChildren();
    valueDiv.append(snakInput);
  });

  const getSubmitHandler = async event => {
    event.preventDefault();

    const selectedOption = propertySelector.querySelector('option:checked');
    const datatype = selectedOption.dataset.type;
    const propertyId = selectedOption.value;
    console.log(event.currentTarget, event.target);
    const data = await createQualifier(statementId, propertyId, getValueFromInputTd(datatype, valueDiv));
    propertyDiv.parentNode.outerHTML = data.updatedHtml;
  };

  const getCancelHandler = event => {
    event.preventDefault();
    propertyDiv.remove();
  };

  createSubmitCancelButtons(actionsDiv, getSubmitHandler, getCancelHandler);
}

async function editQualifier(event) {
  event.preventDefault();

  const langCode = document.querySelector('body').dataset.lang;


  const btn = event.target;
  const snakDiv = btn.closest('.snak-cell');

  const originalHtml = snakDiv.innerHTML;
  const statementId = parseInt(snakDiv.dataset.statementId, 10);

  const {
    rank,
    mainSnak
  } = await getAsJson(`/api/statement/${statementId}`, "Erreur de chargement des données du statement.");
  const {propertyType, value, snak_type} = mainSnak;
  const valueDiv = snakDiv.querySelector('.value-cell');

  const {
    rankSelector,
    snakTypeSelector,
    snakInput
  } = await createSnakInput(langCode, propertyType, value, rank, snak_type);
  valueDiv.replaceChildren();
  valueDiv.append(rankSelector, snakTypeSelector, snakInput);

  const actionsDiv = snakDiv.querySelector('.actions-cell');

  const getSubmitHandler = async event => {
    event.preventDefault();

    const data = await updateStatement(statementId, rankSelector.value, snakTypeSelector.value,
      getValueFromInputTd(propertyType, valueDiv));
    updateDivWithNewStatement(data.updatedHtml, snakDiv);
  };

  const getCancelHandler = event => {
    event.preventDefault();
    snakDiv.innerHTML = originalHtml;
  };

  createSubmitCancelButtons(actionsDiv, getSubmitHandler, getCancelHandler);
}

async function deleteQualifier(event) {
  event.preventDefault();

  const btn = event.target;

  const qualifierDiv = btn.closest('.qualifier-cell');
  const qualifierGroupDiv = qualifierDiv.closest('.qualifiers-cell');
  const qualifierId = qualifierDiv.dataset.qualifierId;

  const confirmed = window.confirm("Are you sure?");
  if (!confirmed) return;

  const data = await postAsJson('/api/qualifier/delete', `Erreur lors de la suppression du qualifier ${qualifierId}`, {qualifier_id: qualifierId});
  const qualifierNumber = data.number;
  qualifierDiv.remove();
  if (qualifierNumber === 0) {
    const noQualifiersDiv = document.createElement('div');
    noQualifiersDiv.textContent = 'No qualifiers.';
    qualifierGroupDiv.prepend(noQualifiersDiv);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const newStatementBtn = document.querySelector('#btn-new-statement');
  if (newStatementBtn) newStatementBtn.addEventListener('click', addNewStatement);
  document.querySelectorAll('.statements').forEach(element =>
    element.addEventListener('click', async event => {
      if (event.target.closest('.btn-add-value'))
        await addnewSnak(event);
      if (event.target.closest('.btn-edit-value'))
        await editSnak(event);
      if (event.target.closest('.btn-delete-value'))
        await deleteValue(event);
      if (event.target.closest('.btn-add-qualifier'))
        await addNewQualifier(event);
      if (event.target.closest('.btn-edit-qualifier'))
        await editQualifier(event);
      if (event.target.closest('.btn-delete-qualifier'))
        await deleteQualifier(event);

    })
  );
  document.querySelectorAll('.map').forEach(item => generateLeafletMap(item));
});