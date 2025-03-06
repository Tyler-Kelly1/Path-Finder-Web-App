"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
// app.ts — Generate a grid and add it to the HTML
let size = 10;
const gridContainer = document.getElementById('mainCont');
const grid = document.getElementById("grid");
function checkForErrors() {
    const grid = gridTo2DArray();
    let errors = [];
    let errorFound = false;
    let playerCount = 0;
    let goalCount = 0;
    //Check for player and error placement
    for (let i = 0; i < grid.length; i++) {
        for (let j = 0; j < grid[i].length; j++) {
            //Check for player
            if (grid[i][j] == "rgb(0, 96, 0)") {
                playerCount += 1;
            }
            if (grid[i][j] == "rgb(255, 215, 0)") {
                goalCount += 1;
            }
        }
    }
    if (playerCount == 0) {
        errors.push("You must place a start!");
        errorFound = true;
    }
    if (goalCount == 0) {
        errors.push("You must place a goal!");
        errorFound = true;
    }
    if (playerCount > 1) {
        errors.push("You must place only 1 start!");
        errorFound = true;
    }
    if (goalCount > 1) {
        errors.push("You must place only 1 goal!");
        errorFound = true;
    }
    return [errorFound, errors];
}
function setSize(element) {
    const value = parseInt(element.value);
    console.log(value);
    size = value;
    const gridContainer = document.getElementById('grid');
    const mainContainter = document.getElementById("mainCont");
    while (gridContainer === null || gridContainer === void 0 ? void 0 : gridContainer.firstChild) {
        gridContainer.removeChild(gridContainer.firstChild);
    }
    createGrid(value);
}
function createGrid(size) {
    const gridContainer = document.getElementById('grid');
    const mainContainter = document.getElementById("mainCont");
    if (!gridContainer) {
        console.log("HELP ME");
        return;
    }
    gridContainer.style.display = 'grid';
    gridContainer.style.gridTemplateRows = `repeat(${size}, 1fr)`;
    gridContainer.style.gridTemplateColumns = `repeat(${size}, 1fr)`;
    for (let r = 0; r < size; r++) {
        for (let c = 0; c < size; c++) {
            const cell = document.createElement('div');
            cell.className = 'grid-cell';
            cell.dataset.row = r.toString();
            cell.dataset.col = c.toString();
            cell.addEventListener('click', () => handleCellClick(cell));
            gridContainer.appendChild(cell);
        }
    }
    gridContainer.classList.add("grid");
    mainContainter === null || mainContainter === void 0 ? void 0 : mainContainter.appendChild(gridContainer);
}
let mode = 0;
function clearCells() {
    const cells = document.querySelectorAll('.grid-cell');
    cells.forEach((cell) => {
        // Example action: Changing the background color
        cell.classList.remove("block");
        cell.classList.remove("start");
        cell.classList.remove("goal");
        cell.classList.remove("path");
    });
}
function setMode(input) {
    switch (input) {
        case 1:
            mode = 1;
            break;
        case 2:
            mode = 2;
            break;
        case 3:
            mode = 3;
            break;
        case 4:
            mode = 4;
    }
}
function handleCellClick(cell) {
    switch (mode) {
        case 1:
            cell.classList.remove("block");
            cell.classList.remove("start");
            cell.classList.remove("goal");
            cell.classList.remove("path");
            break;
        case 2:
            cell.classList.add("block");
            cell.classList.remove("start");
            cell.classList.remove("goal");
            cell.classList.remove("path");
            break;
        case 3:
            cell.classList.add("start");
            cell.classList.remove("remove");
            cell.classList.remove("goal");
            cell.classList.remove("path");
            break;
        case 4:
            cell.classList.add("goal");
            cell.classList.remove("remove");
            cell.classList.remove("start");
    }
}
// Example: Converting grid cells into a 2D array
// Function to convert grid to a 2D array
function gridTo2DArray() {
    const gridArray = [];
    const cells = document.querySelectorAll('.grid-cell');
    let row = [];
    cells.forEach((cell, index) => {
        const cellStyle = getComputedStyle(cell); // Example value from cell
        const cellColor = cellStyle.backgroundColor;
        row.push(cellColor);
        // Once a row is complete, push it into the gridArray
        if ((index + 1) % size === 0) {
            gridArray.push(row);
            row = []; // Reset for next row
        }
    });
    console.log(gridArray);
    return gridArray;
}
function getGridFromBackend() {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            const userID = "thinking";
            const url = `http://127.0.0.1:8000/api/getGrid/${userID}`;
            const response = yield fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = yield response.json();
            const grid = data.grid; // Grab the "grid" field
            renderBoard(grid);
        }
        catch (error) {
            console.error("Error fetching grid:", error);
        }
    });
}
function renderBoard(board) {
    const cells = document.querySelectorAll('.grid-cell');
    cells.forEach((cell, index) => {
        const row = Math.floor(index / board[0].length); // Calculate the row number
        const col = index % board[0].length; // Calculate the column number
        // Example action: Changing the background color
        cell.classList.remove("block");
        cell.classList.remove("start");
        cell.classList.remove("goal");
        cell.classList.remove("path");
        const tile = board[row][col];
        if (tile === "-") {
        }
        else if (tile === 'X') {
            cell.classList.add("block");
        }
        else if (tile === 'p') {
            cell.classList.add("start");
        }
        else if (tile === 'G') {
            cell.classList.add("goal");
        }
        else if (tile === 'O') {
            cell.classList.add("path");
        }
    });
}
window.onload = () => {
    const userID = "thinking";
    const url = `ws://127.0.0.1:8000/ws/${userID}`;
    console.log(url);
    const socket = new WebSocket(url);
    socket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data); // Parse the 2D array
            renderBoard(data);
        }
        catch (error) {
            console.error("Error parsing JSON:", error);
        }
    };
};
function displayErrors(errors) {
    let fullString = "";
    const errorText = document.getElementById("errorTextLine");
    for (let i = 0; i < errors.length; i++) {
        fullString = fullString + ("⚠️" + errors[i] + "⚠️" + "<br\>");
    }
    if (errorText) {
        errorText.innerHTML = fullString;
        errorText.classList.add('show');
        // Stay visible for 1 second, then fade out
        setTimeout(() => { errorText.classList.remove('show'); }, 3000); // 500ms fade in + 1000ms visible
    }
}
// Function to send the 2D array to the backend.
function sendGridToBackend() {
    return __awaiter(this, void 0, void 0, function* () {
        const message = gridTo2DArray(); // Get the 2D array from the grid
        let errorResults = checkForErrors();
        if (errorResults[0]) {
            for (let i = 0; i < errorResults[1].length; i++) {
                console.log(errorResults[1][i]);
            }
            displayErrors(errorResults[1]);
            return;
        }
        try {
            const response = yield fetch("http://127.0.0.1:8000/api/send", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ grid: message })
            });
        }
        catch (error) {
            console.error("Error:", error);
        }
        getGridFromBackend();
    });
}
document.addEventListener('DOMContentLoaded', () => {
    createGrid(size);
});
