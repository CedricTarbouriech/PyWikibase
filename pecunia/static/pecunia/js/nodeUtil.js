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
  return  createNode('input', params);
}

export function createCollapsible(label, content) {
  const button = createButton(label, {
    type: 'button',
    class: 'collapsible'
  });
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