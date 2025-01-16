import React, {useEffect, useRef, useState} from 'react';
import {
    Button,
    Card,
    CardContent,
    CardHeader,
    Typography,
    Grid,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions
} from '@mui/material';
import {ChevronUp, ChevronDown, ChevronLeft, ChevronRight} from 'lucide-react';

import './styles.css';
import {drawField} from './canvasDrawing';

/**
 * Компонент RobotSimulator, ориентированный на учащихся 8 классов:
 * - Более дружелюбные тексты
 * - Кнопка "Помощь" (Help)
 * - Подсказки/инструкции
 */
const RobotSimulator = () => {
    const [width, setWidth] = useState(7);
    const [height, setHeight] = useState(7);
    const [editMode, setEditMode] = useState(false);
    const [robotPos, setRobotPos] = useState({x: 0, y: 0});
    const [walls, setWalls] = useState(new Set());
    const [permanentWalls, setPermanentWalls] = useState(new Set());
    const [markers, setMarkers] = useState({});
    const [coloredCells, setColoredCells] = useState(new Set());
    // UX IMPROVEMENT: Изменили стандартное сообщение на более понятное для школьников.
    const [statusMessage, setStatusMessage] = useState("Используйте кнопки слева, чтобы двигать Робота и рисовать на поле!");
    const [cellSize, setCellSize] = useState(50);

    const canvasRef = useRef(null);

    // UX IMPROVEMENT: Состояние для отображения модального окна "Помощь".
    const [helpOpen, setHelpOpen] = useState(false);

    useEffect(() => {
        setupPermanentWalls();

        // Если при изменении размеров робот "вышел" за границы, возвращаем внутрь.
        setRobotPos(prev => {
            const clampedX = Math.min(Math.max(prev.x, 0), width - 1);
            const clampedY = Math.min(Math.max(prev.y, 0), height - 1);
            return {x: clampedX, y: clampedY};
        });
    }, [width, height]);

    useEffect(() => {
        const canvas = canvasRef.current;
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
     * Создание постоянных (внешних) стенок вокруг поля.
     */
    const setupPermanentWalls = () => {
        const newPermanentWalls = new Set();
        for (let x = 0; x < width; x++) {
            newPermanentWalls.add(`${x},0,${x + 1},0`);
            newPermanentWalls.add(`${x},${height},${x + 1},${height}`);
        }
        for (let y = 0; y < height; y++) {
            newPermanentWalls.add(`0,${y},0,${y + 1}`);
            newPermanentWalls.add(`${width},${y},${width},${y + 1}`);
        }
        setPermanentWalls(newPermanentWalls);
    };

    // -----------------
    // Обработчики Canvas
    // -----------------
    const handleCanvasClick = (event) => {
        if (!editMode) {
            // UX IMPROVEMENT: Подсказка, если кликнули при выключенном режиме редактирования
            setStatusMessage("Вы кликнули по полю, но 'Режим рисования' не включён!");
            return;
        }

        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const gridX = Math.floor(x / cellSize) - 1;
        const gridY = Math.floor(y / cellSize) - 1;
        const margin = 5;

        // Проверяем, не вышли ли за границы
        if (gridX < 0 || gridX >= width || gridY < 0 || gridY >= height) {
            setStatusMessage("Клик за пределами поля — действие не выполнено.");
            return;
        }

        const xRemainder = x % cellSize;
        const yRemainder = y % cellSize;
        let wall = null;
        if (xRemainder < margin) {
            if (gridX >= 0 && gridY >= 0 && gridY + 1 <= height) {
                wall = `${gridX},${gridY},${gridX},${gridY + 1}`;
            }
        } else if (xRemainder > cellSize - margin) {
            if (gridX + 1 <= width && gridY >= 0 && gridY + 1 <= height) {
                wall = `${gridX + 1},${gridY},${gridX + 1},${gridY + 1}`;
            }
        } else if (yRemainder < margin) {
            if (gridX >= 0 && gridX + 1 <= width && gridY >= 0) {
                wall = `${gridX},${gridY},${gridX + 1},${gridY}`;
            }
        } else if (yRemainder > cellSize - margin) {
            if (gridX >= 0 && gridX + 1 <= width && gridY + 1 <= height) {
                wall = `${gridX},${gridY + 1},${gridX + 1},${gridY + 1}`;
            }
        }

        // Если определили границу (стену)
        if (wall && !permanentWalls.has(wall)) {
            setWalls(prev => {
                const newWalls = new Set(prev);
                if (newWalls.has(wall)) {
                    newWalls.delete(wall);
                    setStatusMessage("Стена удалена.");
                } else {
                    newWalls.add(wall);
                    setStatusMessage("Вы поставили стену!");
                }
                return newWalls;
            });
        } else {
            // Иначе красим/снимаем краску
            const pos = `${gridX},${gridY}`;
            setColoredCells(prev => {
                const newCells = new Set(prev);
                if (newCells.has(pos)) {
                    newCells.delete(pos);
                    setStatusMessage("Клетка очищена от краски!");
                } else {
                    newCells.add(pos);
                    setStatusMessage("Клетка раскрашена!");
                }
                return newCells;
            });
        }
    };

    const handleCanvasRightClick = (event) => {
        event.preventDefault();
        if (!editMode) {
            setStatusMessage("Правый клик не сработал: 'Режим рисования' не включён!");
            return;
        }

        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const gridX = Math.floor(x / cellSize) - 1;
        const gridY = Math.floor(y / cellSize) - 1;

        if (gridX < 0 || gridX >= width || gridY < 0 || gridY >= height) {
            setStatusMessage("Правый клик за пределами поля.");
            return;
        }

        const pos = `${gridX},${gridY}`;
        setMarkers(prev => {
            const newMarkers = {...prev};
            if (!newMarkers[pos]) {
                newMarkers[pos] = 1;
                setStatusMessage("Маркер добавлен!");
            } else {
                delete newMarkers[pos];
                setStatusMessage("Маркер убран.");
            }
            return newMarkers;
        });
    };

    // -----------------
    // Движение робота
    // -----------------
    const moveRobot = (direction) => {
        // Меняем позицию робота, проверяем стены и клэмпим в пределах поля
        setRobotPos(prevPos => {
            let newPos = {...prevPos};
            switch (direction) {
                case 'up':
                    if (
                        newPos.y > 0 &&
                        !walls.has(`${newPos.x},${newPos.y},${newPos.x + 1},${newPos.y}`) &&
                        !permanentWalls.has(`${newPos.x},${newPos.y},${newPos.x + 1},${newPos.y}`)
                    ) {
                        newPos.y -= 1;
                        setStatusMessage("Робот сдвинулся вверх!");
                    } else {
                        setStatusMessage("Робот не может пойти вверх (стена или край).");
                    }
                    break;
                case 'down':
                    if (
                        newPos.y < height - 1 &&
                        !walls.has(`${newPos.x},${newPos.y + 1},${newPos.x + 1},${newPos.y + 1}`) &&
                        !permanentWalls.has(`${newPos.x},${newPos.y + 1},${newPos.x + 1},${newPos.y + 1}`)
                    ) {
                        newPos.y += 1;
                        setStatusMessage("Робот сдвинулся вниз!");
                    } else {
                        setStatusMessage("Робот не может пойти вниз (стена или край).");
                    }
                    break;
                case 'left':
                    if (
                        newPos.x > 0 &&
                        !walls.has(`${newPos.x},${newPos.y},${newPos.x},${newPos.y + 1}`) &&
                        !permanentWalls.has(`${newPos.x},${newPos.y},${newPos.x},${newPos.y + 1}`)
                    ) {
                        newPos.x -= 1;
                        setStatusMessage("Робот пошёл влево!");
                    } else {
                        setStatusMessage("Робот не может пойти влево (стена или край).");
                    }
                    break;
                case 'right':
                    if (
                        newPos.x < width - 1 &&
                        !walls.has(`${newPos.x + 1},${newPos.y},${newPos.x + 1},${newPos.y + 1}`) &&
                        !permanentWalls.has(`${newPos.x + 1},${newPos.y},${newPos.x + 1},${newPos.y + 1}`)
                    ) {
                        newPos.x += 1;
                        setStatusMessage("Робот пошёл вправо!");
                    } else {
                        setStatusMessage("Робот не может пойти вправо (стена или край).");
                    }
                    break;
                default:
                    break;
            }

            // Клэмпим, если что-то пошло не так
            newPos.x = Math.min(Math.max(newPos.x, 0), width - 1);
            newPos.y = Math.min(Math.max(newPos.y, 0), height - 1);

            return newPos;
        });
    };

    // -----------------
    // Прокрутка колёсиком
    // -----------------
    const handleCanvasWheel = (event) => {
        event.preventDefault();
        event.stopPropagation();
        setCellSize(prev => {
            const newSize = Math.max(10, prev + (event.deltaY > 0 ? -5 : 5));
            // UX IMPROVEMENT: даём подсказку, если увеличили/уменьшили поле
            if (newSize > prev) {
                setStatusMessage("Поле стало крупнее!");
            } else if (newSize < prev) {
                setStatusMessage("Поле стало мельче!");
            }
            return newSize;
        });
    };

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

    // -----------------
    // Кнопки: маркеры, покраска
    // -----------------
    const putMarker = () => {
        const pos = `${robotPos.x},${robotPos.y}`;
        setMarkers(prev => {
            const newMarkers = {...prev};
            if (!newMarkers[pos]) {
                newMarkers[pos] = 1;
                setStatusMessage("Маркер поставлен прямо под роботом!");
            } else {
                setStatusMessage("Тут уже лежит маркер.");
            }
            return newMarkers;
        });
    };

    const pickMarker = () => {
        const pos = `${robotPos.x},${robotPos.y}`;
        setMarkers(prev => {
            const newMarkers = {...prev};
            if (newMarkers[pos]) {
                delete newMarkers[pos];
                setStatusMessage("Маркер поднят!");
            } else {
                setStatusMessage("Здесь нет маркера, чтобы поднять.");
            }
            return newMarkers;
        });
    };

    const paintCell = () => {
        const pos = `${robotPos.x},${robotPos.y}`;
        setColoredCells(prev => {
            const newCells = new Set(prev);
            if (!newCells.has(pos)) {
                newCells.add(pos);
                setStatusMessage("Клетка под роботом раскрашена!");
            } else {
                setStatusMessage("Клетка уже раскрашена, используйте 'Clear Cell' чтобы очистить.");
            }
            return newCells;
        });
    };

    const clearCell = () => {
        const pos = `${robotPos.x},${robotPos.y}`;
        setColoredCells(prev => {
            const newCells = new Set(prev);
            if (newCells.has(pos)) {
                newCells.delete(pos);
                setStatusMessage("Клетка очищена!");
            } else {
                setStatusMessage("Эта клетка и так не раскрашена.");
            }
            return newCells;
        });
    };

    // -----------------
    // Изменение ширины/высоты
    // -----------------
    const increaseWidth = () => {
        if (editMode) {
            setWidth(prev => {
                setStatusMessage("Поле стало шире!");
                return prev + 1;
            });
        } else {
            setStatusMessage("Изменять ширину можно только в режиме рисования!");
        }
    };

    const decreaseWidth = () => {
        if (editMode && width > 1) {
            setWidth(prev => {
                setStatusMessage("Поле стало уже.");
                return prev - 1;
            });
        } else {
            setStatusMessage("Изменять ширину можно только в режиме рисования!");
        }
    };

    const increaseHeight = () => {
        if (editMode) {
            setHeight(prev => {
                setStatusMessage("Поле стало выше!");
                return prev + 1;
            });
        } else {
            setStatusMessage("Изменять высоту можно только в режиме рисования!");
        }
    };

    const decreaseHeight = () => {
        if (editMode && height > 1) {
            setHeight(prev => {
                setStatusMessage("Поле стало ниже.");
                return prev - 1;
            });
        } else {
            setStatusMessage("Изменять высоту можно только в режиме рисования!");
        }
    };

    // -----------------
    // Переключение режима Edit Mode
    // -----------------
    const toggleEditMode = () => {
        setEditMode(prev => {
            const newMode = !prev;
            if (newMode) {
                setStatusMessage("Режим рисования ВКЛЮЧЁН: теперь можно ставить стены, красить клетки и ставить маркеры!");
            } else {
                setStatusMessage("Режим рисования ВЫКЛЮЧЕН: теперь холст только для просмотра и движения робота.");
            }
            return newMode;
        });
    };

    // -----------------
    // UX IMPROVEMENT: Модальное окно "Помощь"
    // -----------------
    const openHelp = () => {
        setHelpOpen(true);
    };

    const closeHelp = () => {
        setHelpOpen(false);
    };

    return (
        <div className="container">
            {/* Левая панель управления */}
            <Card className="card">
                <CardHeader
                    // UX IMPROVEMENT: Переименовал Controls в "Управление"
                    title={<Typography variant="h6" style={{textAlign: 'center'}}>Управление</Typography>}
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
                                Положить маркер
                            </Button>
                        </Grid>
                        <Grid item xs={6}>
                            <Button
                                variant="contained"
                                className="button full-width"
                                onClick={pickMarker}
                            >
                                Поднять маркер
                            </Button>
                        </Grid>
                        <Grid item xs={6}>
                            <Button
                                variant="contained"
                                className="button full-width"
                                onClick={paintCell}
                            >
                                Покрасить клетку
                            </Button>
                        </Grid>
                        <Grid item xs={6}>
                            <Button
                                variant="contained"
                                className="button full-width"
                                onClick={clearCell}
                            >
                                Очистить клетку
                            </Button>
                        </Grid>

                        {/* Режим рисования */}
                        <Grid item xs={12}>
                            <Button
                                variant="outlined"
                                className="button full-width-outlined"
                                onClick={toggleEditMode}
                            >
                                {editMode ? 'Выключить Режим рисования' : 'Включить Режим рисования'}
                            </Button>
                        </Grid>

                        {/* Изменение размеров поля */}
                        <Grid item xs={6}>
                            <Button
                                variant="contained"
                                className="button full-width"
                                onClick={increaseWidth}
                            >
                                Поле шире
                            </Button>
                        </Grid>
                        <Grid item xs={6}>
                            <Button
                                variant="contained"
                                className="button full-width"
                                onClick={decreaseWidth}
                            >
                                Поле уже
                            </Button>
                        </Grid>
                        <Grid item xs={6}>
                            <Button
                                variant="contained"
                                className="button full-width"
                                onClick={increaseHeight}
                            >
                                Поле выше
                            </Button>
                        </Grid>
                        <Grid item xs={6}>
                            <Button
                                variant="contained"
                                className="button full-width"
                                onClick={decreaseHeight}
                            >
                                Поле ниже
                            </Button>
                        </Grid>

                        {/* UX IMPROVEMENT: Кнопка "Помощь" */}
                        <Grid item xs={12}>
                            <Button
                                variant="contained"
                                color="secondary"
                                className="button full-width"
                                onClick={openHelp}
                            >
                                Помощь
                            </Button>
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>

            {/* Правая часть экрана: Canvas + статус */}
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
                {/* UX IMPROVEMENT: Статус-сообщение стало более дружелюбным */}
                <Card className="status-card">
                    <Typography variant="body2">{statusMessage}</Typography>
                    {/* Пример мини-"счётчиков": сколько маркеров, раскрашенных клеток */}
                    <Typography variant="body2" style={{marginTop: 8}}>
                        Маркеров на поле: {Object.keys(markers).length} <br/>
                        Раскрашенных клеток: {coloredCells.size}
                    </Typography>
                </Card>
            </div>

            {/* UX IMPROVEMENT: Модальное окно "Помощь" с инструкцией */}
            <Dialog open={helpOpen} onClose={closeHelp}>
                <DialogTitle>Как пользоваться симулятором?</DialogTitle>
                <DialogContent>
                    <Typography variant="body1" paragraph>
                        1. Кнопки со стрелками двигают Робота по полю, если перед ним нет стены.
                    </Typography>
                    <Typography variant="body1" paragraph>
                        2. «Включить Режим рисования» даёт возможность рисовать стены и раскрашивать клетки.
                        - Левый клик по границе клетки поставит/уберёт стену;
                        - Левый клик внутри клетки раскрашивает/очищает её;
                        - Правый клик в клетке ставит/убирает маркер.
                    </Typography>
                    <Typography variant="body1" paragraph>
                        3. Кнопки «Поле шире/уже/выше/ниже» меняют размер игрового поля
                        (работают только в Режиме рисования).
                    </Typography>
                    <Typography variant="body1" paragraph>
                        4. Колёсико мыши изменяет масштаб поля (увеличивает или уменьшает размер клеток).
                    </Typography>
                    <Typography variant="body1" paragraph>
                        5. Пробуйте экспериментировать: можете красить клетки, ставить маркеры и создавать лабиринты из
                        стен!
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={closeHelp} variant="contained" color="primary">
                        Понятно!
                    </Button>
                </DialogActions>
            </Dialog>
        </div>
    );
};

export default RobotSimulator;
