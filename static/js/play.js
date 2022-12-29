class Board {
    constructor() {
        this.board = document.getElementById("board");
        this.connection = new WebSocket("ws://localhost:5000/board");
        this.connection.onopen = this.onOpen.bind(this);
        this.connection.onmessage = this.onMessage.bind(this);
        this.ssid = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);

        this.highlightedCell = []; // legal moves
        this.selectedPiece = null; // selected piece
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
        console.log(msg);
        switch (msg.type) {
            case "board":
                this.createBoard(msg.data);
                break;
            case "legal_moves":
                // highlight legal moves
                let positions = msg.data;

                // remove old highlights
                this.setCellClasses(this.highlightedCell, "");
                this.highlightedCell = positions;

                for (let i = 0; i < positions.length; i++) {
                    this.setCellClass(positions[i], "legal-move");
                }
                break;
            case "move_piece":
                // move piece
                let from = msg.data.from;
                let to = msg.data.to;
                let piece = msg.data.piece;

                this.movePiece(from, to, piece);
        }
    }

    deletePiece(pos) {
        let piece = this.getPiece(pos);
        piece.parentNode.removeChild(piece);
    }

    movePiece(from, to, piece) {
        // delete piece from old cell
        this.deletePiece(from);

        // create new piece in new cell
        this.newPiece(piece.type, piece.color, to);
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
        console.log(data);
        // create 16x16 board
        for (let i = 0; i < 16; i++) {
            let row = document.createElement("div");
            row.classList.add("row");
            for (let j = 0; j < 16; j++) {
                let cell = document.createElement("div");
                cell.classList.add("cell");
                cell.addEventListener("click", onCellClick);
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
        let row = cell.parentNode;

        // which number is the piece in its parent row
        let index = Array.prototype.indexOf.call(row.children, cell);

        // which number is the row in its parent board
        let row_index = Array.prototype.indexOf.call(row.parentNode.children, row);

        // position of the piece
        return [row_index, index];
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

    isHighlighted(pos) {
        // no references
        for (let i = 0; i < this.highlightedCell.length; i++) {
            if (this.highlightedCell[i][0] == pos[0] && this.highlightedCell[i][1] == pos[1]) {
                return true;
            }
        }
        return false;
    }

    movePiece(cellPos) {
        // all game mechanics will be handled by the server
        let piecePos = this.getPiecePos(this.selectedPiece);
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

function onCellClick(event) {
    let cell = event.target;
    
    // get position
    let pos = board.getCellPos(cell);

    // is it highlighted?
    if (board.isHighlighted(pos)) {
        // move piece
        console.log("moving piece from " + board.getPiecePos(board.selectedPiece) + " to " + pos);
        board.movePiece(pos);
    }
}

function onPieceClick(event) {
    let piece = event.target;
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

let board = new Board();