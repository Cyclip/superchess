const errorSound = new Audio("/static/audio/error.ogg");

class Board {
    constructor() {
        this.board = document.getElementById("board");
        this.newSSID();

        this.legalMovesCells = []; // legal moves
        this.selectedPiece = null; // selected piece
        this.lastMovedPositions = []; // last moved piece
        this.gameOver = true;

        // sounds
        this.moveSound = new Audio("/static/audio/move.mp3");
        this.captureSound = new Audio("/static/audio/capture.mp3");
        this.gameStartSound = new Audio("/static/audio/game_start.ogg");
        this.gameEndSound = new Audio("/static/audio/game_end.ogg");

        this.toPlay = "W"; // colour to play
        this.gameType = window.location.pathname.split("/")[2]; // game type (local, bot)
    }

    newSSID() {
        this.ssid = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
    }

    onOpen(event) {
        console.log("Connection established");
        // request board
        this.sendMessage({
            "type": "request_board",
            "ssid": this.ssid,
            "data": {}
        });
    }

    deletePiece(pos) {
        let piece = this.getPiece(pos);
        piece.parentNode.removeChild(piece);
    }

    async movePieceOnBoard(from, to, piece) {
        console.log("Moving piece", from, to, piece);
        // delete piece from old cell
        this.deletePiece(from);

        let isCapture = false;

        // delete children from new cell, if any
        let row = this.board.children[to[0]];
        let cell = row.children[to[1]];
        while (cell.firstChild) {
            cell.removeChild(cell.firstChild);
            isCapture = true;
        }

        // create new piece in new cell
        this.newPiece(piece.key, piece.colour, to);

        // delete highlights
        this.clearLegalMoves();

        this.setLastMovedPositions(from, to);

        // play sound
        if (isCapture) {
            await this.captureSound.play();
        } else {
            await this.moveSound.play();
        }

        this.onPieceMoved();
    }

    onPieceMoved() {
        // change turn
        this.switchToPlay();
        
        // if the game is bot, request bot to move
        if (this.gameType == "bot" && this.toPlay == "B") {
            socket.emit("bot_move", {
                "ssid": this.ssid
            })
        }
    }

    setLastMovedPositions(from, to) {
        console.log("Setting last moved positions", from, to)
        // remove old highlights
        this.setCellClasses(this.lastMovedPositions, "");

        // set new highlights
        this.lastMovedPositions = [from, to];

        // highlight last moved positions
        this.setCellClass(from, "last-moved-primary");
        this.setCellClass(to, "last-moved-secondary");
    }

    setCellClasses(positions, className) {
        for (let i = 0; i < positions.length; i++) {
            this.setCellClass(positions[i], className);
        }
    }

    setCellClass(pos, className) {
        let row = this.board.children[pos[0]];
        let cell = row.children[pos[1]];

        // not allowing multiple classes beyond cell
        cell.className = "cell " + className;
    }

    createBoard(data) {
        // create board (16 cols, 10 rows)
        for (let i = 0; i < 10; i++) {
            let row = document.createElement("div");
            row.classList.add("row");
            for (let j = 0; j < 16; j++) {
                let cell = document.createElement("div");
                cell.classList.add("cell");
                cell.addEventListener("click", onCellClick);
                cell.addEventListener("mouseover", onCellHover);
                cell.addEventListener("mouseleave", onCellLeave);
                row.appendChild(cell);
            }
            this.board.appendChild(row);
        }

        /* 
        Example output:
        {
            "W": [
                {
                    "type": "K",
                    "pos": [0, 4]
                },
                {
                    "type": "Q",
                    "pos": [0, 3]
                },
                ...
            ],
            "B": [
                {
                    "type": "K",
                    "pos": [7, 4]
                },
                {
                    "type": "Q",
                    "pos": [7, 3]
                },
                ...
            ]
        }
        */

        let white = data["W"];
        let black = data["B"];

        // place white pieces
        for (let i = 0; i < white.length; i++) {
            this.newPiece(white[i].type, "white", white[i].pos)
        }

        // place black pieces
        for (let i = 0; i < black.length; i++) {
            this.newPiece(black[i].type, "black", black[i].pos)
        }

        // game has started
        this.gameStartSound.play();
    }

    newPiece(type, color, pos) {
        let piece = document.createElement("div");
        piece.classList.add("piece");
        piece.classList.add(color);
        piece.classList.add(type);
        piece.addEventListener("click", onPieceClick);
        let row = this.board.children[pos[0]];
        let cell = row.children[pos[1]];
        cell.appendChild(piece);
    }

    getPiece(pos) {
        let row = this.board.children[pos[0]];
        let cell = row.children[pos[1]];

        // get piece from cell
        return cell.children[0];
    }

    getCell(pos) {
        let row = this.board.children[pos[0]];
        let cell = row.children[pos[1]];

        return cell;
    }

    getPiecePos(piece) {
        let cell = piece.parentNode;
        return this.getCellPos(cell);
    }

    getCellPos(cell) {
        let row = cell.parentNode;

        // which number is the cell in its parent row
        let index = Array.prototype.indexOf.call(row.children, cell);

        // which number is the row in its parent board
        let row_index = Array.prototype.indexOf.call(row.parentNode.children, row);

        // position of the cell
        return [row_index, index];
    }

    isLastMoved(pos) {
        for (let i = 0; i < this.lastMovedPositions.length; i++) {
            if (this.lastMovedPositions[i][0] == pos[0] && this.lastMovedPositions[i][1] == pos[1]) {
                return true;
            }
        }
        return false;
    }

    isLegalMoveHighlighted(pos) {
        // no references
        for (let i = 0; i < this.legalMovesCells.length; i++) {
            if (this.legalMovesCells[i][0] == pos[0] && this.legalMovesCells[i][1] == pos[1]) {
                return true;
            }
        }
        return false;
    }

    movePiece(cellPos) {
        // all game mechanics will be handled by the server
        let piecePos = this.getPiecePos(this.selectedPiece);
        
        // from (piecePos) to (cellPos) must be different
        if (piecePos[0] != cellPos[0] || piecePos[1] != cellPos[1]) {
            socket.emit("move_piece", {
                "ssid": this.ssid,
                "from": piecePos,
                "to": cellPos
            });
        }
    }

    cellHasPiece(cell) {
        return cell.children.length > 0;
    }

    activateCellLabels(pos) {
        document.getElementById("col-labels").classList.add("dim");
        document.getElementById("row-labels").classList.add("dim");

        document.getElementById("col-labels").children[pos[1]].classList.add("active");
        document.getElementById("row-labels").children[pos[0]].classList.add("active");
    }

    deactivateCellLabels(pos) {
        document.getElementById("col-labels").classList.remove("dim");
        document.getElementById("row-labels").classList.remove("dim");

        document.getElementById("col-labels").children[pos[1]].classList.remove("active");
        document.getElementById("row-labels").children[pos[0]].classList.remove("active");
    }

    clearLegalMoves() {
        // clear all legal moves if they are not highlighted
        for (let i = 0; i < this.legalMovesCells.length; i++) {
            if (!this.isLastMoved(this.legalMovesCells[i])) {
                let cell = this.getCell(this.legalMovesCells[i]);
                cell.classList.remove("legal-move");
            }
        }
    }

    pieceInfo(piece) {
        let colour;
        if (piece.classList[1] == "white") {
            colour = "W";
        } else {
            colour = "B";
        }

        let info = {
            "type": piece.classList[2],
            "colour": colour,
        }
        return info;
    }

    canClickPiece(piece) {
        let info = this.pieceInfo(piece);
        if (info.colour == this.toPlay) {
            return true;
        }
        return false;
    }

    switchToPlay() {
        if (this.toPlay == "W") {
            this.toPlay = "B";
        } else {
            this.toPlay = "W";
        }
    }

    endGame(outcome) {
        this.gameOver = true;
        this.setWinner(outcome.winner);
        openOutcomeMenu();
        this.gameEndSound.play();
    }

    setWinner(winner) {
        let outcomeName = document.getElementById("outcome-name");
        let outcomeIconW = document.getElementById("outcome-icon-w");
        let outcomeIconB = document.getElementById("outcome-icon-b");

        if (winner == "W") {
            outcomeName.innerHTML = "White wins!";
            outcomeIconW.classList.add("active");
            outcomeIconB.classList.remove("active");
        } else {
            outcomeName.innerHTML = "Black wins!";
            outcomeIconW.classList.remove("active");
            outcomeIconB.classList.add("active");
        }
    }

    clearBoard() {
        this.board.innerHTML = "";

        // request board again
        socket.emit("get_board", {
            "ssid": this.ssid
        });
    }

    setEvaluation(evaluation) {
        let whiteFill = document.getElementById("evaluation-white-fill");
        let whiteText = document.getElementById("evaluation-text-w");
        let blackText = document.getElementById("evaluation-text-b");

        if (evaluation == 9999999999) {
            // checkmate (white)
            whiteFill.style.height = "100%";
            whiteText.innerHTML = "M";
            whiteText.classList.remove("hidden");
            blackText.classList.add("hidden");
        } else if (evaluation == -9999999999) {
            // checkmate (black)
            whiteFill.style.height = "0%";
            blackText.innerHTML = "M";
            whiteText.classList.add("hidden");
            blackText.classList.remove("hidden");
        } else {
            evaluation = evaluation * 0.1;
            let displayEval = Math.round(evaluation * 10) / 10;

            let evalPerc = sigmoid(evaluation * 0.1) * 100;
            whiteFill.style.height = evalPerc + "%";

            if (evaluation >= 0) {
                whiteText.innerHTML = displayEval;
                whiteText.classList.remove("hidden");
                blackText.classList.add("hidden");
            } else {
                blackText.innerHTML = -displayEval;
                whiteText.classList.add("hidden");
                blackText.classList.remove("hidden");
            }
        }
    }
}

function sigmoid(x) {
    return 1 / (1 + Math.exp(-x));
}

function onCellHover(event) {
    let target = event.target;

    if (target.classList.contains("piece")) {
        target = target.parentNode;
    }

    // get position
    let pos = chessBoard.getCellPos(target);
    chessBoard.activateCellLabels(pos);
}

function onCellLeave(event) {
    let target = event.target;

    if (target.classList.contains("piece")) {
        target = target.parentNode;
    }

    // get position
    let pos = chessBoard.getCellPos(target);
    chessBoard.deactivateCellLabels(pos);
}

function onCellClick(event) {
    if (!chessBoard.gameOver) {
        let cell = event.target;
        // if target is piece, get parent cell
        if (cell.classList.contains("piece")) {
            cell = cell.parentNode;
        }
        
        // get position
        let pos = chessBoard.getCellPos(cell);

        // is it highlighted?
        if (chessBoard.isLegalMoveHighlighted(pos) && chessBoard.selectedPiece != null) {
            // move piece
            console.log("[onCellClick] moving piece from " + chessBoard.getPiecePos(chessBoard.selectedPiece) + " to " + pos);
            chessBoard.movePiece(pos);
        } else if (!chessBoard.cellHasPiece(cell) && chessBoard.selectedPiece != null) {
            // if no piece, deselect
            chessBoard.selectedPiece = null;
            chessBoard.clearLegalMoves();
        }
    }
}

function onPieceClick(event) {
    if (!chessBoard.gameOver) {
        let piece = event.target;
        let info = chessBoard.pieceInfo(piece);
        
        if (info['colour'] == chessBoard.toPlay) {
            let pos = chessBoard.getPiecePos(piece);
            chessBoard.selectedPiece = piece;

            // get legal moves
            socket.emit("get_legal_moves", {
                "ssid": chessBoard.ssid,
                "pos": pos
            });
        }
    }
}

// outcome functions
const outcome_menu = document.getElementById("outcome");

function playLocal() {
    window.history.pushState("", "", "/play/local");
    chessBoard.clearBoard();
    chessBoard.gameType = "local";
    chessBoard.toPlay = "W";
    chessBoard.gameOver = false;
    chessBoard.newSSID();
    socket.emit("request_board", {"ssid": chessBoard.ssid});
    closeOutcomeMenu();
}

function playBot() {
    window.history.pushState("", "", "/play/bot");
    chessBoard.clearBoard();
    chessBoard.gameType = "bot";
    chessBoard.toPlay = "W";
    chessBoard.gameOver = false;
    chessBoard.newSSID();
    socket.emit("request_board", {"ssid": chessBoard.ssid});
    closeOutcomeMenu();
}

function closeOutcomeMenu() {
    // fade out
    outcome_menu.classList.add("fadeout");
    setTimeout(function() {
        outcome_menu.classList.remove("fadeout");
        outcome_menu.classList.add("hidden");
    }, 500);
}

function openOutcomeMenu() {
    outcome_menu.classList.remove("hidden");
    outcome_menu.classList.add("fadein");
    setTimeout(function() {
        outcome_menu.classList.remove("fadein");
    }, 500);
}

// error handling
function showError(err) {
    let board_cover = document.getElementById("board-cover");
    let text = document.getElementById("board-cover-text-p");

    text.innerHTML = err;
    board_cover.classList.remove("hidden");
    errorSound.play();
}

function hideError() {
    let board_cover = document.getElementById("board-cover");
    board_cover.classList.add("hidden");
}

let chessBoard = new Board();

// Connections
const socket = io();
console.log("Connecting to server", socket);

socket.on("connect", function() {
    console.log("connected to server, requesting board..");
    if (chessBoard.gameOver) {
        // request board
        socket.emit("request_board", {
            "ssid": chessBoard.ssid
        });
        hideError();
    } else {
        console.error("Game not over, cannot request board");
        showError("Game not over, cannot request board");
    }
});

socket.on("disconnect", function() {
    console.log("disconnected from server");
    chessBoard.gameOver = true;
    showError("Unexpectedly disconnected from server.");
});

socket.on("error", function(err) {
    console.error("error", err);
    showError(err);
});

socket.on("board", function(data) {
    console.log("received board", data);
    chessBoard.gameOver = false;
    chessBoard.clearBoard();
    chessBoard.createBoard(data);
});

socket.on("legal_moves", function(data) {
    console.log("received legal moves", data);
    let positions = data;
    chessBoard.clearLegalMoves();
    chessBoard.legalMovesCells = positions;
    chessBoard.setCellClasses(positions, "legal-move");
});

socket.on("move_piece", function(data) {
    console.log("received move_piece", data);
    let from = data.from;
    let to = data.to;
    let piece = data.piece;

    if (chessBoard.toPlay == "B") {
        setTimeout(function() {
            // instant is too fast
            chessBoard.movePieceOnBoard(from, to, piece);
        }, 500);
    } else {
        chessBoard.movePieceOnBoard(from, to, piece);
    }
});

socket.on("game_over", function(data) {
    console.log("game over, outcome:", data);
    let outcome = data.outcome;

    setTimeout(function() {
        chessBoard.endGame(outcome);
    }, 750);
});

socket.on("evaluation", function(data) {
    console.log("received evaluation", data);
    let evaluation = data.evaluation;
    let colour = data.colour;

    chessBoard.setEvaluation(evaluation, colour);
})