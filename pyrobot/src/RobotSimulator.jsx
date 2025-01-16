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
import {getHint} from './hints'; // <-- ИМПОРТ вашей функции для динамичных подсказок

/**
 * Компонент RobotSimulator, ориентированный на учащихся 8 классов.
 * - Включает режим рисования (Edit Mode) для расстановки стен, раскрашивания клеток, постановки маркеров.
 * - Есть кнопка "Помощь" (Help) с инструкцией.
 * - Робот можно передвигать кнопками-стрелками или перетаскиванием (drag & drop) в режиме рисования.
 * - Перетаскивание в реальном времени: робот сразу меняет клетку при движении мыши.
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

    // Динамичное сообщение статуса/подсказок
    const [statusMessage, setStatusMessage] = useState(
        // При желании можно сразу: getHint("initial", false)
        "Используйте кнопки слева, чтобы двигать Робота и рисовать на поле!"
    );

    // Размер одной клетки на Canvas
    const [cellSize, setCellSize] = useState(50);

    const canvasRef = useRef(null);

    // Модальное окно «Помощь»
    const [helpOpen, setHelpOpen] = useState(false);

    // Флаг, указывающий, что мы «перетаскиваем» робота в режиме рисования
    const [isDraggingRobot, setIsDraggingRobot] = useState(false);

    // -----------------------------------------
    // ИНИЦИАЛИЗАЦИЯ
    // -----------------------------------------
    useEffect(() => {
        setupPermanentWalls();

        // Если робот «оказался» за новой границей при изменении width/height, клэмпим обратно.
        setRobotPos(prev => {
            const clampedX = Math.min(Math.max(prev.x, 0), width - 1);
            const clampedY = Math.min(Math.max(prev.y, 0), height - 1);
            return {x: clampedX, y: clampedY};
        });
    }, [width, height]);

    useEffect(() => {
        // При изменениях перерисовываем поле
        const canvas = canvasRef.current;
        if (!canvas) return;

        drawField(canvas, {
            coloredCells,
            robotPos,
            markers,
            walls,
            permanentWalls,
            width,
            height,
            cellSize,
        });
    }, [robotPos, width, height, walls, coloredCells, markers, cellSize, permanentWalls]);

    /**
     * Создание постоянных (внешних) стен вокруг поля (верхняя/нижняя/левая/правая границы).
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

    // -----------------------------------------
    // ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ КООРДИНАТ
    // -----------------------------------------
    /**
     * Возвращает координаты (x, y) мыши внутри Canvas, с учётом offset'а в DOM.
     */
    const getCanvasCoords = (event) => {
        const canvas = canvasRef.current;
        if (!canvas) {
            return {x: null, y: null};
        }
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        return {x, y};
    };

    /**
     * Перевод координат (x,y) в клетку (gridX,gridY), учитывая смещение на 1 клетку в отрисовке.
     */
    const toGridCoords = (x, y) => {
        const gx = Math.floor(x / cellSize) - 1;
        const gy = Math.floor(y / cellSize) - 1;
        if (gx < 0 || gx >= width || gy < 0 || gy >= height) {
            return {gridX: null, gridY: null};
        }
        return {gridX: gx, gridY: gy};
    };

    // -----------------------------------------
    // ПЕРЕТАСКИВАНИЕ РОБОТА (в реальном времени)
    // -----------------------------------------
    const handleMouseDown = (event) => {
        // Сюда мы точно зашли только при left click (button = 0).

        if (!editMode) return;
        const {x, y} = getCanvasCoords(event);
        if (x === null || y === null) return;

        const {gridX, gridY} = toGridCoords(x, y);
        if (gridX === null || gridY === null) return;

        // Если попали по роботу => перетаскиваем
        if (gridX === robotPos.x && gridY === robotPos.y) {
            setIsDraggingRobot(true);
            // Подсказка для «зажали робота»
            setStatusMessage(getHint("moveRobotUp", editMode)); // Или любой подходящий ключ
            // или, если хотите специальный hint вроде "robotDragStart":
            // setStatusMessage(getHint("robotDragStart", editMode));
        } else {
            // Иначе - логика для стен или покраски
            handleCanvasClick(event);
        }
    };


    const handleMouseMove = (event) => {
        // Если НЕ перетаскиваем, ничего не делаем.
        if (!isDraggingRobot) return;

        const {x, y} = getCanvasCoords(event);
        if (x === null || y === null) return;

        const {gridX, gridY} = toGridCoords(x, y);
        if (gridX === null || gridY === null) {
            // Если курсор вышел за границы
            setStatusMessage("Курсор за пределами поля — робот не выйдет за край.");
            return;
        }

        // Обновляем позицию робота «на лету»
        const clampedX = Math.min(Math.max(gridX, 0), width - 1);
        const clampedY = Math.min(Math.max(gridY, 0), height - 1);
        setRobotPos({x: clampedX, y: clampedY});
    };

    const handleMouseUp = (event) => {
        if (!isDraggingRobot) return;
        // Прекращаем перетаскивание
        setIsDraggingRobot(false);
        // Тут можно дать подсказку, типа «Робот отпущен»
        setStatusMessage("Робот отпущен! Он остался в последней выбранной клетке.");
    };

    // -----------------------------------------
    // ЛОГИКА ДЛЯ ЛЕВОГО КЛИКА (стены и покраска)
    // -----------------------------------------
    const handleCanvasClick = (event) => {
        if (!editMode) {
            // Подсказка: режим редактирования выключен
            setStatusMessage(getHint("canvasLeftClickNoEdit", editMode));
            return;
        }

        const {x, y} = getCanvasCoords(event);
        if (x === null || y === null) return;

        // Рассчитываем, в какой клетке клик
        const gridX = Math.floor(x / cellSize) - 1;
        const gridY = Math.floor(y / cellSize) - 1;
        if (gridX < 0 || gridX >= width || gridY < 0 || gridY >= height) {
            setStatusMessage("Клик за пределами поля — действие не выполнено.");
            return;
        }

        const margin = 5;
        const xRemainder = x % cellSize;
        const yRemainder = y % cellSize;
        let wall = null;

        // Определяем, попали ли мы на границу клетки (чтобы поставить/убрать стену)
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

        // Если удалось вычислить «линию стены», проверяем, не постоянная ли
        if (wall && !permanentWalls.has(wall)) {
            setWalls(prev => {
                const newWalls = new Set(prev);
                if (newWalls.has(wall)) {
                    newWalls.delete(wall);
                    setStatusMessage(getHint("canvasLeftClickEditMode", editMode) + " Стена удалена.");
                } else {
                    newWalls.add(wall);
                    setStatusMessage(getHint("canvasLeftClickEditMode", editMode) + " Вы поставили стену!");
                }
                return newWalls;
            });
        } else {
            // Иначе красим или очищаем клетку
            const pos = `${gridX},${gridY}`;
            setColoredCells(prev => {
                const newCells = new Set(prev);
                if (newCells.has(pos)) {
                    newCells.delete(pos);
                    setStatusMessage(getHint("canvasLeftClickEditMode", editMode) + " Клетка очищена от краски!");
                } else {
                    newCells.add(pos);
                    setStatusMessage(getHint("canvasLeftClickEditMode", editMode) + " Клетка раскрашена!");
                }
                return newCells;
            });
        }
    };

    // -----------------------------------------
    // ПРАВЫЙ КЛИК: МАРКЕРЫ
    // -----------------------------------------
    const handleCanvasRightClick = (event) => {
        event.preventDefault();
        if (!editMode) {
            setStatusMessage(getHint("canvasRightClickNoEdit", editMode));
            return;
        }

        const {x, y} = getCanvasCoords(event);
        if (x === null || y === null) return;

        const gridX = Math.floor(x / cellSize) - 1;
        const gridY = Math.floor(y / cellSize) - 1;

        if (gridX < 0 || gridX >= width || gridY < 0 || gridY >= height) {
            setStatusMessage("Правый клик за пределами поля.");
            return;
        }

        const pos = `${gridX},${gridY}`;
        setMarkers((prev) => {
            const newMarkers = {...prev};
            if (!newMarkers[pos]) {
                newMarkers[pos] = 1;
                setStatusMessage(getHint("canvasRightClickEditMode", editMode) + " Маркер добавлен!");
            } else {
                delete newMarkers[pos];
                setStatusMessage(getHint("canvasRightClickEditMode", editMode) + " Маркер убран.");
            }
            return newMarkers;
        });
    };


    // -----------------------------------------
    // ДВИЖЕНИЕ РОБОТА КНОПКАМИ
    // -----------------------------------------
    const moveRobot = (direction) => {
        // Решаем, какой ключ действия использовать
        let actionKey = '';
        switch (direction) {
            case 'up':
                actionKey = 'moveRobotUp';
                break;
            case 'down':
                actionKey = 'moveRobotDown';
                break;
            case 'left':
                actionKey = 'moveRobotLeft';
                break;
            case 'right':
                actionKey = 'moveRobotRight';
                break;
            default:
                break;
        }

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
                    } else {
                        // При неудачном движении можно что-то другое сказать
                        setStatusMessage("Робот не может пойти вверх (стена или край).");
                        return prevPos;
                    }
                    break;
                case 'down':
                    if (
                        newPos.y < height - 1 &&
                        !walls.has(`${newPos.x},${newPos.y + 1},${newPos.x + 1},${newPos.y + 1}`) &&
                        !permanentWalls.has(`${newPos.x},${newPos.y + 1},${newPos.x + 1},${newPos.y + 1}`)
                    ) {
                        newPos.y += 1;
                    } else {
                        setStatusMessage("Робот не может пойти вниз (стена или край).");
                        return prevPos;
                    }
                    break;
                case 'left':
                    if (
                        newPos.x > 0 &&
                        !walls.has(`${newPos.x},${newPos.y},${newPos.x},${newPos.y + 1}`) &&
                        !permanentWalls.has(`${newPos.x},${newPos.y},${newPos.x},${newPos.y + 1}`)
                    ) {
                        newPos.x -= 1;
                    } else {
                        setStatusMessage("Робот не может пойти влево (стена или край).");
                        return prevPos;
                    }
                    break;
                case 'right':
                    if (
                        newPos.x < width - 1 &&
                        !walls.has(`${newPos.x + 1},${newPos.y},${newPos.x + 1},${newPos.y + 1}`) &&
                        !permanentWalls.has(`${newPos.x + 1},${newPos.y},${newPos.x + 1},${newPos.y + 1}`)
                    ) {
                        newPos.x += 1;
                    } else {
                        setStatusMessage("Робот не может пойти вправо (стена или край).");
                        return prevPos;
                    }
                    break;
                default:
                    return prevPos;
            }
            // Клэмпим
            newPos.x = Math.min(Math.max(newPos.x, 0), width - 1);
            newPos.y = Math.min(Math.max(newPos.y, 0), height - 1);
            return newPos;
        });

        if (actionKey) {
            // Достаём случайную подсказку (не повторяем дважды подряд)
            setStatusMessage(getHint(actionKey, editMode));
        }
    };

    // -----------------------------------------
    // ПРОКРУТКА КОЛЁСИКОМ (МАСШТАБ)
    // -----------------------------------------
    const handleCanvasWheel = (event) => {
        event.preventDefault();
        event.stopPropagation();
        setCellSize(prev => {
            const newSize = Math.max(10, prev + (event.deltaY > 0 ? -5 : 5));
            if (newSize > prev) {
                setStatusMessage(getHint("wheelZoomIn", editMode));
            } else if (newSize < prev) {
                setStatusMessage(getHint("wheelZoomOut", editMode));
            }
            return newSize;
        });
    };

    // Блокируем прокрутку страницы при колёсике над Canvas
    useEffect(() => {
        const canvas = canvasRef.current;
        if (canvas) {
            const preventScroll = (e) => e.preventDefault();
            canvas.addEventListener('wheel', preventScroll, {passive: false});
            return () => {
                canvas.removeEventListener('wheel', preventScroll);
            };
        }
    }, []);

    // -----------------------------------------
    // КНОПКИ: МАРКЕРЫ И ПОКРАСКА ПОД РОБОТОМ
    // -----------------------------------------
    const putMarker = () => {
        const pos = `${robotPos.x},${robotPos.y}`;
        setMarkers(prev => {
            const newMarkers = {...prev};
            if (!newMarkers[pos]) {
                newMarkers[pos] = 1;
            } else {
                // Если хотите запретить второй раз ставить, можно убрать
                setStatusMessage("Тут уже лежит маркер.");
                return prev;
            }
            return newMarkers;
        });
        setStatusMessage(getHint("putMarker", editMode));
    };

    const pickMarker = () => {
        const pos = `${robotPos.x},${robotPos.y}`;
        setMarkers(prev => {
            const newMarkers = {...prev};
            if (newMarkers[pos]) {
                delete newMarkers[pos];
            } else {
                setStatusMessage("Здесь нет маркера, чтобы поднять.");
                return prev;
            }
            return newMarkers;
        });
        setStatusMessage(getHint("pickMarker", editMode));
    };

    const paintCell = () => {
        const pos = `${robotPos.x},${robotPos.y}`;
        setColoredCells(prev => {
            const newCells = new Set(prev);
            if (!newCells.has(pos)) {
                newCells.add(pos);
            } else {
                setStatusMessage("Клетка уже раскрашена, используйте 'Очистить клетку' чтобы убрать краску.");
                return prev;
            }
            return newCells;
        });
        setStatusMessage(getHint("paintCell", editMode));
    };

    const clearCell = () => {
        const pos = `${robotPos.x},${robotPos.y}`;
        setColoredCells(prev => {
            const newCells = new Set(prev);
            if (newCells.has(pos)) {
                newCells.delete(pos);
            } else {
                setStatusMessage("Эта клетка и так не раскрашена.");
                return prev;
            }
            return newCells;
        });
        setStatusMessage(getHint("clearCell", editMode));
    };

    // -----------------------------------------
    // КНОПКИ: ИЗМЕНЕНИЕ РАЗМЕРОВ ПОЛЯ
    // -----------------------------------------
    const increaseWidth = () => {
        if (editMode) {
            setWidth(prev => {
                return prev + 1;
            });
            setStatusMessage(getHint("increaseWidth", editMode));
        } else {
            setStatusMessage("Изменять ширину можно только в режиме рисования!");
        }
    };

    const decreaseWidth = () => {
        if (editMode && width > 1) {
            setWidth(prev => {
                return prev - 1;
            });
            setStatusMessage(getHint("decreaseWidth", editMode));
        } else {
            setStatusMessage("Изменять ширину можно только в режиме рисования!");
        }
    };

    const increaseHeight = () => {
        if (editMode) {
            setHeight(prev => {
                return prev + 1;
            });
            setStatusMessage(getHint("increaseHeight", editMode));
        } else {
            setStatusMessage("Изменять высоту можно только в режиме рисования!");
        }
    };

    const decreaseHeight = () => {
        if (editMode && height > 1) {
            setHeight(prev => {
                return prev - 1;
            });
            setStatusMessage(getHint("decreaseHeight", editMode));
        } else {
            setStatusMessage("Изменять высоту можно только в режиме рисования!");
        }
    };

    // -----------------------------------------
    // ПЕРЕКЛЮЧЕНИЕ РЕЖИМА РИСОВАНИЯ
    // -----------------------------------------
    const toggleEditMode = () => {
        setEditMode(prev => {
            const newMode = !prev;
            if (newMode) {
                setStatusMessage(getHint("enterEditMode", newMode));
            } else {
                setStatusMessage(getHint("exitEditMode", newMode));
            }
            return newMode;
        });
    };

    // -----------------------------------------
    // МОДАЛЬНОЕ ОКНО ПОМОЩИ
    // -----------------------------------------
    const openHelp = () => setHelpOpen(true);
    const closeHelp = () => setHelpOpen(false);

    // -----------------------------------------
    // ВЕРСТКА JSX
    // -----------------------------------------
    return (
        <div className="container">
            {/* Левая панель управления */}
            <Card className="card">
                <CardHeader
                    title={<Typography variant="h6" style={{textAlign: 'center'}}>Управление</Typography>}
                />
                <CardContent>
                    <Grid container spacing={2} alignItems="center" justifyContent="center">
                        {/* Кнопки движения робота */}
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

                        {/* Кнопки с маркерами и покраской */}
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

                        {/* Кнопка "Помощь" */}
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

                        // Перехватываем mouseDown, mouseMove, mouseUp
                        onMouseDown={(e) => {
                            if (e.button !== 0) return; // только левая кнопка!
                            handleMouseDown(e);
                        }}
                        onMouseMove={handleMouseMove}
                        onMouseUp={handleMouseUp}

                        onContextMenu={handleCanvasRightClick}
                        onWheel={handleCanvasWheel}
                    />
                </Card>
                <Card className="status-card">
                    <Typography variant="body2">{statusMessage}</Typography>
                    <Typography variant="body2" style={{marginTop: 8}}>
                        Маркеров на поле: {Object.keys(markers).length} <br/>
                        Раскрашенных клеток: {coloredCells.size}
                    </Typography>
                </Card>
            </div>

            {/* Модальное окно "Помощь" */}
            <Dialog open={helpOpen} onClose={closeHelp}>
                <DialogTitle>Как пользоваться симулятором?</DialogTitle>
                <DialogContent>
                    <Typography variant="body1" paragraph>
                        1. Кнопки со стрелками двигают Робота по полю, если перед ним нет стены.
                    </Typography>
                    <Typography variant="body1" paragraph>
                        2. «Включить Режим рисования» даёт возможность рисовать стены и раскрашивать клетки:
                        <br/>• Левый клик по границе клетки — поставить/убрать стену;
                        <br/>• Левый клик внутри клетки — раскрасить/очистить клетку;
                        <br/>• Правый клик в клетке — поставить/убрать маркер;
                        <br/>• А также перетаскивать Робота (зажать мышь на роботе и двигать).
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
