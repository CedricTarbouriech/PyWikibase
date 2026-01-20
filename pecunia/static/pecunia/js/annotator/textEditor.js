import {debounce} from "../util.js";
import {DeleteDropZone, Pool, Token} from "./dragAndDrop.js";
import {Stack} from "../stack.js";
import {Component, createButton, createDiv, createSpan} from "../nodeUtil.js";

/**
 * Returns the next free id for a new tag.
 * If text does not contain any tags, returns 1;
 * @param {string} text the text to search tags into
 * @returns {number} the next free id
 */
function getNextFreeTagId(text) {
  const ids = text.matchAll(/<w id="(\d+)">/g).map(m => parseInt(m[1]));
  return Math.max(...ids, 0) + 1;
}

function getNextFreeUntagId() {
  // TODO Implement
  return 1;
}

/**
 *
 * @param {HTMLElement} node
 * @returns {boolean}
 */
function isIncompleteTag(node) {
  return node.nodeName === 'w' && node.getAttribute('part') === 'I';
}

function transformToLeiden(nodes, incomplete = false) {
  let root = document.createElement('div');
  for (const node of nodes) {
    switch (node.nodeType) {
      case Node.ELEMENT_NODE:
        let newNode = document.createElement('span');
        newNode.setAttribute('data-tei-tag', node.nodeName);
        for (const {name, value} of node.attributes)
          newNode.setAttribute(`data-tei-attr-${name}`, value);
        newNode.append(...transformToLeiden(node.childNodes, incomplete || isIncompleteTag(node)).childNodes);
        root.append(newNode);

        switch (node.nodeName) {
          case 'lb':
            const br = document.createElement('br');
            newNode.append(br);
            break;
          case 'gap':
            if (!node.hasAttribute("reason") || !node.hasAttribute('quantity') && !node.hasAttribute('extent')) {
              newNode.textContent = "gap without reason or quantity or extent";
              break;
            }
            let tmp = "";
            if (node.hasAttribute('quantity')) {
              tmp = ".".repeat(node.getAttribute("quantity"));
            } else if (node.hasAttribute('extent')) {
              tmp = '----';
            }
            if (node.getAttribute("reason") === "lost") {
              tmp = `[${tmp}]`;
            }
            newNode.textContent = tmp;
            break;
          case 'del':
            if (!node.hasAttribute("rend") || node.getAttribute("rend") !== "erasure") {
              newNode.textContent = 'del without rend="erasure"';
              break
            }
            newNode.prepend('⟦');
            newNode.append('⟧');
            break;
          case 'supplied':
            if (!node.hasAttribute("reason")) {
              newNode.textContent = 'supplied without reason';
              break;
            }

            if (node.getAttribute("reason") === "lost") {
              newNode.prepend('[');
              let suffix = ']';
              if (node.hasAttribute('cert') && node.getAttribute('cert') === 'low') {
                suffix = '?' + suffix;
              } else if (incomplete) {
                suffix = '-' + suffix;
              }
              newNode.append(suffix);
            } else if (node.getAttribute("reason") === "omitted") {
              newNode.prepend('<');
              newNode.append('>');
            }
            break;
          case 'surplus':
            newNode.prepend('{');
            newNode.append('}');
            break;
          case 'corr':
            newNode.prepend('<');
            newNode.append('>');
            break;
          case 'sic':
            newNode.hidden = true;
            break;
          case 'ex':
            newNode.prepend('(');
            let suffix = ')';
            if (node.hasAttribute('cert') && node.getAttribute('cert') === 'low') {
              suffix = '?' + suffix;
            } else if (incomplete) {
              suffix = '-' + suffix;
            }
            newNode.append(suffix);
            break;
          case 'space':
            newNode.textContent = 'v.';
            break;
          case 'g':
            newNode.textContent = `((${node.getAttribute('type')}))`;
            break;
        }
        break;
      case Node.TEXT_NODE:
        root.append(node.cloneNode());
        break;
    }
  }
  return root;
}

function transformFromLeiden(nodes) {
  let text = '';
  for (const node of nodes) {
    switch (node.nodeType) {
      case Node.ELEMENT_NODE:
        const tagType = node.getAttribute('data-tei-tag');
        const selfClosing = tagType === 'lb' || tagType === 'gap' || tagType === 'g' || tagType === 'space';
        if (text && tagType === 'lb')
          text += '\n';
        text += `<${tagType}`;

        for (const attr of node.attributes) {
          if (attr.name.startsWith('data-tei-attr-')) {
            text += ' ' + attr.name.substring('data-tei-attr-'.length) + '="' + attr.value + '"';
          }
        }

        if (selfClosing)
          text += `/>`;
        else {
          let childNodes = transformFromLeiden(node.childNodes);
          if (tagType === 'del' || tagType === 'supplied' || tagType === 'surplus' || tagType === 'ex' || tagType === 'corr') {
            childNodes = childNodes.slice(1, -1);
          }
          text += `>${childNodes}</${tagType}>`;
        }
        break;
      case Node.TEXT_NODE:
        text += node.textContent;
        break;
    }
  }
  return text;
}

export default class TextEditor extends Component {
  constructor(env) {
    super(document.getElementById('annotator'));

    this.textArea = document.getElementById('id_text');
    this.displayArea = createDiv({id: 'middle'});
    this.textArea.after(this.displayArea);

    const teiButton = createButton('TEI', {
      id: 'tei-tab-button', type: 'button', class: 'progressive'
    });
    const textButton = createButton('Text', {
      id: 'text-tab-button', type: 'button', class: 'progressive'
    });
    const bothButton = createButton('TEI & Text', {
      id: 'both-tab-button', type: 'button', class: 'progressive'
    });
    this.textArea.before(teiButton, textButton, bothButton);

    teiButton.addEventListener('click', () => {
      this.textArea.style.display = "";
      this.displayArea.style.display = "none";
    });
    textButton.addEventListener('click', () => {
      this.textArea.style.display = "none";
      this.displayArea.style.display = "";
    });
    bothButton.addEventListener('click', () => {
      this.textArea.style.display = "";
      this.displayArea.style.display = "";
    });

    if (this.textArea.value === "") {
      teiButton.click();
    } else {
      textButton.click();
    }

    this.textArea.addEventListener('input', debounce(_ => this.updateTokensFromText()));

    const parser = new DOMParser();

    this.textArea.addEventListener('input', _ => {
      const parsed = parser.parseFromString(`<xml>${this.textArea.value.replaceAll('\n', '')}</xml>`, "application/xml").childNodes[0];
      const toLeidenText = transformToLeiden(parsed.childNodes);
      this.displayArea.innerHTML = toLeidenText.innerHTML;
    });

    this.textArea.dispatchEvent(new CustomEvent('input'));

    let tagId = getNextFreeTagId(this.textArea.value);
    const tagButton = createButton('Tag entity', {
      id: 'tag-button', type: 'button', class: 'progressive'
    });

    tagButton.addEventListener('click', event => {

      const selection = document.getSelection();
      let anchorNode = selection.anchorNode;
      let focusNode = selection.focusNode;
      let anchorOffset = selection.anchorOffset;
      let focusOffset = selection.focusOffset;

      if (selection.direction === 'backward') {
        let tmp = focusNode;
        focusNode = anchorNode;
        anchorNode = tmp;

        tmp = focusOffset;
        focusOffset = anchorOffset;
        anchorOffset = tmp;
      }

      const span = document.createElement('span');
      span.classList.add('anno');
      span.setAttribute('data-tei-tag', 'w');
      span.setAttribute('data-tei-attr-id', tagId);
      tagId++;

      const range = document.createRange();
      range.setStart(anchorNode, anchorOffset);
      range.setEnd(focusNode, focusOffset);

      const content = range.extractContents();
      span.appendChild(content);
      range.insertNode(span);
      selection.removeAllRanges();

      this.textArea.value = transformFromLeiden(this.displayArea.childNodes);
      this.updateTokensFromText()
    });

    const buttonsDiv = document.createElement('div');
    this._node.append(buttonsDiv);

    this.untagId = getNextFreeUntagId();
    const newUntaggedEntityButton = createButton('Add untagged entity', {
      id: 'new-untagged-button', type: 'button', class: 'progressive'
    });

    newUntaggedEntityButton.addEventListener('click', _ => {
      const label = prompt('Please enter a tag label.');
      if (!label) return;
      this.addUntaggedToken(label);
    });

    buttonsDiv.append(tagButton, newUntaggedEntityButton);

    this.taggedEntitiesPool = new Pool();
    this.untaggedEntitiesPool = new Pool();

    this.deleteDropZone = new DeleteDropZone(env);
    this._node.append(
      createSpan('Tagged entity tokens'), this.taggedEntitiesPool.node,
      createSpan('Untagged entity tokens'), this.untaggedEntitiesPool.node,
      this.deleteDropZone.node
    );
  }

  addUntaggedToken(label) {
    const token = new Token(Token.UNTAGGED, this.untagId.toString(), `u${this.untagId}`, label);
    this.untaggedEntitiesPool.add(token);
    this.untagId++;
    return token;
  }

  aggregate() {
    return {
      taggedEntities: this.taggedEntitiesPool.aggregate(),
      untaggedEntities: this.untaggedEntitiesPool.aggregate()
    };
  }

  updateTokensFromText() {
    const parser = new DOMParser();
    const doc = parser.parseFromString(`<xml>${this.textArea.value}</xml>`, 'application/xml');
    const wTags = doc.querySelectorAll('w');

    for (const wTag of wTags) {
      const tagId = wTag.getAttribute('id');
      if (tagId.length === 0) continue;
      if (this.taggedEntitiesPool.has(tagId)) {
        this.taggedEntitiesPool.get(tagId).text = wTag.textContent;
      } else {
        this.taggedEntitiesPool.add(new Token(Token.TAGGED, tagId, `t${tagId}`, wTag.textContent));
      }
    }
  }

  /**
   *
   * @param {string} tokenId
   * @return {Token}
   */
  getToken(tokenId) {
    const type = tokenId.charAt(0);
    const id = tokenId.slice(1);

    switch (type) {
      case "u":
        return this.untaggedEntitiesPool.get(id);
      case "t":
        return this.taggedEntitiesPool.get(id);
      default:
        throw new Error(`Unknown token type: ${type}!`);
    }
  }
}