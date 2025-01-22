/**
 * В этом файле лежат функции, которые помогают рисовать на Canvas
 * (разбиваем логику рисования по разным функциям).
 */

/**
 * Очищает canvas перед новым рисованием
 * @param {HTMLCanvasElement} canvas
 * @param {CanvasRenderingContext2D} ctx
 */
export function clearCanvas(canvas, ctx) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

/**
 * Рисует раскрашенные клетки
 * @param {CanvasRenderingContext2D} ctx
 * @param {Set<string>} coloredCells - Набор позиций вида "x,y"
 * @param {number} cellSize
 */
export function drawColoredCells(ctx, coloredCells, cellSize) {
    ctx.fillStyle = 'gray';
    coloredCells.forEach(cell => {
        const [x, y] = cell.split(',').map(Number);
        ctx.fillRect((x + 1) * cellSize, (y + 1) * cellSize, cellSize, cellSize);
    });
}

/**
 * Рисует робота (ромб) на холсте
 * @param {CanvasRenderingContext2D} ctx
 * @param {{x:number,y:number}} robotPos
 * @param {number} cellSize
 */
export function drawRobot(ctx, robotPos, cellSize) {
    const robotX = (robotPos.x + 1) * cellSize + cellSize / 2;
    const robotY = (robotPos.y + 1) * cellSize + cellSize / 2;
    const diamondSize = cellSize * 0.4 * 1.5; // 1.5x масштаб

    ctx.fillStyle = '#FF4500';
    ctx.beginPath();
    ctx.moveTo(robotX, robotY - diamondSize / 2);
    ctx.lineTo(robotX + diamondSize / 2, robotY);
    ctx.lineTo(robotX, robotY + diamondSize / 2);
    ctx.lineTo(robotX - diamondSize / 2, robotY);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
}

/**
 * Рисует маркеры (кружочки)
 * @param {CanvasRenderingContext2D} ctx
 * @param {Object} markers - Объект вида { "x,y": 1, ... }
 * @param {number} cellSize
 */

export function drawMarkers(ctx, markers, cellSize) {
    Object.keys(markers).forEach(key => {
        const [x, y] = key.split(',').map(Number);
        ctx.fillStyle = 'white';
        ctx.beginPath();
        ctx.arc(
            (x + 1.75) * cellSize,
            (y + 1.75) * cellSize,
            cellSize * 0.15,
            0,
            2 * Math.PI
        );
        ctx.fill();
        ctx.strokeStyle = 'black';
        ctx.lineWidth = 1;
        ctx.stroke();
    });
}

/**
 * Рисует набор стен (обычные или постоянные)
 * @param {CanvasRenderingContext2D} ctx
 * @param {Set<string>} walls - Строки вида "x1,y1,x2,y2"
 * @param {number} cellSize
 * @param {string} strokeStyle - цвет линии
 * @param {number} lineWidth - толщина линии
 */
export function drawWalls(ctx, walls, cellSize, strokeStyle, lineWidth) {
    ctx.strokeStyle = strokeStyle;
    ctx.lineWidth = lineWidth;
    walls.forEach(wall => {
        const [x1, y1, x2, y2] = wall.split(',').map(Number);
        ctx.beginPath();
        ctx.moveTo((x1 + 1) * cellSize, (y1 + 1) * cellSize);
        ctx.lineTo((x2 + 1) * cellSize, (y2 + 1) * cellSize);
        ctx.stroke();
    });
}

/**
 * Рисует сетку
 * @param {CanvasRenderingContext2D} ctx
 * @param {number} width - ширина поля
 * @param {number} height - высота поля
 * @param {number} cellSize
 */
export function drawGrid(ctx, width, height, cellSize) {
    ctx.strokeStyle = '#C8C80F';
    ctx.lineWidth = 2;
    for (let x = 0; x <= width + 2; x++) {
        for (let y = 0; y <= height + 2; y++) {
            ctx.strokeRect(x * cellSize, y * cellSize, cellSize, cellSize);
        }
    }
}

/**
 * Основная функция, объединяющая все остальные
 * (если хотите оставить единый вход, но с вызовами отдельных частей).
 * @param {HTMLCanvasElement} canvas
 * @param {Object} params - все нужные параметры, чтобы не передавать 100 аргументов
 */
export function drawField(canvas, params) {
    const {
        coloredCells, robotPos, markers, walls, permanentWalls, width, height, cellSize
    } = params;

    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    // 1. Очистка
    clearCanvas(canvas, ctx);

    // 2. Раскрасить ячейки
    drawColoredCells(ctx, coloredCells, cellSize);

    // 3. Робот
    drawRobot(ctx, robotPos, cellSize);

    // 4. Маркеры
    drawMarkers(ctx, markers, cellSize);

    // 5. Обычные стены (толщиной 8, цветом '#C8C80F')
    drawWalls(ctx, walls, cellSize, '#C8C80F', 8);

    // 6. Постоянные стены (те же цвет/толщина, но можно задать и другой)
    drawWalls(ctx, permanentWalls, cellSize, '#C8C80F', 8);

    // 7. Сетка
    drawGrid(ctx, width, height, cellSize);
}
