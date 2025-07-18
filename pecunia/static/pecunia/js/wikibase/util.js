'use strict';

import {getAsJson} from '../api.js';

function getLabel(value, lang_code) {
  if (!value.labels) return '(no label)';
  return value.labels[lang_code] || (value.labels['en'] ? `(en) ${value.labels['en']}` : '(no label)');
}

export function incrementRowSpan($element) {
  const incrementedRowSpan = parseInt($element.attr('rowspan')) + 1;
  $element.attr('rowspan', incrementedRowSpan);
}

/**
 * Create two buttons: submit and cancel, attach to them click event handles and append them to the $actions element.
 * @param $actions The element to which the two buttons will be appended.
 * @param submitHandle The click event handle for the submit button.
 * @param cancelHandle The click event handle for the cancel button.
 */
export function createSubmitCancelButtons($actions, submitHandle, cancelHandle) {
  const $submitBtn = $('<a class="button">Submit</a>');
  const $cancelBtn = $('<a class="button">Cancel</a>');

  $submitBtn.on('click', submitHandle);
  $cancelBtn.on('click', cancelHandle);

  $actions.append($submitBtn, $cancelBtn);
}

export function updateTableWithNewStatement(updatedHtml, $tr) {
  const $updateHtml = $(updatedHtml);
  const $valueInputTd = $tr.find('.value-input-cell');
  const $actions = $tr.find('.actions-cell');
  const $firstTr = $updateHtml.find('tr:first');
  const $tds = $firstTr.find('td');
  $tr.data('statement-id', $firstTr.data('statement-id'));
  $valueInputTd.replaceWith($tds.get()[1]);
  $actions.replaceWith($tds.get()[2]);
}

/**
 * Creates a promise for a selector filled with the existing properties.
 * @param lang_code The language code to use for the properties’ label.
 * @returns {Promise<JQuery<HTMLElement>>}
 */
export async function createPropertySelector(lang_code) {
  const data = await getAsJson('/api/properties', 'Erreur de chargement des propriétés');

  const $propertySelector = $('<select><option value="" disabled selected>-- Select a property --</option></select>');
  Object.entries(data).forEach(([key, value]) => {
    const $option = $('<option>')
      .val(key)
      .data('type', value.type)
      .text(getLabel(value, lang_code))
    $propertySelector.append($option);
  });
  return $propertySelector;
}

const datatypeHandlers = {
  Item: {
    createInput: async (langCode, defaultValue) => {
      const data = await getAsJson('/api/items', 'Erreur de chargement des éléments.');

      let $valueInput = $('<select class="value-selector">');
      if (!defaultValue) {
        $valueInput.append($('<option value="" disabled selected>-- Select an item --</option>'));
      }

      Object.entries(data).forEach(([key, value]) => {
        let itemName = getLabel(value, langCode);
        const $option = $('<option>')
          .val(key)
          .text(itemName);
        if (defaultValue && parseInt(key) === parseInt(defaultValue.id))
          $option.prop('selected', true);

        $valueInput.append($option);
      });
      return $valueInput;
    },

    getValue: ($input) => {
      return {item: $input.find('.value-selector option:selected').val()};
    }
  },
  StringValue: {
    createInput: async (langCode, defaultValue) => {
      return $('<input>').attr('type', 'text').val(defaultValue ? defaultValue.value : "");
    },
    getValue: ($input) => {
      return {value: $input.find('input').val()};
    }
  },
  UrlValue: {
    createInput: async (langCode, defaultValue) => {
      return $('<input>').attr('type', 'text').val(defaultValue ? defaultValue.value : "");
    },
    getValue: ($input) => {
      return {value: $input.find('input').val()};
    }
  },
  MonolingualTextValue: {
    createInput: async (langCode, defaultValue) => {
      const $languageInput = $('<input>').attr('type', 'text').attr('placeholder', 'Language code').val(defaultValue ? defaultValue.lang : "");
      const $textInput = $('<input>').attr('type', 'text').attr('placeholder', 'Text').val(defaultValue ? defaultValue.value : "");
      return $('<span>').append($languageInput, $textInput);
    },
    getValue: ($input) => {
      const values = $input.find('input').map(function () {
        return $(this).val();
      }).get();
      return {
        language: values[0],
        value: values[1]
      }
    }
  },
  QuantityValue: {
    createInput: async (langCode, defaultValue) => {
      return $('<input>').attr('type', 'text').val(defaultValue ? defaultValue.number : "");
    },
    getValue: ($input) => {
      return {number: $input.find('input').val()};
    }
  },
  GlobeCoordinatesValue: {
    createInput: async (langCode, defaultValue) => {
      const $latitudeInput = $('<input>').attr('type', 'text').attr('placeholder', 'latitude').val(defaultValue ? defaultValue.latitude : "");
      const $longitudeInput = $('<input>').attr('type', 'text').attr('placeholder', 'longitude').val(defaultValue ? defaultValue.longitude : "");
      return $('<span>').append($latitudeInput, $longitudeInput);
    },
    getValue: ($input) => {
      const values = $input.find('input').map(function () {
        return $(this).val();
      }).get();
      return {
        latitude: values[0],
        longitude: values[1]
      }
    }
  },
  TimeValue: {}
};

export async function createSnakInput(langCode, datatype, defaultValue = null) {
  const handler = datatypeHandlers[datatype];
  if (!handler) throw new Error(`No input creator for datatype: ${datatype}.`)
  return handler.createInput(langCode, defaultValue);
}

export function getValueFromInputTd(datatype, $valueInputTd) {
  const handler = datatypeHandlers[datatype];
  if (!handler) throw new Error(`No value extractor for datatype: ${datatype}.`)
  return handler.getValue($valueInputTd);
}

/**
 * Create a selector for the snak type (Value, SomeValue, NoValue) and initialise it.
 * The selected option is the one matching the value of snakType.
 * @param $snakInput The input field of the snak value to be shown or hidden.
 * @param {int} snakType The index of the option to be selected.
 * @returns {*|jQuery|HTMLElement|JQuery<HTMLElement>} The snak type selector element.
 */
export function createSnakTypeSelector($snakInput, snakType = 0) {
  const $snakTypeSelector = $('<select>');
  for (const [snakTypeValue, snakTypeLabel] of [[0, 'Value'], [1, 'Unknown value'], [2, 'No value']]) {
    const $option = $('<option>').val(snakTypeValue).text(snakTypeLabel);
    if (snakType === snakTypeValue)
      $option.prop('selected', true);
    $snakTypeSelector.append($option);
  }

  $snakTypeSelector.on('change', event => {
    const value = parseInt($(event.currentTarget).val());
    if (value === 0) {
      $snakInput.show();
    } else {
      $snakInput.hide();
    }
  });
  return $snakTypeSelector;
}

/**
 * Create a selector for the snak rank and initialise it.
 * @param {int} rank The index of the rank to be selected by default. 1 for Preferred, 0 for Normal, -1 for Obsolete.
 * @returns {*|jQuery|HTMLElement|JQuery<HTMLElement>} The rank selector.
 */
export function createRankSelector(rank = 0) {
  const $rankSelector = $('<select>');
  for (const [rankValue, rankLabel] of [[1, 'Preferred'], [0, 'Normal'], [-1, 'Obsolete']]) {
    const $option = $('<option>').val(rankValue).text(rankLabel);
    if (rank === rankValue)
      $option.prop('selected', true);
    $rankSelector.append($option);
  }
  return $rankSelector;
}