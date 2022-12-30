class Board {
    constructor() {
        this.board = document.getElementById("board");
        this.connection = new WebSocket("ws://localhost:5000/board");
        this.connection.onopen = this.onOpen.bind(this);
        this.connection.onmessage = this.onMessage.bind(this);
        this.ssid = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);

        this.legalMovesCells = []; // legal moves
        this.selectedPiece = null; // selected piece
        this.lastMovedPositions = []; // last moved piece

        // sounds
        this.moveSound = new Audio("/static/audio/move.mp3");
        this.captureSound = new Audio("/static/audio/capture.mp3");

        this.toPlay = "W"; // colour to play
        this.gameType = window.location.pathname.split("/")[2]; // game type (local, bot)
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

    sendMessage(message) {
        this.connection.send(
            JSON.stringify(message)
        );
    }

    readMessage(message) {
        return JSON.parse(message);
    }

    onMessage(event) {
        let msg = this.readMessage(event.data);
        console.log("Received", msg);
        switch (msg.type) {
            case "board":
                this.createBoard(msg.data);
                break;
            case "legal_moves":
                // highlight legal moves
                let positions = msg.data;

                // remove old highlights
                this.clearLegalMoves();
                this.legalMovesCells = positions;
                this.setCellClasses(positions, "legal-move");
                break;
            case "move_piece":
                // move piece
                let from = msg.data.from;
                let to = msg.data.to;
                let piece = msg.data.piece;

                this.movePieceOnBoard(from, to, piece);
        }
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
            this.sendMessage({
                "type": "bot_move",
                "ssid": this.ssid,
                "data": {}
            });
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

        console.log("Setting cell class", pos, className);
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
            this.sendMessage({
                "type": "move_piece",
                "ssid": this.ssid,
                "data": {
                    "from": piecePos,
                    "to": cellPos
                }
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
}

function onCellHover(event) {
    console.log("cell hover", event.target);
    let target = event.target;

    if (target.classList.contains("piece")) {
        target = target.parentNode;
    }

    // get position
    let pos = board.getCellPos(target);
    board.activateCellLabels(pos);
}

function onCellLeave(event) {
    console.log("cell leave", event.target);
    let target = event.target;

    if (target.classList.contains("piece")) {
        target = target.parentNode;
    }

    // get position
    let pos = board.getCellPos(target);
    board.deactivateCellLabels(pos);
}

function onCellClick(event) {
    let cell = event.target;
    // if target is piece, get parent cell
    if (cell.classList.contains("piece")) {
        cell = cell.parentNode;
    }
    
    // get position
    let pos = board.getCellPos(cell);

    // is it highlighted?
    if (board.isLegalMoveHighlighted(pos) && board.selectedPiece != null) {
        // move piece
        console.log("[onCellClick] moving piece from " + board.getPiecePos(board.selectedPiece) + " to " + pos);
        board.movePiece(pos);
    } else if (!board.cellHasPiece(cell) && board.selectedPiece != null) {
        // if no piece, deselect
        board.selectedPiece = null;
        board.clearLegalMoves();
    }
}

function onPieceClick(event) {
    let piece = event.target;
    let info = board.pieceInfo(piece);
    
    if (info['colour'] == board.toPlay) {
        let pos = board.getPiecePos(piece);
        board.selectedPiece = piece;

        // get legal moves
        board.sendMessage({
            "type": "get_legal_moves",
            "ssid": board.ssid,
            "data": {
                "pos": pos
            }
        });
    }
}

let board = new Board();