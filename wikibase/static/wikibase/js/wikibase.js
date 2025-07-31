'use strict';

import {createStatement, updateStatement, fetchPropertyDataType, getAsJson, postAsJson} from './api.js';
import {
  createPropertySelector,
  createSnakInput,
  createSubmitCancelButtons,
  getValueFromInputTd,
  updateDivWithNewStatement
} from './util.js';


/**
 *
 * @param event
 * @returns {Promise<void>}
 */
async function addNewStatement(event) {
  event.preventDefault();

  const langCode = $('body').data('lang');

  // Choose property
  const $propertySelector = await createPropertySelector(langCode);

  const $propertyDiv = $('<div class="property-cell">').append($propertySelector);
  const $valueDiv = $('<div class="value-cell">');
  const $actionsDiv = $('<div class="actions-cell">');
  const $snakDiv = $('<div class="snak-cell">').append($valueDiv, $actionsDiv);
  const $statementsDiv = $('<div class="statement-group">').append($propertyDiv, $snakDiv);

  $(event.currentTarget).before($statementsDiv);

  $propertySelector.on('change', async () => {
    const datatype = $propertySelector.find('option:selected').data('type');
    const {$rankSelector, $snakTypeSelector, $snakInput} = await createSnakInput(langCode, datatype);
    $valueDiv.empty().append($rankSelector, $snakTypeSelector, $snakInput);
  });

  const getSubmitHandler = async event => {
    event.preventDefault();

    const $selectedOption = $propertySelector.find('option:selected');
    const datatype = $selectedOption.data('type');
    const propertyId = $selectedOption.val();
    const data = await createStatement($valueDiv.find('.snak-type-selector').val(), $valueDiv.find('.rank-selector').val(), propertyId, $('h1').data('item_id'), getValueFromInputTd(datatype, $valueDiv));
    $statementsDiv.replaceWith(data.updatedHtml);
    $statementsDiv.find('.btn-add-value').on('click', addnewSnak);
  };

  const getCancelHandler = event => {
    event.preventDefault();
    $statementsDiv.remove();
  };

  createSubmitCancelButtons($actionsDiv, getSubmitHandler, getCancelHandler);
}

async function addnewSnak(event) {
  event.preventDefault();

  const langCode = $('body').data('lang');

  const $btn = $(this);
  const $newValueDiv = $btn.closest('.new-value-cell');

  const $statementsDiv = $btn.closest('.statement-group');
  const propertyId = $statementsDiv.data('property-id');

  const $valueDiv = $('<div class="value-cell">');
  const $actionsDiv = $('<div class="actions-cell">');
  const $snakDiv = $('<div class="snak-cell">').append($valueDiv, $actionsDiv);
  $newValueDiv.before($snakDiv);

  const propertyType = await fetchPropertyDataType(propertyId);
  const {$rankSelector, $snakTypeSelector, $snakInput} = await createSnakInput(langCode, propertyType);
  $valueDiv.empty().append($rankSelector, $snakTypeSelector, $snakInput);

  const getSubmitHandler = async event => {
    event.preventDefault();
    const data = await createStatement($snakTypeSelector.val(), $rankSelector.val(), propertyId, $('h1').data('item_id'), getValueFromInputTd(propertyType, $valueDiv));
    updateDivWithNewStatement(data.updatedHtml, $snakDiv);
  };

  const getCancelHandler = event => {
    event.preventDefault();
    $snakDiv.remove();
  };

  createSubmitCancelButtons($actionsDiv, getSubmitHandler, getCancelHandler);
}

async function editSnak(event) {
  event.preventDefault();

  const langCode = $('body').data('lang');

  const $btn = $(this);
  const $snakDiv = $btn.closest('.snak-cell');

  const originalHtml = $snakDiv.html();
  const statementId = $snakDiv.data('statement-id');

  const {
    rank,
    mainSnak
  } = await getAsJson(`/api/statement/${statementId}`, "Erreur de chargement des données du statement.");
  const {propertyType, value, snak_type} = mainSnak;
  const $valueDiv = $snakDiv.find('.value-cell');

  const {$rankSelector, $snakTypeSelector, $snakInput} = await createSnakInput(langCode, propertyType, value, rank, snak_type);
  $valueDiv.empty().append($rankSelector, $snakTypeSelector, $snakInput);

  const $actionsDiv = $snakDiv.find('.actions-cell');

  const getSubmitHandler = async event => {
    event.preventDefault();

    const data = await updateStatement(statementId, $rankSelector.val(), $snakTypeSelector.val(), getValueFromInputTd(propertyType, $valueDiv));
    updateDivWithNewStatement(data.updatedHtml, $snakDiv);
  };

  const getCancelHandler = event => {
    event.preventDefault();
    $snakDiv.html(originalHtml);
    $snakDiv.find('.btn-edit-value').on('click', editSnak);
    $snakDiv.find('.btn-delete-value').on('click', deleteValue);
  };

  createSubmitCancelButtons($actionsDiv, getSubmitHandler, getCancelHandler);
}

async function deleteValue(event) {
  event.preventDefault();

  const $btn = $(this);

  const $snakDiv = $btn.closest('.snak-cell');
  const $statementDiv = $snakDiv.closest('.statement-group');
  const statementId = $snakDiv.data('statement-id');

  const confirmed = window.confirm("Are you sure?");
  if (!confirmed) return;

  const data = await postAsJson('/api/statement/delete', `Erreur lors de la suppression du statement ${statementId}`, {statement_id: statementId});
  const statementNumber = data.number;
  if (statementNumber === 0) {
    $statementDiv.remove();
  } else {
    $snakDiv.remove();
  }
}

function generateLeafletMap() {
  const $map = $(this);
  const id = $map.attr('id');
  const latitude = parseFloat($map.data('lat'));
  const longitude = parseFloat($map.data('lon'));

  const map = L.map(id).setView([latitude, longitude], 6);
  L.tileLayer('https://dh.gu.se/tiles/imperium/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://imperium.ahlfeldt.se/">DARE</a>',
    maxZoom: 10
  }).addTo(map);
  L.marker([latitude, longitude]).addTo(map);
}

$(function () {
  $('#btn-new-statement').on('click', addNewStatement);
  $('.statements')
    .on('click', '.btn-add-value', addnewSnak)
    .on('click', '.btn-edit-value', editSnak)
    .on('click', '.btn-delete-value', deleteValue);
  $('.map').each(generateLeafletMap);
});