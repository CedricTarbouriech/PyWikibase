'use strict';

import {Stack} from './stack.js';

function addTag(beginTag, endTag) {
  let textarea = ($('.annotator-text-field'))[0];
  let start = textarea.selectionStart;
  let end = textarea.selectionEnd;

  let selected = textarea.value.substring(start, end);
  let tagged = `${beginTag}${selected}${endTag}`;

  textarea.setRangeText(tagged, start, end, 'end');

  textarea.setSelectionRange(start + 3, start + selected.length + 3);
  textarea.focus();
  parseAnnotationTextArea();
}

function addWTag() {
  addTag('<w>', '</w>');
}

function addPersonTag() {
  addTag('<w type="person">', '</w>');
}

function addPlaceTag() {
  addTag('<w type="place">', '</w>');
}

function addResourceTag() {
  addTag('<w type="resource">', '</w>');
}

function parseAnnotationTextArea() {
  const $textfield = $('.annotator-text-field');
  if (!$textfield.length) return;
  const textValue = $textfield.val().toString();
  let $matchDiv = $('div#matchResult');
  if ($matchDiv.length === 0) {
    $matchDiv = $('<div id="matchResult"></div>');
    $textfield.after($matchDiv);
  }
  if ($('#wbtn').length === 0) {
    const $btns = $('<div id="wbtn">');
    $btns.append($('<a class="button">&lt;w&gt;</a>').on('click', addWTag));
    $btns.append($('<a class="button">Person</a>').on('click', addPersonTag));
    $btns.append($('<a class="button">Place</a>').on('click', addPlaceTag));
    $btns.append($('<a class="button">Resource</a>').on('click', addResourceTag));
    $matchDiv.before($btns);
  }

  const parser = new DOMParser();
  const doc = parser.parseFromString(`<xml>${textValue}</xml>`, 'application/xml');
  const wElements = doc.querySelectorAll('w');

  if (wElements) {
    let $list = $('<ul>');
    wElements.forEach(w => {
      let text = `${w.textContent}`;
      if (w.hasAttribute('id')) {
        const id = w.getAttribute('id');
        text += ` lié à <a href="/item/${id}">Q${id}</a>`;
      }
      const $li = $('<li class="typed">').html(text);
      if (w.hasAttribute('type')) {
        $li.addClass(`type-${w.getAttribute('type')}`);
      }
      $list.append($li);
    });

    $matchDiv.text('Liste des éléments trouvés :').append($list);
  } else {
    $matchDiv.text('Pas d’élément trouvé.');
  }
}


/**
 *
 * @param {string} text
 * @returns {boolean}
 */
function checkCharacterOverlap(text) {
  let stack = new Stack();
  for (const c of text) {
    if (c === "<") stack.push("<");
    else if (c === ">") {
      if (stack.isEmpty()) {
        return true;
      } else {
        if (stack.top() === "<") {
          stack.pop();
        } else {
          return true;
        }
      }
    }
  }
  return false;
}

function checkCharacterOverlap2(text) {
  let stack = new Stack();
  for (const c of text) {
    if (c === "<") stack.push("<");
    else if (c === ">") {
      if (stack.isEmpty()) {
        return true;
      } else {
        if (stack.top() === "<") {
          stack.pop();
        } else {
          return true;
        }
      }
    }
  }
  return !stack.isEmpty();
}

function checkTagOverlap(text) {
  return false;
}

let lastSelection = "";

// TODO: Faire en sorte que ça ne soit lancé que pour éditer les textes
$(() => {
  const $annotatorTextField = $('.annotator-text-field');
  $annotatorTextField.on('input', parseAnnotationTextArea);
  $annotatorTextField.on('mousedown', function () {
    $annotatorTextField.on('mousemove.selectionCheck', function () {
      let selection = window.getSelection().toString();
      if (selection !== lastSelection) {
        lastSelection = selection;
        if (selection.length > 0) {
          console.log('Nouvelle sélection:', selection);
          const $warningSpan = $('.warning-span');
          if (checkCharacterOverlap(selection) || checkTagOverlap(selection)) {
            $warningSpan.text("Erreur !");
          } else {
            $warningSpan.text("Pas d’erreur.");

          }
        }
      }
    });
  });

  $annotatorTextField.on('mouseup', function () {
    $annotatorTextField.off('mousemove.selectionCheck');
  });
  $annotatorTextField.on('select', function () {
    let selection = window.getSelection().toString();
    const $warningSpan = $('.warning-span');
    if (checkCharacterOverlap2(selection) || checkTagOverlap(selection)) {
      $warningSpan.text("Erreur !");
    } else {
      $warningSpan.text("Pas d’erreur.");
    }
    // TODO : retirer le warning si le texte est déselectionner.
  });
  $annotatorTextField.trigger('input');
});