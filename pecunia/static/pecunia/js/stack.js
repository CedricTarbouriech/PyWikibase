'use strict';

export class EmptyStackError extends Error {
  constructor() {
    super("Stack is empty");
    this.name = "EmptyStackError";
  }
}

export class Stack {
  constructor() {
    this.items = [];
  }

  /**
   * Push the element onto the stack.
   * @param {object} element
   */
  push(element) {
    this.items.push(element);
  }

  /**
   * Pop the top element from the stack.
   * @throws {EmptyStackError} if the stack is empty.
   * @returns {object} The popped element.
   */
  pop() {
    if (this.isEmpty()) throw new EmptyStackError();
    return this.items.pop();
  }

  /**
   * @throws {EmptyStackError} if the stack is empty.
   * @returns {object} the top element.
   */
  top() {
    if (this.isEmpty()) throw "Stack is empty";
    return this.items[this.size() - 1];
  }

  /**
   * @returns {boolean} `true` if the stack is empty; `false` otherwise.
   */
  isEmpty() {
    return this.items.length === 0;
  }

  /**
   * @returns {number} the number of elements in the stack.
   */
  size() {
    return this.items.length;
  }
}
