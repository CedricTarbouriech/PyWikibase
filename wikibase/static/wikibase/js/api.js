'use strict';

/**
 * Fetch JSON data from the specified URL using a GET request.
 * Throws an error with the provided message if the response is not successful.
 * @param {string} url The endpoint to fetch data from.
 * @param {string} errorMessage The error message to throw if the request fails.
 * @returns {Promise<any>} The parsed JSON response from the server.
 *
 */
export async function getAsJson(url, errorMessage) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(errorMessage)
  return await response.json();
}

/**
 * Send JSON data to the specified URL using a POST request.
 * Throws an error with the provided message if the response is not successful.
 * @param {string} url The endpoint to send data to.
 * @param {string} errorMessage The error message to throw if the request fails.
 * @param {any} data The data to be sent as the request body.
 * @returns {Promise<any>} The parsed JSON response from the server.
 */
export async function postAsJson(url, errorMessage, data) {
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
    },
    body: JSON.stringify(data)
  });
  if (!response.ok) throw new Error(errorMessage);
  return await response.json();
}

export async function fetchPropertyDataType(propertyId) {
  const data = await getAsJson(`/api/property/${propertyId}`, `Impossible de charger les données de la propriété ${propertyId}.`);
  return data.type;
}

/**
 *
 * @param {int} snakType
 * @param rank
 * @param propertyId
 * @param entityId
 * @param value
 * @returns {Promise<{updatedHtml: string}>}
 */
export async function createStatement(snakType, rank, propertyId, entityId, value) {
  return await postAsJson('/api/statement/add', 'Erreur lors de l’ajout d’un statement.', {
    snak_type: snakType,
    prop_id: propertyId,
    entity_id: entityId,
    rank: rank,
    value: value
  });
}

/**
 *
 * @param {int} statementId
 * @param rank
 * @param snakType
 * @param value
 * @returns {Promise<{updatedHtml: string}>}
 */
export async function updateStatement(statementId, rank, snakType, value) {
  return await postAsJson('/api/statement/update', 'Erreur dans la mise à jour du statement.', {
    statement_id: statementId,
    rank: rank,
    snak_type: snakType,
    value: value
  });
}