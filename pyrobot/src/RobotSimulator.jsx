import React, {useEffect, useRef, useState} from 'react';
import {Button, Card, CardContent, CardHeader, Typography, Grid} from '@mui/material';
import {ChevronUp, ChevronDown, ChevronLeft, ChevronRight} from 'lucide-react';
import './styles.css';

/**
 * Основной компонент симулятора робота.
 * Содержит поле (Canvas) с сеткой, стены, робот, а также панель управления.
 */
const RobotSimulator = () => {
    // -------------------------------
    // Состояния (hooks useState)
    // -------------------------------
    const [width, setWidth] = useState(7);          // Ширина в клетках
    const [height, setHeight] = useState(7);        // Высота в клетках
    const [editMode, setEditMode] = useState(false); // Режим редактирования (возможность ставить стены, красить клетки)
    const [robotPos, setRobotPos] = useState({x: 0, y: 0}); // Позиция робота
    const [walls, setWalls] = useState(new Set());          // Множество "стен", заданных пользователем
    const [permanentWalls, setPermanentWalls] = useState(new Set()); // Статичные стены (границы поля)
    const [markers, setMarkers] = useState({});     // Маркеры (ключ: "x,y")
    const [coloredCells, setColoredCells] = useState(new Set()); // Набор раскрашенных ячеек
    const [statusMessage, setStatusMessage] = useState("Click between cells to add/remove walls");
    const canvasRef = useRef(null);                 // Ссылка на Canvas
    const [cellSize, setCellSize] = useState(50);   // Размер (в пикселях) одной клетки

    /**
     * useEffect: При изменении ширины/высоты переопределяем постоянные стены.
     */
    useEffect(() => {
        setupPermanentWalls();
    }, [width, height]);

    /**
     * useEffect: Перерисовываем поле при любых изменениях ключевых параметров.
     */
    useEffect(() => {
        drawField();
    }, [robotPos, width, height, walls, coloredCells, markers, cellSize, permanentWalls]);

    /**
     * Создаёт набор постоянных стен (границ поля), исходя из текущих width/height.
     * Записывает их в state (setPermanentWalls).
     */
    const setupPermanentWalls = () => {
        const newPermanentWalls = new Set();

        // Верхняя и нижняя горизонтальные границы
        for (let x = 0; x < width; x++) {
            newPermanentWalls.add(`${x},0,${x + 1},0`);
            newPermanentWalls.add(`${x},${height},${x + 1},${height}`);
        }

        // Левая и правая вертикальные границы
        for (let y = 0; y < height; y++) {
            newPermanentWalls.add(`0,${y},0,${y + 1}`);
            newPermanentWalls.add(`${width},${y},${width},${y + 1}`);
        }
        setPermanentWalls(newPermanentWalls);
    };

    /**
     * Функция для рисования всего игрового поля на Canvas:
     * - Очищает Canvas
     * - Отрисовывает раскрашенные ячейки
     * - Отрисовывает робота
     * - Отрисовывает маркеры
     * - Отрисовывает стены (и обычные, и постоянные)
     * - Отрисовывает сетку
     */
    const drawField = () => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        // Очистка холста (полностью)
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // 1. Рисуем раскрашенные клетки (серым цветом)
        ctx.fillStyle = 'gray';
        coloredCells.forEach(cell => {
            const [x, y] = cell.split(',').map(Number);
            // Сдвиг "на 1 клетку" вправо/вниз, чтобы получить рамку вокруг
            ctx.fillRect((x + 1) * cellSize, (y + 1) * cellSize, cellSize, cellSize);
        });

        // 2. Рисуем робота (оранжевый ромб)
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

        // 3. Рисуем маркеры (маленькие белые круги)
        Object.keys(markers).forEach(key => {
            const [x, y] = key.split(',').map(Number);
            ctx.fillStyle = 'white';
            ctx.beginPath();
            ctx.arc(
                (x + 1.75) * cellSize, // смещение на 1.75 клетки: чуть правее/ниже центра
                (y + 1.75) * cellSize,
                cellSize * 0.15,      // радиус примерно 15% от cellSize
                0,
                2 * Math.PI
            );
            ctx.fill();
            ctx.strokeStyle = 'black'; // Чёрная тонкая обводка
            ctx.lineWidth = 1;
            ctx.stroke();
        });

        // 4. Рисуем обычные (добавленные пользователем) стены (толстая жёлтая линия)
        ctx.strokeStyle = '#C8C80F';
        ctx.lineWidth = 8;
        walls.forEach(wall => {
            const [x1, y1, x2, y2] = wall.split(',').map(Number);
            ctx.beginPath();
            ctx.moveTo((x1 + 1) * cellSize, (y1 + 1) * cellSize);
            ctx.lineTo((x2 + 1) * cellSize, (y2 + 1) * cellSize);
            ctx.stroke();
        });

        // 5. Рисуем постоянные стены (границы)
        permanentWalls.forEach(wall => {
            const [x1, y1, x2, y2] = wall.split(',').map(Number);
            ctx.beginPath();
            ctx.moveTo((x1 + 1) * cellSize, (y1 + 1) * cellSize);
            ctx.lineTo((x2 + 1) * cellSize, (y2 + 1) * cellSize);
            ctx.stroke();
        });

        // 6. Рисуем сетку (тонкая жёлтая линия, 2px)
        ctx.strokeStyle = '#C8C80F';
        ctx.lineWidth = 2;
        for (let x = 0; x <= width + 2; x++) {
            for (let y = 0; y <= height + 2; y++) {
                ctx.strokeRect(x * cellSize, y * cellSize, cellSize, cellSize);
            }
        }
    };

    /**
     * Обработчик левого клика мышью по Canvas.
     * Если режим редактирования включён (editMode = true):
     *  - Если клик ближе к границе клетки (определяется через margin),
     *    добавляем/удаляем стену (если она не является постоянной).
     *  - Иначе переключаем раскраску ячейки (окрасить/снять окраску).
     */
    const handleCanvasClick = (event) => {
        if (!editMode) return;

        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        // Координаты клика внутри canvas
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        // Определяем, над какой клеткой (gridX, gridY) произошёл клик
        // "−1", чтобы учесть отступ в 1 клетку, который добавлен при рисовании
        const gridX = Math.floor(x / cellSize) - 1;
        const gridY = Math.floor(y / cellSize) - 1;

        // Небольшая "зона" у границы, где будем решать, что это клик по стене
        const margin = 5;

        // Проверяем, что мы не вышли за пределы основного поля
        if (gridX < 0 || gridX >= width || gridY < 0 || gridY >= height) {
            return;
        }

        // Остатки внутри клетки, чтобы понять, близко ли мы к краю
        const xRemainder = x % cellSize;
        const yRemainder = y % cellSize;

        let wall = null;
        // Если очень близко к левой границе клетки
        if (xRemainder < margin) {
            wall = `${gridX},${gridY},${gridX},${gridY + 1}`;
        }
        // Если очень близко к правой границе клетки
        else if (xRemainder > cellSize - margin) {
            wall = `${gridX + 1},${gridY},${gridX + 1},${gridY + 1}`;
        }
        // Если очень близко к верхней границе клетки
        else if (yRemainder < margin) {
            wall = `${gridX},${gridY},${gridX + 1},${gridY}`;
        }
        // Если очень близко к нижней границе клетки
        else if (yRemainder > cellSize - margin) {
            wall = `${gridX},${gridY + 1},${gridX + 1},${gridY + 1}`;
        }

        // Если мы определили, что это клик по границе (wall != null)
        // и при этом эта граница не является постоянной (границы поля),
        // тогда добавить/убрать её из walls.
        if (wall && !permanentWalls.has(wall)) {
            setWalls((prev) => {
                const newWalls = new Set(prev);
                if (newWalls.has(wall)) {
                    newWalls.delete(wall);
                } else {
                    newWalls.add(wall);
                }
                return newWalls;
            });
        }
        else {
            // Иначе (не ближе к краю) раскрашиваем/снимаем раскраску ячейки
            const pos = `${gridX},${gridY}`;
            setColoredCells((prev) => {
                const newCells = new Set(prev);
                if (newCells.has(pos)) {
                    newCells.delete(pos);
                } else {
                    newCells.add(pos);
                }
                return newCells;
            });
        }
    };

    /**
     * Обработчик правого клика мышью по Canvas.
     * Если режим редактирования включён, то в ячейке ставим/убираем маркер (toggle).
     *
     * @param {MouseEvent} event - Содержит координаты и др. данные о клике.
     */
    const handleCanvasRightClick = (event) => {
        // Отменяем стандартное контекстное меню
        event.preventDefault();
        if (!editMode) return;

        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const gridX = Math.floor(x / cellSize) - 1;
        const gridY = Math.floor(y / cellSize) - 1;

        // Не даём ставить маркеры за границей поля
        if (gridX < 0 || gridX >= width || gridY < 0 || gridY >= height) return;

        const pos = `${gridX},${gridY}`;
        setMarkers((prev) => {
            const newMarkers = {...prev};
            // Если маркера нет — ставим
            if (!newMarkers[pos]) {
                newMarkers[pos] = 1;
            }
            // Если есть — убираем
            else {
                delete newMarkers[pos];
            }
            return newMarkers;
        });
    };

    /**
     * Двигает робота в заданном направлении (up/down/left/right).
     * При проверке учитываются стены (walls и permanentWalls).
     *
     * @param {'up'|'down'|'left'|'right'} direction - Направление движения.
     */
    const moveRobot = (direction) => {
        setRobotPos((prevPos) => {
            let newPos = {...prevPos};
            switch (direction) {
                case 'up':
                    // Проверяем верхнюю границу и отсутствие стены
                    if (
                        newPos.y > 0 &&
                        !walls.has(`${newPos.x},${newPos.y},${newPos.x + 1},${newPos.y}`) &&
                        !permanentWalls.has(`${newPos.x},${newPos.y},${newPos.x + 1},${newPos.y}`)
                    ) {
                        newPos.y -= 1;
                    }
                    break;
                case 'down':
                    // Проверяем нижнюю границу и отсутствие стены
                    if (
                        newPos.y < height - 1 &&
                        !walls.has(`${newPos.x},${newPos.y + 1},${newPos.x + 1},${newPos.y + 1}`) &&
                        !permanentWalls.has(`${newPos.x},${newPos.y + 1},${newPos.x + 1},${newPos.y + 1}`)
                    ) {
                        newPos.y += 1;
                    }
                    break;
                case 'left':
                    // Проверяем левую границу и отсутствие стены
                    if (
                        newPos.x > 0 &&
                        !walls.has(`${newPos.x},${newPos.y},${newPos.x},${newPos.y + 1}`) &&
                        !permanentWalls.has(`${newPos.x},${newPos.y},${newPos.x},${newPos.y + 1}`)
                    ) {
                        newPos.x -= 1;
                    }
                    break;
                case 'right':
                    // Проверяем правую границу и отсутствие стены
                    if (
                        newPos.x < width - 1 &&
                        !walls.has(`${newPos.x + 1},${newPos.y},${newPos.x + 1},${newPos.y + 1}`) &&
                        !permanentWalls.has(`${newPos.x + 1},${newPos.y},${newPos.x + 1},${newPos.y + 1}`)
                    ) {
                        newPos.x += 1;
                    }
                    break;
                default:
                    // Неизвестное направление — ничего не делаем
                    break;
            }
            return newPos;
        });
    };

    /**
     * Обработчик события колёсика мыши (прокрутки) над Canvas.
     * Уменьшает/увеличивает размер клетки (cellSize) с ограничением минимум 10px.
     */
    const handleCanvasWheel = (event) => {
        event.preventDefault();
        event.stopPropagation();
        // При прокрутке вниз (deltaY > 0) уменьшаем cellSize, вверх — увеличиваем
        setCellSize((prev) => Math.max(10, prev + (event.deltaY > 0 ? -5 : 5)));
    };

    /**
     * useEffect для блокировки прокрутки всей страницы при прокрутке в области Canvas.
     */
    useEffect(() => {
        const canvas = canvasRef.current;
        if (canvas) {
            const preventScroll = (event) => {
                event.preventDefault();
            };
            // Добавляем слушатель (passive: false, чтобы можно было отменить)
            canvas.addEventListener('wheel', preventScroll, {passive: false});
            // При размонтировании убираем слушатель
            return () => {
                canvas.removeEventListener('wheel', preventScroll);
            };
        }
    }, []);

    /**
     * Кладёт маркер в ячейку, где сейчас находится робот.
     * (Если маркера не было — появляется, если был, то не убирается, это не toggle).
     */
    const putMarker = () => {
        const pos = `${robotPos.x},${robotPos.y}`;
        setMarkers((prev) => {
            const newMarkers = {...prev};
            // Если там нет маркера, ставим
            if (!newMarkers[pos]) {
                newMarkers[pos] = 1;
            }
            return newMarkers;
        });
    };

    /**
     * Забирает маркер в ячейке, где сейчас находится робот (если там есть).
     */
    const pickMarker = () => {
        const pos = `${robotPos.x},${robotPos.y}`;
        setMarkers((prev) => {
            const newMarkers = {...prev};
            if (newMarkers[pos]) {
                // Удаляем из объекта
                delete newMarkers[pos];
            }
            return newMarkers;
        });
    };

    /**
     * Раскрасить клетку, в которой находится робот.
     */
    const paintCell = () => {
        const pos = `${robotPos.x},${robotPos.y}`;
        setColoredCells((prev) => {
            const newCells = new Set(prev);
            newCells.add(pos);
            return newCells;
        });
    };

    /**
     * Снять раскраску с клетки, в которой находится робот.
     */
    const clearCell = () => {
        const pos = `${robotPos.x},${robotPos.y}`;
        setColoredCells((prev) => {
            const newCells = new Set(prev);
            newCells.delete(pos);
            return newCells;
        });
    };

    /**
     * Увеличить ширину поля на 1 (только если в режиме редактирования).
     */
    const increaseWidth = () => {
        if (editMode) {
            setWidth((prev) => prev + 1);
        }
    };

    /**
     * Уменьшить ширину поля на 1 (минимум 1).
     */
    const decreaseWidth = () => {
        if (editMode && width > 1) {
            setWidth((prev) => prev - 1);
        }
    };

    /**
     * Увеличить высоту поля на 1 (только если в режиме редактирования).
     */
    const increaseHeight = () => {
        if (editMode) {
            setHeight((prev) => prev + 1);
        }
    };

    /**
     * Уменьшить высоту поля на 1 (минимум 1).
     */
    const decreaseHeight = () => {
        if (editMode && height > 1) {
            setHeight((prev) => prev - 1);
        }
    };

    // -------------------------------------------------------------------------
    // Вёрстка JSX
    // -------------------------------------------------------------------------
    return (
        <div className="container">
            {/* Левая панель управления (Card) */}
            <Card className="card">
                <CardHeader
                    title={<Typography variant="h6" style={{textAlign: 'center'}}>Controls</Typography>}
                />
                <CardContent>
                    <Grid container spacing={2} alignItems="center" justifyContent="center">
                        {/* Кнопки движения (стрелки) */}
                        <Grid item xs={4}></Grid>
                        <Grid item xs={4}>
                            <Button
                                variant="contained"
                                className="button"
                                onClick={() => moveRobot('up')}
                            >
                                <ChevronUp />
                            </Button>
                        </Grid>
                        <Grid item xs={4}></Grid>

                        <Grid item xs={4}>
                            <Button
                                variant="contained"
                                className="button"
                                onClick={() => moveRobot('left')}
                            >
                                <ChevronLeft />
                            </Button>
                        </Grid>
                        <Grid item xs={4}></Grid>
                        <Grid item xs={4}>
                            <Button
                                variant="contained"
                                className="button"
                                onClick={() => moveRobot('right')}
                            >
                                <ChevronRight />
                            </Button>
                        </Grid>

                        <Grid item xs={4}></Grid>
                        <Grid item xs={4}>
                            <Button
                                variant="contained"
                                className="button"
                                onClick={() => moveRobot('down')}
                            >
                                <ChevronDown />
                            </Button>
                        </Grid>
                        <Grid item xs={4}></Grid>

                        {/* Кнопки для маркеров и покраски */}
                        <Grid item xs={6}>
                            <Button
                                variant="contained"
                                className="button full-width"
                                onClick={putMarker}
                            >
                                Put Marker
                            </Button>
                        </Grid>
                        <Grid item xs={6}>
                            <Button
                                variant="contained"
                                className="button full-width"
                                onClick={pickMarker}
                            >
                                Pick Marker
                            </Button>
                        </Grid>
                        <Grid item xs={6}>
                            <Button
                                variant="contained"
                                className="button full-width"
                                onClick={paintCell}
                            >
                                Paint Cell
                            </Button>
                        </Grid>
                        <Grid item xs={6}>
                            <Button
                                variant="contained"
                                className="button full-width"
                                onClick={clearCell}
                            >
                                Clear Cell
                            </Button>
                        </Grid>

                        {/* Переключатель режима редактирования */}
                        <Grid item xs={12}>
                            <Button
                                variant="outlined"
                                className="button full-width-outlined"
                                onClick={() => setEditMode(!editMode)}
                            >
                                {editMode ? 'Exit Edit Mode' : 'Enter Edit Mode'}
                            </Button>
                        </Grid>

                        {/* Кнопки изменения размеров (Width и Height) */}
                        <Grid item xs={6}>
                            <Button
                                variant="contained"
                                className="button full-width"
                                onClick={increaseWidth}
                            >
                                Width +
                            </Button>
                        </Grid>
                        <Grid item xs={6}>
                            <Button
                                variant="contained"
                                className="button full-width"
                                onClick={decreaseWidth}
                            >
                                Width -
                            </Button>
                        </Grid>
                        <Grid item xs={6}>
                            <Button
                                variant="contained"
                                className="button full-width"
                                onClick={increaseHeight}
                            >
                                Height +
                            </Button>
                        </Grid>
                        <Grid item xs={6}>
                            <Button
                                variant="contained"
                                className="button full-width"
                                onClick={decreaseHeight}
                            >
                                Height -
                            </Button>
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>

            {/* Справа: область поля + отдельный блок статуса */}
            <div className="field-area">
                {/* Карточка с Canvas */}
                <Card className="card-controls">
                    <canvas
                        ref={canvasRef}
                        width={(width + 2) * cellSize}
                        height={(height + 2) * cellSize}
                        className={editMode ? 'edit-mode' : ''}
                        onClick={handleCanvasClick}
                        onContextMenu={handleCanvasRightClick}
                        onWheel={handleCanvasWheel}
                    />
                </Card>

                {/* Отдельный блок для статуса (под Canvas) */}
                <Card className="status-card">
                    <Typography variant="body2">{statusMessage}</Typography>
                </Card>
            </div>
        </div>
    );
};

export default RobotSimulator;
