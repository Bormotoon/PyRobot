import React, {useEffect, useRef, useState} from 'react';
import {Button, Card, CardContent, CardHeader, Typography, Grid} from '@mui/material';
import {ChevronUp, ChevronDown, ChevronLeft, ChevronRight} from 'lucide-react';

import './styles.css';
import {drawField} from './canvasDrawing'; // <-- Импорт функций рисования

/**
 * Основной компонент RobotSimulator
 */
const RobotSimulator = () => {
    // -------------------------------
    // Состояния (hooks useState)
    // -------------------------------
    const [width, setWidth] = useState(7);
    const [height, setHeight] = useState(7);
    const [editMode, setEditMode] = useState(false);
    const [robotPos, setRobotPos] = useState({x: 0, y: 0});
    const [walls, setWalls] = useState(new Set());
    const [permanentWalls, setPermanentWalls] = useState(new Set());
    const [markers, setMarkers] = useState({});
    const [coloredCells, setColoredCells] = useState(new Set());
    const [statusMessage, setStatusMessage] = useState("Click between cells to add/remove walls");
    const [cellSize, setCellSize] = useState(50); // Размер одной клетки
    const canvasRef = useRef(null);

    /**
     * useEffect: Создаём постоянные стены при изменении ширины/высоты
     */
    useEffect(() => {
        setupPermanentWalls();
    }, [width, height]);

    /**
     * useEffect: Перерисовываем поле при изменении любых важных состояний
     */
    useEffect(() => {
        const canvas = canvasRef.current;
        // Собираем все параметры, которые нужны для рисования
        const params = {
            coloredCells,
            robotPos,
            markers,
            walls,
            permanentWalls,
            width,
            height,
            cellSize
        };
        drawField(canvas, params);
    }, [robotPos, width, height, walls, coloredCells, markers, cellSize, permanentWalls]);

    /**
     * Создаёт (или пересоздаёт) набор постоянных стен (границы поля).
     */
    const setupPermanentWalls = () => {
        const newPermanentWalls = new Set();
        // Верхняя и нижняя границы
        for (let x = 0; x < width; x++) {
            newPermanentWalls.add(`${x},0,${x + 1},0`);
            newPermanentWalls.add(`${x},${height},${x + 1},${height}`);
        }
        // Левая и правая границы
        for (let y = 0; y < height; y++) {
            newPermanentWalls.add(`0,${y},0,${y + 1}`);
            newPermanentWalls.add(`${width},${y},${width},${y + 1}`);
        }
        setPermanentWalls(newPermanentWalls);
    };

    /**
     * Обработчик клика левой кнопкой мыши по Canvas
     */
    const handleCanvasClick = (event) => {
        if (!editMode) return;

        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const gridX = Math.floor(x / cellSize) - 1;
        const gridY = Math.floor(y / cellSize) - 1;
        const margin = 5;

        // Не даём действовать за пределами основного поля
        if (gridX < 0 || gridX >= width || gridY < 0 || gridY >= height) {
            return;
        }

        const xRemainder = x % cellSize;
        const yRemainder = y % cellSize;

        let wall = null;
        if (xRemainder < margin) {
            wall = `${gridX},${gridY},${gridX},${gridY + 1}`;
        } else if (xRemainder > cellSize - margin) {
            wall = `${gridX + 1},${gridY},${gridX + 1},${gridY + 1}`;
        } else if (yRemainder < margin) {
            wall = `${gridX},${gridY},${gridX + 1},${gridY}`;
        } else if (yRemainder > cellSize - margin) {
            wall = `${gridX},${gridY + 1},${gridX + 1},${gridY + 1}`;
        }

        // Если это "попадание" на границу клетки (wall != null), проверяем, не постоянная ли стена
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
        } else {
            // Иначе красим/снимаем краску
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
     * Обработчик клика правой кнопкой по Canvas (ставим/убираем маркер)
     */
    const handleCanvasRightClick = (event) => {
        event.preventDefault(); // не показывать контекстное меню
        if (!editMode) return;

        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const gridX = Math.floor(x / cellSize) - 1;
        const gridY = Math.floor(y / cellSize) - 1;

        if (gridX < 0 || gridX >= width || gridY < 0 || gridY >= height) return;

        const pos = `${gridX},${gridY}`;
        setMarkers((prev) => {
            const newMarkers = {...prev};
            if (!newMarkers[pos]) {
                newMarkers[pos] = 1;
            } else {
                delete newMarkers[pos];
            }
            return newMarkers;
        });
    };

    /**
     * Двигаем робота в указанном направлении (up/down/left/right),
     * проверяем стены (обычные и постоянные).
     */
    const moveRobot = (direction) => {
        setRobotPos((prevPos) => {
            let newPos = {...prevPos};
            switch (direction) {
                case 'up':
                    if (
                        newPos.y > 0 &&
                        !walls.has(`${newPos.x},${newPos.y},${newPos.x + 1},${newPos.y}`) &&
                        !permanentWalls.has(`${newPos.x},${newPos.y},${newPos.x + 1},${newPos.y}`)
                    ) {
                        newPos.y -= 1;
                    }
                    break;
                case 'down':
                    if (
                        newPos.y < height - 1 &&
                        !walls.has(`${newPos.x},${newPos.y + 1},${newPos.x + 1},${newPos.y + 1}`) &&
                        !permanentWalls.has(`${newPos.x},${newPos.y + 1},${newPos.x + 1},${newPos.y + 1}`)
                    ) {
                        newPos.y += 1;
                    }
                    break;
                case 'left':
                    if (
                        newPos.x > 0 &&
                        !walls.has(`${newPos.x},${newPos.y},${newPos.x},${newPos.y + 1}`) &&
                        !permanentWalls.has(`${newPos.x},${newPos.y},${newPos.x},${newPos.y + 1}`)
                    ) {
                        newPos.x -= 1;
                    }
                    break;
                case 'right':
                    if (
                        newPos.x < width - 1 &&
                        !walls.has(`${newPos.x + 1},${newPos.y},${newPos.x + 1},${newPos.y + 1}`) &&
                        !permanentWalls.has(`${newPos.x + 1},${newPos.y},${newPos.x + 1},${newPos.y + 1}`)
                    ) {
                        newPos.x += 1;
                    }
                    break;
                default:
                    break;
            }
            return newPos;
        });
    };

    /**
     * Масштабирование колёсиком: меняем cellSize (минимум 10).
     */
    const handleCanvasWheel = (event) => {
        event.preventDefault();
        event.stopPropagation();
        setCellSize((prev) => Math.max(10, prev + (event.deltaY > 0 ? -5 : 5)));
    };

    // useEffect для блокировки прокрутки страницы при колесе над канвасом
    useEffect(() => {
        const canvas = canvasRef.current;
        if (canvas) {
            const preventScroll = (event) => {
                event.preventDefault();
            };
            canvas.addEventListener('wheel', preventScroll, {passive: false});
            return () => {
                canvas.removeEventListener('wheel', preventScroll);
            };
        }
    }, []);

    /**
     * Положить маркер в клетку, где стоит робот
     */
    const putMarker = () => {
        const pos = `${robotPos.x},${robotPos.y}`;
        setMarkers((prev) => {
            const newMarkers = {...prev};
            if (!newMarkers[pos]) {
                newMarkers[pos] = 1;
            }
            return newMarkers;
        });
    };

    /**
     * Забрать маркер из клетки, где стоит робот
     */
    const pickMarker = () => {
        const pos = `${robotPos.x},${robotPos.y}`;
        setMarkers((prev) => {
            const newMarkers = {...prev};
            if (newMarkers[pos]) {
                delete newMarkers[pos];
            }
            return newMarkers;
        });
    };

    /**
     * Покрасить клетку, где стоит робот
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
     * Снять краску с клетки, где стоит робот
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
     * Увеличение/уменьшение ширины (только в режиме редактирования)
     */
    const increaseWidth = () => {
        if (editMode) {
            setWidth((prev) => prev + 1);
        }
    };
    const decreaseWidth = () => {
        if (editMode && width > 1) {
            setWidth((prev) => prev - 1);
        }
    };

    /**
     * Увеличение/уменьшение высоты (только в режиме редактирования)
     */
    const increaseHeight = () => {
        if (editMode) {
            setHeight((prev) => prev + 1);
        }
    };
    const decreaseHeight = () => {
        if (editMode && height > 1) {
            setHeight((prev) => prev - 1);
        }
    };

    return (
        <div className="container">
            {/* Левая панель управления (Card) */}
            <Card className="card">
                <CardHeader
                    title={<Typography variant="h6" style={{textAlign: 'center'}}>Controls</Typography>}
                />
                <CardContent>
                    <Grid container spacing={2} alignItems="center" justifyContent="center">
                        {/* Кнопки перемещения */}
                        <Grid item xs={4}></Grid>
                        <Grid item xs={4}>
                            <Button
                                variant="contained"
                                className="button"
                                onClick={() => moveRobot('up')}
                            >
                                <ChevronUp/>
                            </Button>
                        </Grid>
                        <Grid item xs={4}></Grid>

                        <Grid item xs={4}>
                            <Button
                                variant="contained"
                                className="button"
                                onClick={() => moveRobot('left')}
                            >
                                <ChevronLeft/>
                            </Button>
                        </Grid>
                        <Grid item xs={4}></Grid>
                        <Grid item xs={4}>
                            <Button
                                variant="contained"
                                className="button"
                                onClick={() => moveRobot('right')}
                            >
                                <ChevronRight/>
                            </Button>
                        </Grid>

                        <Grid item xs={4}></Grid>
                        <Grid item xs={4}>
                            <Button
                                variant="contained"
                                className="button"
                                onClick={() => moveRobot('down')}
                            >
                                <ChevronDown/>
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

                        {/* Кнопка переключения режима редактирования */}
                        <Grid item xs={12}>
                            <Button
                                variant="outlined"
                                className="button full-width-outlined"
                                onClick={() => setEditMode(!editMode)}
                            >
                                {editMode ? 'Exit Edit Mode' : 'Enter Edit Mode'}
                            </Button>
                        </Grid>

                        {/* Изменение ширины и высоты */}
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

            {/* Правая часть: Canvas + статус */}
            <div className="field-area">
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
                <Card className="status-card">
                    <Typography variant="body2">{statusMessage}</Typography>
                </Card>
            </div>
        </div>
    );
};

export default RobotSimulator;
