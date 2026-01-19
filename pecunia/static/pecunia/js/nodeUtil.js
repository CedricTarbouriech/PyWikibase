function createNode(type, params) {
  const node = document.createElement(type);
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      node.setAttribute(key, value);
    }
  }
  return node;
}

export function createDiv(params) {
  return createNode('div', params);
}

/**
 *
 * @param text
 * @param params
 * @returns {HTMLButtonElement}
 */
export function createButton(text, params) {
  const button = createNode('button', params);
  button.textContent = text;
  return button;
}

export function createSpan(text, params) {
  const span = createNode('span', params);
  span.textContent = text;
  return span;
}

export function createInput(params) {
  return createNode('input', params);
}

export function createSelect(labels) {
  const select = document.createElement('select');

  for (const label of labels) {
    const option = document.createElement('option');
    option.textContent = label;
    select.append(option);
  }

  return select;
}

export function createLabel(value, params) {
  const label = createNode('label', params);
  label.textContent = value;
  return label;
}

export function createCollapsible(label, content) {
  const button = createButton('', {
    type: 'button',
    class: 'collapsible neutral'
  });

  button.append(createSpan(label));

  button.append(createSpan('', {class: 'icon'}));
  button.addEventListener('click', _ => {
    button.classList.toggle("active");
    if (content.style.display === "none") {
      content.style.display = "block";
    } else {
      content.style.display = "none";
    }
  });
  content.classList.add("content");

  return [button, content];
}

/**
 *
 * @param {string} type
 * @param {Component} removedComponent
 * @returns {HTMLButtonElement}
 */
export function createDeleteButton(type, removedComponent) {
  const deleteButton = createButton('X', {
    type: 'button',
    style: 'margin-right: 10px',
    class: 'destructive'
  });

  deleteButton.addEventListener('click', _ => {
    const confirmed = window.confirm("Are you sure?");
    if (!confirmed) return;

    removedComponent.node.dispatchEvent(new CustomEvent(`${type}removed`, {
      bubbles: true,
      detail: {removed: removedComponent}
    }));
    removedComponent.node.remove();
  });
  return deleteButton;
}

export function deleteListener(event, list) {
  const link = event.detail.removed;
  const index = list.indexOf(link);
  if (index > -1)
    list.splice(index, 1);
}

export class Component {
  constructor(node) {
    if (node) {
      this._node = node;
    }
  }

  /**
   *
   * @returns {HTMLElement}
   */
  get node() {
    return this._node;
  }
}

export class GroupComponent extends Component {
  /**
   * @param {DragAndDropEnv} env
   * @param {HTMLElement} node
   * @param {string} newButtonLabel
   * @param {typeof Component} ComponentSubClass
   * @param {string} componentName
   * @param {(item: Component) => boolean} filter
   */
  constructor(env, node, newButtonLabel, ComponentSubClass, componentName, filter = (_ => true)) {
    super(node);
    this.group = [];
    this.filter = filter;

    const newButton = createButton(newButtonLabel, {
      type: 'button',
      class: 'progressive'
    });

    newButton.addEventListener('click', () => {
      const item = new ComponentSubClass(env);
      this.group.push(item);
      newButton.before(item.node);
    });

    this.node.addEventListener(`${componentName}removed`, event => deleteListener(event, this.group));
    this.node.append(newButton);
  }

  aggregate() {
    return this.group.filter(this.filter).map(item => item.aggregate());
  }
}

export class GroupItemComponent extends Component {
  constructor(node, componentName) {
    super(node);
    this.node.append(createDeleteButton(componentName, this));
  }
}

export class CollapsibleGroupItemComponent extends Component {
  constructor(node, componentName, div) {
    super(node);

    const deleteButton = createDeleteButton(componentName, this);
    const [collapseButton, content] = createCollapsible('', div);
    this.collapseButton = collapseButton;
    const buttons = createDiv({class: 'delete-and-collapse-buttons'});
    buttons.append(deleteButton, collapseButton);
    this.node.append(buttons, content);
  }
}