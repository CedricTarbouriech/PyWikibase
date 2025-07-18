function addTag(beginTag, endTag) {
  let textarea = $('#textfield')[0];
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
  const $textfield = $('#textfield');
  if (!$textfield.length) return;
  const textValue = $textfield.val().toString();
  let $matchDiv = $('div#matchResult');
  if ($matchDiv.length === 0) {
    $matchDiv = $('<div id="matchResult"></div>');
    $textfield.after($matchDiv);
  }
  if ($('#wbtn').length === 0) {
    const $btns = $('<div id="wbtn">');
    $btns.append($('<a class="button" onclick="addWTag()">&lt;w&gt;</a>'));
    $btns.append($('<a class="button" onclick="addPersonTag()">Person</a>'));
    $btns.append($('<a class="button" onclick="addPlaceTag()">Place</a>'));
    $btns.append($('<a class="button" onclick="addResourceTag()">Resource</a>'));
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

// TODO: Faire en sorte que ça ne soit lancé que pour éditer les textes
$(() => {
  $('#textfield').on('input', parseAnnotationTextArea);
  parseAnnotationTextArea();
});