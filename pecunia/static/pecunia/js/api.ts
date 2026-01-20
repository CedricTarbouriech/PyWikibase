'use strict';

/**
 * Fetch JSON data from the specified URL using a GET request.
 * Throws an error with the provided message if the response is not successful.
 * @param {string} url The endpoint to fetch data from.
 * @param {string} errorMessage The error message to throw if the request fails.
 * @returns {Promise<any>} The parsed JSON response from the server.
 */
async function getAsJson(
    url: string,
    errorMessage: string
): Promise<any> {
    const response = await fetch(url);
    if (!response.ok) throw new Error(errorMessage)
    return await response.json();
}

/**
 * Retrieves a CSRF token from the page.
 * Throws an error if no token is found.
 * @returns {string} a CSRF token.
 */
function getCSRFTokenFromDocument(): string {
    const inputWithCSRF = document.querySelector<HTMLInputElement>('[name=csrfmiddlewaretoken]');
    if (!inputWithCSRF)
        throw new Error('No CSRF token available!');
    return inputWithCSRF.value;
}

/**
 * Send JSON data to the specified URL using a POST request.
 * Throws an error with the provided message if the response is not successful.
 * @param {string} url The endpoint to send data to.
 * @param {string} errorMessage The error message to throw if the request fails.
 * @param {any} data The data to be sent as the request body.
 * @returns {Promise<any>} The parsed JSON response from the server.
 */
async function postAsJson(
    url: string,
    errorMessage: string,
    data: any
): Promise<any> {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFTokenFromDocument()
        },
        body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error(errorMessage);
    return await response.json();
}

async function putAsJson(
    url: string,
    errorMessage: string,
    data: any
): Promise<any> {
    const response = await fetch(url, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFTokenFromDocument()
        },
        body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error(errorMessage);
    return await response.json();
}

async function deleteAsJson(
    url: string,
    errorMessage: string,
    data: any
): Promise<any> {
    const response = await fetch(url, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFTokenFromDocument()
        },
        body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error(errorMessage);
    return await response.json();
}

async function fetchPropertyDataType(
    propertyId: string
) {
    const data = await getAsJson(`/api/properties/${propertyId}`, `Impossible de charger les données de la propriété ${propertyId}.`);
    return data.type;
}

/**
 *
 * @param {number} snakType
 * @param rank
 * @param propertyId
 * @param entityId
 * @param value
 * @returns {Promise<{updatedHtml: string}>}
 */
async function createStatement(
    snakType: number,
    rank: any,
    propertyId: any,
    entityId: any,
    value: any
) {
    return await postAsJson('/api/statements/', 'Erreur lors de l’ajout d’un statement.', {
        snak_type: snakType,
        prop_id: propertyId,
        entity_id: entityId,
        rank: rank,
        value: value
    });
}

/**
 *
 * @param {number} statementId
 * @param {number} propertyId
 * @param value
 * @returns {Promise<{updatedHtml: string}>}
 */
async function createQualifier(
    statementId: number,
    propertyId: number,
    value: any
) {
    console.log(statementId, propertyId, value);
    return await postAsJson('/api/qualifiers/', 'Erreur lors de l’ajout d’un qualifier.', {
        statement_id: statementId,
        prop_id: propertyId,
        value: value
    });
}

/**
 *
 * @param {number} statementId
 * @param rank
 * @param snakType
 * @param value
 * @returns {Promise<{updatedHtml: string}>}
 */
async function updateStatement(
    statementId: number,
    rank: any,
    snakType: any,
    value: any
) {
    return await putAsJson('/api/statements/', 'Erreur dans la mise à jour du statement.', {
        statement_id: statementId,
        rank: rank,
        snak_type: snakType,
        value: value
    });
}