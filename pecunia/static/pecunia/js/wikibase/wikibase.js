'use strict';

import {createStatement, fetchPropertyDataType, getAsJson, postAsJson} from '../api.js';
import {
  createPropertySelector,
  createRankSelector,
  createSnakInput,
  createSnakTypeSelector,
  createSubmitCancelButtons,
  getValueFromInputTd,
  incrementRowSpan,
  updateTableWithNewStatement
} from './util.js';

function tmp(editMode, chooseValue, sendPost, updateTable) {
  editMode();
  chooseValue();
  sendPost();
  updateTable();
}

async function addNewStatement(event) {
  event.preventDefault();
  const lang_code = $('body').data('lang');

  // Choose property
  const $propertySelector = await createPropertySelector(lang_code);
  const $propertyTd = $('<td class="propertySelector">').append($propertySelector);
  const $valueInputTd = $('<td class="value-input-cell">');
  const $actionsTd = $('<td class="actions">');
  const $tr = $('<tr>').append($propertyTd, $valueInputTd, $actionsTd);
  const $table = $('<table>').append($tr);

  $propertySelector.on('change', async () => {
    const datatype = $propertySelector.find('option:selected').data('type');
    const $propertyValueInput = await createSnakInput(lang_code, datatype);
    $valueInputTd.html($propertyValueInput);
  });

  const getSubmitHandler = async event => {
    event.preventDefault();

    const $selectedOption = $propertySelector.find('option:selected');
    const datatype = $selectedOption.data('type');
    const propertyId = $selectedOption.val();
    const data = await createStatement('0', propertyId, $('h1').data('item_id'), getValueFromInputTd(datatype, $valueInputTd));
    $table.replaceWith(data.updatedHtml);
    $table.find('.btn-add-value').on('click', addnewSnak);
  };

  const getCancelHandler = event => {
    event.preventDefault();
    $table.remove();
  };

  createSubmitCancelButtons($actionsTd, getSubmitHandler, getCancelHandler);

  $(event.currentTarget).before($table);
}

async function addnewSnak(event) {
  event.preventDefault();

  const langCode = $('body').data('lang');

  const $btn = $(this);
  const $closestTr = $btn.closest('tr');

  const $table = $btn.closest('table');
  const propertyId = $table.data('property-id');

  const $valueInputTd = $('<td class="value-input-cell">');
  const $actionsTd = $('<td class="actions-cell">');
  const $newTr = $('<tr></tr>').append($valueInputTd, $actionsTd);
  $closestTr.before($newTr);
  const $propertyTd = $table.find('td[rowspan]');
  incrementRowSpan($propertyTd);

  const datatype = await fetchPropertyDataType(propertyId);
  const $snakInput = await createSnakInput(langCode, datatype);

  const $rankSelector = createRankSelector();
  const $snakTypeSelector = createSnakTypeSelector($snakInput, 0);
  $snakTypeSelector.trigger('change');
  $valueInputTd.empty().append($rankSelector, $snakTypeSelector, $snakInput);

  const getSubmitHandler = async event => {
    event.preventDefault();
    const data = await createStatement($snakTypeSelector.val(), propertyId, $('h1').data('item_id'), getValueFromInputTd(datatype, $valueInputTd));
    updateTableWithNewStatement(data.updatedHtml, $newTr);
  };

  const getCancelHandler = event => {
    event.preventDefault();
    $newTr.remove();
    $propertyTd.attr('rowspan', parseInt($propertyTd.attr('rowspan')) - 1);
  };

  createSubmitCancelButtons($actionsTd, getSubmitHandler, getCancelHandler);
}

async function editSnak(event) {
  event.preventDefault();

  const langCode = $('body').data('lang');

  const $btn = $(this);
  const $closestTr = $btn.closest('tr');

  const originalHtml = $closestTr.html();
  const statementId = $closestTr.data('statement-id');

  const {
    rank,
    mainSnak
  } = await getAsJson(`/api/statement/${statementId}`, "Erreur de chargement des données du statement.");
  const {propertyType, value, snak_type} = mainSnak;

  const $snakInput = await createSnakInput(langCode, propertyType, value);
  const $valueInputTd = $closestTr.find('td.value-cell');
  $valueInputTd.removeClass('value-cell');
  $valueInputTd.addClass('value-input-cell');

  const $rankSelector = createRankSelector(rank);
  const $snakTypeSelector = createSnakTypeSelector($snakInput, parseInt(snak_type));
  $snakTypeSelector.trigger('change');
  $valueInputTd.empty().append($rankSelector, $snakTypeSelector, $snakInput);

  const $actions = $closestTr.find('.actions-cell');

  const getSubmitHandler = async event => {
    event.preventDefault();

    const data = await postAsJson('/api/statement/update', "Erreur dans la mise à jour du statement.", {
      statement_id: statementId,
      rank: $rankSelector.val(),
      snak_type: $snakTypeSelector.val(),
      value: getValueFromInputTd(propertyType, $valueInputTd)
    });

    updateTableWithNewStatement(data.updatedHtml, $closestTr);
  };

  const getCancelHandler = event => {
    event.preventDefault();
    $closestTr.html(originalHtml);
    $closestTr.find('.btn-edit-value').on('click', editSnak);
    $closestTr.find('.btn-delete-value').on('click', deleteValue);
  };

  createSubmitCancelButtons($actions, getSubmitHandler, getCancelHandler);
}

async function deleteValue(event) {
  event.preventDefault();
  const $btn = $(this);
  const $tr = $btn.closest('tr');
  const $table = $tr.closest('table');
  const statementId = $tr.data('statement-id');
  const confirmed = window.confirm("Are you sure?");
  if (!confirmed) return;

  const data = await postAsJson('/api/statement/delete', `Erreur lors de la suppression du statement ${statementId}`, {statement_id: statementId});
  const statementNumber = data.number;
  if (statementNumber === 0) {
    $table.remove();
  } else {
    const $allTrs = $table.find('tr');
    const isFirstTr = $allTrs.first().is($tr);

    if (isFirstTr) {
      const $nextTr = $tr.next('tr');
      const $rowspanTd = $tr.find('td[rowspan]');
      $rowspanTd.prependTo($nextTr);
    }

    const $updatedRowspanTd = $table.find('td[rowspan]');
    const currentRowspan = parseInt($updatedRowspanTd.attr('rowspan'));
    $updatedRowspanTd.attr('rowspan', currentRowspan - 1);

    $tr.remove();
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