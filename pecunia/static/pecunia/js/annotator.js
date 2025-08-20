'use strict';

import {Stack} from './stack.js';

function addTag(beginTag, endTag) {
  const $annotatorTextField = $('.annotator-text-field');
  let textarea = $annotatorTextField[0];
  let start = textarea.selectionStart;
  let end = textarea.selectionEnd;

  let selection = textarea.value.substring(start, end);
  let tagged = `${beginTag}${selection}${endTag}`;

  const {
    charOverlap,
    msgOverlap
  } = checkCharacterOverlap($annotatorTextField.text(), selection, start);
  if (charOverlap || checkTagOverlap($annotatorTextField.text(), selection)) {
    alert(`Erreur dans la sélection : ${msgOverlap}. Impossible d’ajouter les balises.`);
  } else {
    textarea.setRangeText(tagged, start, end, 'end');

    textarea.setSelectionRange(start + 3, start + selection.length + 3);
    textarea.focus();
    $annotatorTextField.trigger('input');
  }
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

  if (wElements && wElements.length > 0) {
    let $list = $('<ul>');

    wElements.forEach((w, index) => {
      const $li = $('<li class="typed">').text(w.textContent || '');

      if (w.hasAttribute('type')) {
        $li.addClass(`type-${w.getAttribute('type')}`);
      }

      if (w.hasAttribute('qid')) {
        const qid = w.getAttribute('qid');
        $li.append(' lié à ', $('<a>').attr('href', "/item/${qid}").text(`Q${qid}`));
      } else {
        const $newItemBtn = $('<a>')
          .attr('href', '#')
          .data('w-index', "index")
          .text('créer un élément');
        const $searchItemBtn = $('<a>')
          .attr('href', '#')
          .data('w-index', index)
          .text('chercher un élément');
        $li.append(' (', $newItemBtn, ', ', $searchItemBtn, ')');

        $newItemBtn.on('click', event => {
          event.preventDefault();
          // TODO Implémenter
        });

        $searchItemBtn.on('click', event => {
          event.preventDefault();
          // TODO Implémenter
        });
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
 * @param {string} selection
 * @param {number} selectionStart
 * @returns {{charOverlap: boolean, msgOverlap: string}}
 */
function checkCharacterOverlap(text, selection, selectionStart) {
  let stack = new Stack();
  for (const c of selection) {
    if (c === "<") stack.push("<");
    else if (c === ">") {
      if (stack.isEmpty()) {
        return {charOverlap: true, msgOverlap: 'Fin de balise sélectionnée'};
      } else if (stack.top() === "<") {
        stack.pop();
      } else {
        return {charOverlap: true, msgOverlap: ''}; // Cette situation ne peut pas arriver.
      }
    }
  }
  console.log(stack);
  if (!stack.isEmpty())
    return {'charOverlap': true, 'msgOverlap': 'Début de balise sélectionné'};

  for (let i = selectionStart - 1; i >= 0; i--) {
    console.log(i, text.at(i));
    if (text.at(i) === ">") break;
    if (text.at(i) === "<")
      return {charOverlap: true, msgOverlap: 'Intérieur d’une balise sélectionné'};
  }

  return {charOverlap: false, msgOverlap: ''};
}

function checkTagOverlap(text, selection) {
  let stack = new Stack();
  for (const c of selection) {
    if (c === "<") {
      // TODO Implementer
    }
  }
  return false;
}

let lastSelection = "";

// TODO: Faire en sorte que ça ne soit lancé que pour éditer les textes
$(() => {
  const $annotatorTextField = $('.annotator-text-field');
  $annotatorTextField.on('input', parseAnnotationTextArea);
  $annotatorTextField.on('selectionchange', function () {
    let selection = window.getSelection().toString();
    if (selection !== lastSelection) {
      const $warningSpan = $('.warning-span');
      lastSelection = selection;
      if (selection.length > 0) {
        const {
          charOverlap,
          msgOverlap
        } = checkCharacterOverlap($annotatorTextField.text(), selection, $annotatorTextField[0].selectionStart);
        if (charOverlap || checkTagOverlap($annotatorTextField.text(), selection)) {
          $warningSpan.text(`Erreur ! (${msgOverlap})`);
        } else {
          $warningSpan.text("Pas d’erreur.");
        }
      } else {
        $warningSpan.text("Pas d’erreur.");
      }
    }
  });

  $annotatorTextField.trigger('input');
});