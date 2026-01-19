'use strict';

import {getAsJson} from './api.js';

function getLabel(value, lang_code) {
  if (!value.labels) return '(no label)';
  return value.labels[lang_code] || (value.labels['en'] ? `(en) ${value.labels['en']}` : '(no label)');
}

/**
 *
 * @param html
 * @returns {HTMLElement}
 */
export function generateElement(html) {
  const template = document.createElement('template');
  template.innerHTML = html.trim();
  return template.content.children[0];
}

/**
 * Create two buttons: submit and cancel, attach to them click event handles and append them to the actions element.
 * @param actions The element to which the two buttons will be appended.
 * @param submitHandle The click event handle for the submit button.
 * @param cancelHandle The click event handle for the cancel button.
 */
export function createSubmitCancelButtons(actions, submitHandle, cancelHandle) {
  const submitBtn = generateElement('<a class="button">Submit</a>');
  const cancelBtn = generateElement('<a class="button">Cancel</a>');

  submitBtn.addEventListener('click', submitHandle);
  cancelBtn.addEventListener('click', cancelHandle);

  actions.replaceChildren();
  actions.append(submitBtn, cancelBtn);
}

export function updateDivWithNewStatement(updatedHtml, snakDiv) {
  const wrapper = document.createElement('div');
  wrapper.innerHTML = updatedHtml;
  snakDiv.replaceWith(wrapper.querySelector('.snak-cell'));
}

/**
 * Creates a promise for a selector filled with the existing properties.
 * @param {string} langCode The language code to use for the properties’ label.
 * @returns {Promise<HTMLElement>}
 */
export async function createPropertySelector(langCode) {
  const data = await getAsJson('/api/properties/?fields=labels', 'Erreur de chargement des propriétés');

  const propertySelector = generateElement('<select><option value="" disabled selected>-- Select a property --</option></select>');
  console.log(data)
  Object.values(data).forEach(property => {
    const option = generateElement('<option>');
    option.value = property['display_id'];
    option.dataset.type = property['type'];
    option.textContent = getLabel(property, langCode);
    propertySelector.append(option);
  });
  return propertySelector;
}

const datatypeHandlers = {
  Item: {
    /**
     *
     * @param langCode
     * @param defaultValue
     * @returns {Promise<HTMLElement>}
     */
    createInput: async (langCode, defaultValue) => {
      const data = await getAsJson('/api/items/?fields=labels', 'Erreur de chargement des éléments.');

      let valueInput = generateElement('<select class="value-selector">');
      if (!defaultValue) {
        valueInput.append(generateElement('<option value="" disabled selected>-- Select an item --</option>'));
      }

      Object.values(data).forEach(item => {
        let itemName = getLabel(item, langCode);
        const option = generateElement('<option>');
        option.value = item['display_id'];
        option.textContent = itemName;
        if (defaultValue && parseInt(item['display_id']) === parseInt(defaultValue.id))
          option.selected = true;
        valueInput.append(option);
      });
      return valueInput;
    },

    getValue: (input) => {
      const selected = input.querySelector('.value-selector option:checked');
      return {item: selected ? selected.value.substring(1) : ""};
    }
  },
  StringValue: {
    /**
     *
     * @param langCode
     * @param defaultValue
     * @returns {Promise<HTMLElement>}
     */
    createInput: async (langCode, defaultValue) => {
      const input = generateElement('<input>');
      input.setAttribute('type', 'text');
      input.value = defaultValue ? defaultValue.value : "";
      return input;
    },
    getValue: input => {
      return {value: input.querySelector('input').value};
    }
  },
  UrlValue: {
    /**
     *
     * @param langCode
     * @param defaultValue
     * @returns {Promise<HTMLElement>}
     */
    createInput: async (langCode, defaultValue) => {
      const input = generateElement('<input>');
      input.setAttribute('type', 'text');
      input.value = defaultValue ? defaultValue.value : "";
      return input;
    },
    getValue: input => {
      return {value: input.querySelector('input').value};
    }
  },
  MonolingualTextValue: {
    /**
     *
     * @param langCode
     * @param defaultValue
     * @returns {Promise<HTMLElement>}
     */
    createInput: async (langCode, defaultValue) => {
      const languageInput = generateElement('<input>');
      languageInput.setAttribute('type', 'text');
      languageInput.setAttribute('placeholder', 'Language code');
      languageInput.value = defaultValue ? defaultValue.lang : "";
      const textInput = generateElement('<input>');
      textInput.setAttribute('type', 'text');
      textInput.setAttribute('placeholder', 'Text');
      textInput.value = defaultValue ? defaultValue.value : "";
      const span = generateElement('<span>');
      span.append(languageInput, textInput);
      return span;
    },
    getValue: input => {
      const values = Array.from(input.querySelectorAll('input')).map(input => input.value);
      return {
        language: values[0],
        value: values[1]
      }
    }
  },
  QuantityValue: {
    /**
     *
     * @param langCode
     * @param defaultValue
     * @returns {Promise<HTMLElement>}
     */
    createInput: async (langCode, defaultValue) => {
      const htmlElement = generateElement('<input>');
      htmlElement.setAttribute('type', 'text');
      htmlElement.value = defaultValue ? defaultValue.number : "";
      return htmlElement;
    },
    getValue: input => {
      return {number: input.querySelector('input').value};
    }
  },
  GlobeCoordinatesValue: {
    /**
     *
     * @param langCode
     * @param defaultValue
     * @returns {Promise<HTMLElement>}
     */
    createInput: async (langCode, defaultValue) => {
      const latitudeInput = generateElement('<input>');
      latitudeInput.setAttribute('type', 'text');
      latitudeInput.setAttribute('placeholder', 'latitude');
      latitudeInput.value = defaultValue ? defaultValue.latitude : "";
      const longitudeInput = generateElement('<input>');
      longitudeInput.setAttribute('type', 'text');
      longitudeInput.setAttribute('placeholder', 'longitude');
      longitudeInput.value = defaultValue ? defaultValue.longitude : "";
      const span = generateElement('<span>');
      span.append(latitudeInput, longitudeInput);
      return span;
    },
    getValue: input => {
      const values = Array.from(input.querySelectorAll('input')).map(input => {
        return input.value;
      });
      return {
        latitude: values[0],
        longitude: values[1]
      }
    }
  },
  TimeValue: {
  }
};

export async function createSnakInput(langCode, datatype, defaultValue = null, rank = 0, snakType = 0) {
  const handler = datatypeHandlers[datatype];
  if (!handler) throw new Error(`No input creator for datatype: ${datatype}.`)
  const snakInput = await handler.createInput(langCode, defaultValue);
  const rankSelector = createRankSelector(rank);
  const snakTypeSelector = createSnakTypeSelector(snakInput, snakType);
  snakTypeSelector.dispatchEvent(new Event('change'));

  return {rankSelector, snakTypeSelector, snakInput};
}

/**
 *
 * @param datatype
 * @param valueInputTd
 * @returns {string}
 */
export function getValueFromInputTd(datatype, valueInputTd) {
  const handler = datatypeHandlers[datatype];
  if (!handler) throw new Error(`No value extractor for datatype: ${datatype}.`)
  return handler.getValue(valueInputTd);
}

/**
 * Create a selector for the snak type (Value, SomeValue, NoValue) and initialise it.
 * The selected option is the one matching the value of snakType.
 * @param {HTMLElement} snakInput The input field of the snak value to be shown or hidden.
 * @param {int} snakType The index of the option to be selected.
 * @returns {HTMLElement} The snak type selector element.
 */
export function createSnakTypeSelector(snakInput, snakType = 0) {
  const snakTypeSelector = generateElement('<select class="snak-type-selector">');
  for (const [snakTypeValue, snakTypeLabel] of [[0, 'Value'], [1, 'Unknown value'], [2, 'No value']]) {
    const option = generateElement('<option>');
    option.value = snakTypeValue;
    option.textContent = snakTypeLabel;
    if (snakType === snakTypeValue)
      option.selected = true;
    snakTypeSelector.append(option);
  }

  snakTypeSelector.addEventListener('change', event => {
    const value = parseInt(event.target.value, 10);
    if (value === 0) {
      snakInput.style.display = '';
    } else {
      snakInput.style.display = 'none';
    }
  });

  return snakTypeSelector;
}

/**
 * Create a selector for the snak rank and initialise it.
 * @param {int} rank The index of the rank to be selected by default. 1 for Preferred, 0 for Normal, -1 for Obsolete.
 * @returns {HTMLElement} The rank selector.
 */
export function createRankSelector(rank = 0) {
  const rankSelector = generateElement('<select class="rank-selector">');
  for (const [rankValue, rankLabel] of [[1, 'Preferred'], [0, 'Normal'], [-1, 'Obsolete']]) {
    const option = generateElement('<option>');
    option.value = rankValue;
    option.textContent = rankLabel;
    if (rank === rankValue)
      option.selected = true;
    rankSelector.append(option);
  }
  return rankSelector;
}

export function debounce(fn, wait = 250) {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), wait);
  };
}
