import {Component, createDiv} from "../nodeUtil.js";
import {getAsJson} from "../api.js";

class StatementGroup extends Component {
  constructor(property, statements) {
    super(createDiv());
    this.node.append(property);

    for (const statement of statements) {
      this.node.append(`${statement['rank']} - ${statement['mainsnak']}`)
    }
  }
}

class Application extends Component {
  constructor(id) {
    super(document.getElementById(id));

  }

  async start(itemId) {
    const items = await getAsJson(
      `/api/items/${itemId}/?fields=labels,descriptions,claims`,
      `Unable to search items for e.`
    );

    console.log(items);
    for (const [property, statements] of Object.entries(items['claims'])) {
      this.node.append(new StatementGroup(property, statements).node);
      console.log(property, statements)
    }


  }
}

document.addEventListener('DOMContentLoaded', async () => {
  const app = new Application('app-statement');
  const itemId = app.node.getAttribute('data-item-id');
  await app.start(itemId)
});