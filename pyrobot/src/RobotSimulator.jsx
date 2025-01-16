import React, {useEffect, useRef, useState} from 'react';
import {Button, Card, CardContent, CardHeader, Typography, Grid} from '@mui/material';
import {ChevronUp, ChevronDown, ChevronLeft, ChevronRight} from 'lucide-react';
import './styles.css';

const RobotSimulator = () => {
    const [width, setWidth] = useState(7);
    const [height, setHeight] = useState(7);
    const [editMode, setEditMode] = useState(false);
    const [robotPos, setRobotPos] = useState({x: 0, y: 0});
    const [walls, setWalls] = useState(new Set());
    const [permanentWalls, setPermanentWalls] = useState(new Set());
    const [markers, setMarkers] = useState({});
    const [coloredCells, setColoredCells] = useState(new Set());
    const [statusMessage, setStatusMessage] = useState("Click between cells to add/remove walls");
    const canvasRef = useRef(null);
    const [cellSize, setCellSize] = useState(50); // State для размера ячейки

    // При изменении размеров поля пересоздаем постоянные стены (границы)
    useEffect(() => {
        setupPermanentWalls();
    }, [width, height]);

    // Перерисовка при любом изменении важных параметров
    useEffect(() => {
        drawField();
    }, [robotPos, width, height, walls, coloredCells, markers, cellSize, permanentWalls]);

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

    const drawField = () => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Заливка раскрашенных ячеек
        ctx.fillStyle = 'gray';
        coloredCells.forEach(cell => {
            const [x, y] = cell.split(',').map(Number);
            ctx.fillRect((x + 1) * cellSize, (y + 1) * cellSize, cellSize, cellSize);
        });

        // Рисуем робота (ромб)
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

        // Рисуем маркеры (кружочки)
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

        // Рисуем стены (оранжевым цветом)
        ctx.strokeStyle = '#C8C80F';
        ctx.lineWidth = 8;
        walls.forEach(wall => {
            const [x1, y1, x2, y2] = wall.split(',').map(Number);
            ctx.beginPath();
            ctx.moveTo((x1 + 1) * cellSize, (y1 + 1) * cellSize);
            ctx.lineTo((x2 + 1) * cellSize, (y2 + 1) * cellSize);
            ctx.stroke();
        });

        // Рисуем постоянные стены
        permanentWalls.forEach(wall => {
            const [x1, y1, x2, y2] = wall.split(',').map(Number);
            ctx.beginPath();
            ctx.moveTo((x1 + 1) * cellSize, (y1 + 1) * cellSize);
            ctx.lineTo((x2 + 1) * cellSize, (y2 + 1) * cellSize);
            ctx.stroke();
        });

        // Рисуем сетку
        ctx.strokeStyle = '#C8C80F';
        ctx.lineWidth = 2;
        for (let x = 0; x <= width + 2; x++) {
            for (let y = 0; y <= height + 2; y++) {
                ctx.strokeRect(x * cellSize, y * cellSize, cellSize, cellSize);
            }
        }
    };

    const handleCanvasClick = (event) => {
        if (!editMode) return;

        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const gridX = Math.floor(x / cellSize) - 1;
        const gridY = Math.floor(y / cellSize) - 1;
        const margin = 5;

        if (gridX < 0 || gridX >= width || gridY < 0 || gridY >= height) {
            return; // Не действуем за пределами поля
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
            // Если не попали в стену, красим/снимаем краску
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

    const handleCanvasRightClick = (event) => {
        event.preventDefault(); // Не показывать контекстное меню
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

    const handleCanvasWheel = (event) => {
        event.preventDefault();
        event.stopPropagation();
        setCellSize((prev) => Math.max(10, prev + (event.deltaY > 0 ? -5 : 5)));
    };

    // Запрещаем прокрутку страницы при прокрутке колесом над канвасом
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

    // Добавить маркер в позицию робота
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

    // Забрать маркер в позиции робота
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

    // Покрасить текущую ячейку робота
    const paintCell = () => {
        const pos = `${robotPos.x},${robotPos.y}`;
        setColoredCells((prev) => {
            const newCells = new Set(prev);
            newCells.add(pos);
            return newCells;
        });
    };

    // Снять покраску текущей ячейки робота
    const clearCell = () => {
        const pos = `${robotPos.x},${robotPos.y}`;
        setColoredCells((prev) => {
            const newCells = new Set(prev);
            newCells.delete(pos);
            return newCells;
        });
    };

    // Изменение ширины/высоты поля
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
            {/* Левая панель управления */}
            <Card className="card">
                <CardHeader
                    title={<Typography variant="h6" style={{textAlign: 'center'}}>Controls</Typography>}
                />
                <CardContent>
                    <Grid container spacing={2} alignItems="center" justifyContent="center">
                        {/* Кнопки движения */}
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

                        {/* Кнопки маркеров и покраски */}
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

                        {/* Режим редактирования */}
                        <Grid item xs={12}>
                            <Button
                                variant="outlined"
                                className="button full-width-outlined"
                                onClick={() => setEditMode(!editMode)}
                            >
                                {editMode ? 'Exit Edit Mode' : 'Enter Edit Mode'}
                            </Button>
                        </Grid>

                        {/* Изменение размеров */}
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

            {/* Правая часть экрана: Canvas + отдельный блок статуса */}
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
