import React, {useCallback, useEffect, useRef, useState} from 'react';

import {
    Button,
    Card,
    CardContent,
    CardHeader,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Grid,
    Typography
} from '@mui/material';
import {ChevronDown, ChevronLeft, ChevronRight, ChevronUp} from 'lucide-react';

import './styles.css';
import {drawField} from './canvasDrawing';
import {getHint} from './hints'; // <-- Импорт функции для случайных подсказок


/**
 * Компонент RobotSimulator — симулятор поля с «Роботом», стенами, маркерами и возможностью раскрашивать клетки.
 *
 * Что умеет:
 * - В «режиме рисования» (editMode = true) можно:
 *   • Кликать левой кнопкой мыши для постройки стен или покраски клеток.
 *   • Кликать правой кнопкой мыши, чтобы ставить/убирать маркер.
 *   • Перетаскивать (drag & drop) робота, зажав левую кнопку мыши, если кликнули по самому роботу.
 * - В «обычном режиме» (editMode = false) можно только двигать робота кнопками стрелок (вверх, вниз, влево, вправо).
 * - Можно менять размер поля (ширину и высоту) в режиме рисования.
 * - Можно увеличивать/уменьшать масштаб колёсиком мыши (wheel).
 *
 * Целевая аудитория: школьники (8 класс).
 * Поэтому добавлены максимально дружелюбные подсказки и понятные комментарии.
 */
const RobotSimulator = () => {
    /**
     * @constant {number} width     - Текущая ширина поля (в клетках)
     * @constant {number} height    - Текущая высота поля (в клетках)
     * @constant {boolean} editMode - Режим рисования (true/false)
     * @constant {object} robotPos  - Позиция робота {x, y}, где x, y — индексы клетки
     * @constant {Set<string>} walls - Набор «стен», каждая стена описывается строкой "x1,y1,x2,y2"
     * @constant {Set<string>} permanentWalls - То же, но постоянные стены (границы поля)
     * @constant {object} markers   - Объект с маркерами: ключ — "x,y", значение — любое (напр. 1)
     * @constant {Set<string>} coloredCells - Набор раскрашенных клеток (каждая: "x,y")
     * @constant {string} statusMessage - Текущее сообщение/подсказка пользователю
     * @constant {number} cellSize  - Размер (в пикселях) одной клетки
     * @constant {boolean} isDraggingRobot - Флаг: перетаскивают ли сейчас робота
     */
    const [width, setWidth] = useState(7);
    const [height, setHeight] = useState(7);
    const [editMode, setEditMode] = useState(false);
    const [robotPos, setRobotPos] = useState({x: 0, y: 0});
    const [walls, setWalls] = useState(new Set());
    const [permanentWalls, setPermanentWalls] = useState(new Set());
    const [markers, setMarkers] = useState({}); // { "x,y": 1 }
    const [coloredCells, setColoredCells] = useState(new Set());
    const [statusMessage, setStatusMessage] = useState("Используйте кнопки слева, чтобы двигать Робота и рисовать на поле!");
    const [cellSize, setCellSize] = useState(50);
    const [isDraggingRobot, setIsDraggingRobot] = useState(false);


    // Ссылка на Canvas
    const canvasRef = useRef(null);

    // Новые ref и состояния для импорта
    const fileInputRef = useRef(null);

    // Новые обработчики импорта
    const handleImportField = () => {
        fileInputRef.current.click();
    };

    // Добавляем функцию сброса состояний
    const resetFieldState = useCallback(() => {
        setRobotPos({x: 0, y: 0});
        setWalls(new Set());
        setColoredCells(new Set());
        setMarkers({});
        setWidth(7);
        setHeight(7);
    }, []);

    const handleFileChange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        try {
            const content = await file.text();
            parseAndApplyFieldFile(content);
            setStatusMessage("Обстановка успешно импортирована!");
        } catch (error) {
            setStatusMessage("Ошибка импорта: " + error.message);
        }
    };

    // Парсер файла .fil
    const parseAndApplyFieldFile = (content) => {
        try {
            // Полный сброс перед загрузкой новых данных
            resetFieldState();

            const lines = content.split('\n').filter(line => !line.startsWith(';') && line.trim() !== '');

            // Размеры поля
            const [width, height] = lines[0].split(/\s+/).map(Number);
            setWidth(width);
            setHeight(height);

            // Позиция робота
            const [robotX, robotY] = lines[1].split(/\s+/).map(Number);
            setRobotPos({x: robotX, y: robotY});

            // Временные хранилища новых данных
            const newWalls = new Set();
            const newColored = new Set();
            const newMarkers = {};

            // Обработка клеток
            for (let i = 2; i < lines.length; i++) {
                const parts = lines[i].split(/\s+/);
                const x = parseInt(parts[0]);
                const y = parseInt(parts[1]);
                const wall = parts[2];
                const color = parts[3];
                const point = parts[8];

                if (color === '1') newColored.add(`${x},${y}`);
                if (point === '1') newMarkers[`${x},${y}`] = 1;

                const walls = parseWallCode(Number(wall), x, y);
                walls.forEach(w => newWalls.add(w));
            }

            // Применение новых данных
            setWalls(newWalls);
            setColoredCells(newColored);
            setMarkers(newMarkers);

        } catch (error) {
            setStatusMessage("Ошибка парсинга файла: " + error.message);
            // В случае ошибки - полный сброс
            resetFieldState();
        }
    };


    const parseWallCode = (code, x, y) => {
        const walls = [];
        if (code & 8) walls.push(`${x},${y},${x + 1},${y}`);    // Верх
        if (code & 4) walls.push(`${x + 1},${y},${x + 1},${y + 1}`); // Право
        if (code & 2) walls.push(`${x},${y + 1},${x + 1},${y + 1}`); // Низ
        if (code & 1) walls.push(`${x},${y},${x},${y + 1}`);    // Лево
        return walls;
    };

    // Состояние для модального окна «Помощь»
    const [helpOpen, setHelpOpen] = useState(false);

    // Добавлены состояния
    const [code, setCode] = useState('');
    const [isRunning, setIsRunning] = useState(false);

    // Обработчики действий
    const handleClearCode = useCallback(() => {
        setCode('');
        setStatusMessage('Код программы очищен');
    }, []);

    const handleStart = useCallback(() => {
        if (!code.trim()) {
            setStatusMessage('Ошибка: программа пустая');
            return;
        }
        setIsRunning(true);
        setStatusMessage('Программа выполняется...');
    }, [code]);

    const handleStop = useCallback(() => {
        setIsRunning(false);
        setStatusMessage('Выполнение прервано');
    }, []);


    /**
     * Создаём постоянные стены (границы поля):
     * - Верх/низ (горизонтальные)
     * - Лево/право (вертикальные)
     */
    const setupPermanentWalls = useCallback(() => {
        // При изменении ширины/высоты пересоздаём постоянные стены
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
    }, [width, height]);
// ^^^ Обратите внимание: [width, height], т.к. внутри функция
//    использует width, height

// useEffect:
    useEffect(() => {
        setupPermanentWalls();
        // какие-то ещё действия...
    }, [width, height, setupPermanentWalls, resetFieldState]);

    /**
     * useEffect: При изменении ширины/высоты пересоздаём постоянные стены
     * и клэмпим (ограничиваем) координаты робота, чтобы он не вышел за границы.
     */
    useEffect(() => {
        setupPermanentWalls();

        // Если робот оказался за новой границей (напр. уменьшили width),
        // сдвигаем его внутрь
        setRobotPos(prev => {
            const clampedX = Math.min(Math.max(prev.x, 0), width - 1);
            const clampedY = Math.min(Math.max(prev.y, 0), height - 1);
            return {x: clampedX, y: clampedY};
        });
    }, [width, height, setupPermanentWalls]);

    /**
     * useEffect: При любом изменении ключевых переменных (поз. робота, стены, маркеры и т. д.)
     * перерисовываем Canvas с помощью drawField.
     */
    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        drawField(canvas, {
            coloredCells, robotPos, markers, walls, permanentWalls, width, height, cellSize,
        });
    }, [robotPos, width, height, walls, coloredCells, markers, cellSize, permanentWalls]);


    /**
     * Функция возвращает координаты мыши (x, y) внутри Canvas,
     * учитывая отступ холста в окне браузера.
     *
     * @param {MouseEvent} event - Событие мыши
     * @return {{x: number|null, y: number|null}}
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
     * Переводит координаты холста (x, y) в координаты клеток (gridX, gridY).
     * У нас есть сдвиг на 1 клетку (т. к. в drawField поле рисуется,
     * начиная с (1,1)), поэтому вычитаем 1 клетку, делая (x / cellSize) - 1.
     *
     * @param {number} x - Координата X на холсте
     * @param {number} y - Координата Y на холсте
     * @return {{gridX: number|null, gridY: number|null}}
     */
    const toGridCoords = (x, y) => {
        const gx = Math.floor(x / cellSize) - 1; // -1 из-за отступа поля
        const gy = Math.floor(y / cellSize) - 1;
        if (gx < 0 || gx >= width || gy < 0 || gy >= height) {
            return {gridX: null, gridY: null};
        }
        return {gridX: gx, gridY: gy};
    };

    // ---------------------------------------------------------
    // ПЕРЕТАСКИВАНИЕ РОБОТА: onMouseDown / onMouseMove / onMouseUp
    // ---------------------------------------------------------
    /**
     * Нажали левую кнопку мыши на Canvas:
     * - Если попали в робота и editMode=true, начинаем перетаскивать робота (isDraggingRobot=true).
     * - Если не попали в робота, вызываем логику handleCanvasClick (стены/покраска).
     *
     * @param {MouseEvent} event
     */
    const handleMouseDown = (event) => {
        if (!editMode) return; // только в режиме рисования
        const {x, y} = getCanvasCoords(event);
        if (x === null || y === null) return;

        const {gridX, gridY} = toGridCoords(x, y);
        if (gridX === null || gridY === null) return;

        // Если кликнули именно по роботу — начинаем перетаскивать
        if (gridX === robotPos.x && gridY === robotPos.y) {
            setIsDraggingRobot(true);
            // Например, покажем какую-нибудь подсказку (ключ "moveRobotUp" заменён на любой нужный):
            setStatusMessage(getHint("moveRobotUp", editMode));
        } else {
            // Иначе — логика стен/покраски
            handleCanvasClick(event);
        }
    };

    /**
     * Двигаем мышь при зажатой левой кнопке:
     * - Если isDraggingRobot=true, робот следует за курсором в реальном времени.
     *
     * @param {MouseEvent} event
     */
    const handleMouseMove = (event) => {
        if (!isDraggingRobot) return; // если не перетаскиваем — ничего

        const {x, y} = getCanvasCoords(event);
        if (x === null || y === null) return;

        const {gridX, gridY} = toGridCoords(x, y);
        if (gridX === null || gridY === null) {
            setStatusMessage("Курсор за пределами поля — робот не выйдет за край.");
            return;
        }

        // Обновляем позицию робота прямо во время движения
        const clampedX = Math.min(Math.max(gridX, 0), width - 1);
        const clampedY = Math.min(Math.max(gridY, 0), height - 1);
        setRobotPos({x: clampedX, y: clampedY});
    };

    /**
     * Отпустили левую кнопку:
     * - Если перетаскивали робота, завершаем перетаскивание.
     *
     * @param {MouseEvent} event
     */
    const handleMouseUp = (event) => {
        if (!isDraggingRobot) return;
        setIsDraggingRobot(false);
        // Можем показать простое сообщение
        setStatusMessage("Робот отпущен! Он остался в последней выбранной клетке.");
    };

    // ---------------------------------------------------------
    // ЛОГИКА ЛЕВОГО КЛИКА (стены/покраска) — handleCanvasClick
    // ---------------------------------------------------------
    /**
     * Функция обрабатывает обычный левый клик в режиме рисования:
     * - Смотрит, близко ли к границе клетки (тогда ставим/убираем стену)
     * - Иначе красим или очищаем клетку
     *
     * @param {MouseEvent} event
     */
    const handleCanvasClick = (event) => {
        if (!editMode) {
            // Если режим редактирования выключен:
            setStatusMessage(getHint("canvasLeftClickNoEdit", editMode));
            return;
        }

        const {x, y} = getCanvasCoords(event);
        if (x === null || y === null) return;

        // Определяем координаты в клетках
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

        // Проверяем, не кликаем ли у границы (ставим стену)
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

        if (wall && !permanentWalls.has(wall)) {
            setWalls(prev => {
                const newWalls = new Set(prev);
                if (newWalls.has(wall)) {
                    newWalls.delete(wall);
                    // Объединяем случайную подсказку + конкретное действие
                    setStatusMessage(getHint("canvasLeftClickEditMode", editMode) + " Стена удалена.");
                } else {
                    newWalls.add(wall);
                    setStatusMessage(getHint("canvasLeftClickEditMode", editMode) + " Вы поставили стену!");
                }
                return newWalls;
            });
        } else {
            // Иначе красим/очищаем
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

    // ---------------------------------------------------------
    // ПРАВЫЙ КЛИК (onContextMenu): УСТАНОВКА / УБИРАНИЕ МАРКЕРА
    // ---------------------------------------------------------
    /**
     * Правый клик по холсту:
     * - Ставим/убираем маркер в клетке, если editMode=true
     *
     * @param {MouseEvent} event
     */
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

    // ---------------------------------------------------------
    // ДВИЖЕНИЕ РОБОТА ПО КНОПКАМ
    // ---------------------------------------------------------
    /**
     * Функция, вызываемая при нажатии на кнопки со стрелками. Двигает робота,
     * если нет стены и не край поля. Выбирает случайную подсказку из hints.js.
     *
     * @param {'up'|'down'|'left'|'right'} direction
     */
    const moveRobot = (direction) => {
        // Определяем ключ действия для hints
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
                    if (newPos.y > 0 && !walls.has(`${newPos.x},${newPos.y},${newPos.x + 1},${newPos.y}`) && !permanentWalls.has(`${newPos.x},${newPos.y},${newPos.x + 1},${newPos.y}`)) {
                        newPos.y -= 1;
                    } else {
                        setStatusMessage("Робот не может пойти вверх (стена или край).");
                        return prevPos;
                    }
                    break;
                case 'down':
                    if (newPos.y < height - 1 && !walls.has(`${newPos.x},${newPos.y + 1},${newPos.x + 1},${newPos.y + 1}`) && !permanentWalls.has(`${newPos.x},${newPos.y + 1},${newPos.x + 1},${newPos.y + 1}`)) {
                        newPos.y += 1;
                    } else {
                        setStatusMessage("Робот не может пойти вниз (стена или край).");
                        return prevPos;
                    }
                    break;
                case 'left':
                    if (newPos.x > 0 && !walls.has(`${newPos.x},${newPos.y},${newPos.x},${newPos.y + 1}`) && !permanentWalls.has(`${newPos.x},${newPos.y},${newPos.x},${newPos.y + 1}`)) {
                        newPos.x -= 1;
                    } else {
                        setStatusMessage("Робот не может пойти влево (стена или край).");
                        return prevPos;
                    }
                    break;
                case 'right':
                    if (newPos.x < width - 1 && !walls.has(`${newPos.x + 1},${newPos.y},${newPos.x + 1},${newPos.y + 1}`) && !permanentWalls.has(`${newPos.x + 1},${newPos.y},${newPos.x + 1},${newPos.y + 1}`)) {
                        newPos.x += 1;
                    } else {
                        setStatusMessage("Робот не может пойти вправо (стена или край).");
                        return prevPos;
                    }
                    break;
                default:
                    return prevPos;
            }
            // Ограничиваем внутри поля
            newPos.x = Math.min(Math.max(newPos.x, 0), width - 1);
            newPos.y = Math.min(Math.max(newPos.y, 0), height - 1);
            return newPos;
        });

        if (actionKey) {
            setStatusMessage(getHint(actionKey, editMode));
        }
    };

    // ---------------------------------------------------------
    // ПРОКРУТКА КОЛЁСИКОМ (МАСШТАБИРОВАНИЕ)
    // ---------------------------------------------------------
    /**
     * При прокрутке колёсика (wheel) на Canvas:
     * - Увеличиваем/уменьшаем cellSize (не меньше 10)
     * - Выбираем подсказку (wheelZoomIn/wheelZoomOut)
     *
     * @param {WheelEvent} event
     */
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

    /**
     * useEffect: Блокируем прокрутку всей страницы при прокрутке на канвасе.
     */
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

    // ---------------------------------------------------------
    // КНОПКИ МАРКЕРОВ И ПОКРАСКИ ПОД РОБОТОМ
    // ---------------------------------------------------------
    /**
     * Ставит маркер под роботом, если там нет маркера.
     */
    const putMarker = () => {
        const pos = `${robotPos.x},${robotPos.y}`;
        setMarkers(prev => {
            const newMarkers = {...prev};
            if (!newMarkers[pos]) {
                newMarkers[pos] = 1;
            } else {
                setStatusMessage("Тут уже лежит маркер.");
                return prev;
            }
            return newMarkers;
        });
        setStatusMessage(getHint("putMarker", editMode));
    };

    /**
     * Убирает маркер из-под робота, если он там есть.
     */
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

    /**
     * Красит клетку под роботом (если не покрашена).
     */
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

    /**
     * Убирает краску с клетки, где стоит робот (если она покрашена).
     */
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

    // ---------------------------------------------------------
    // КНОПКИ ИЗМЕНЕНИЯ РАЗМЕРОВ ПОЛЯ
    // ---------------------------------------------------------
    /**
     * Увеличивает ширину поля на 1, если editMode=true.
     */
    const increaseWidth = () => {
        if (editMode) {
            setWidth(prev => prev + 1);
            setStatusMessage(getHint("increaseWidth", editMode));
        } else {
            setStatusMessage("Изменять ширину можно только в режиме рисования!");
        }
    };

    /**
     * Уменьшает ширину поля на 1, если editMode=true.
     */
    const decreaseWidth = () => {
        if (editMode && width > 1) {
            setWidth(prev => prev - 1);
            setStatusMessage(getHint("decreaseWidth", editMode));
        } else {
            setStatusMessage("Изменять ширину можно только в режиме рисования!");
        }
    };

    /**
     * Увеличивает высоту поля на 1, если editMode=true.
     */
    const increaseHeight = () => {
        if (editMode) {
            setHeight(prev => prev + 1);
            setStatusMessage(getHint("increaseHeight", editMode));
        } else {
            setStatusMessage("Изменять высоту можно только в режиме рисования!");
        }
    };

    /**
     * Уменьшает высоту поля на 1, если editMode=true.
     */
    const decreaseHeight = () => {
        if (editMode && height > 1) {
            setHeight(prev => prev - 1);
            setStatusMessage(getHint("decreaseHeight", editMode));
        } else {
            setStatusMessage("Изменять высоту можно только в режиме рисования!");
        }
    };

    // ---------------------------------------------------------
    // РЕЖИМ РИСОВАНИЯ
    // ---------------------------------------------------------
    /**
     * Переключает editMode (включить/выключить) и выводит соответствующую подсказку.
     */
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

    // ---------------------------------------------------------
    // МОДАЛЬНОЕ ОКНО «ПОМОЩЬ»
    // ---------------------------------------------------------
    /**
     * Открывает диалоговое окно (модальное) с инструкцией.
     */
    const openHelp = () => setHelpOpen(true);

    /**
     * Закрывает диалоговое окно (модальное).
     */
    const closeHelp = () => setHelpOpen(false);

    // ---------------------------------------------------------
    // JSX (верстка) — то, что отрисовывается на странице
    // ---------------------------------------------------------
    return (<div className="container">


        {/* Блок редактора кода (слева) */}
        <Card className="card code-editor">
    <textarea
        className="code-input"
        placeholder="// Программа управления роботом..."
        value={code}
        onChange={(e) => setCode(e.target.value)}
    />

            {/* Контейнер для кнопок */}
            <div className="editor-controls">
                <Button
                    variant="contained"
                    color="secondary"
                    onClick={handleClearCode}
                    fullWidth
                >
                    Очистить
                </Button>
                <Button
                    variant="contained"
                    color="error"
                    onClick={handleStop}
                    disabled={!isRunning}
                    fullWidth
                >
                    Стоп
                </Button>
                <Button
                    variant="contained"
                    color="success"
                    onClick={handleStart}
                    disabled={isRunning}
                    fullWidth
                >
                    Пуск
                </Button>
            </div>
        </Card>

        {/* Левая панель управления */}
        <Card className="card">
            <CardHeader
                title={<Typography variant="h6" style={{textAlign: 'center'}}>Управление</Typography>}
            />
            <CardContent>
                <Grid container spacing={2} alignItems="center" justifyContent="center">
                    {/* Кнопки движения робота (стрелки) */}
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

                    {/* Кнопки для маркеров и покраски (под роботом) */}
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

                    {/* Переключатель режима рисования */}
                    <Grid item xs={12}>
                        <Button
                            variant="outlined"
                            className="button full-width-outlined"
                            onClick={toggleEditMode}
                        >
                            {editMode ? 'Выключить Режим рисования' : 'Включить Режим рисования'}
                        </Button>
                    </Grid>

                    {/* Кнопки изменения размеров поля */}
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

                    <Grid item xs={12}>
                        <Button
                            variant="contained"
                            color="secondary"
                            className="button full-width"
                            onClick={handleImportField}
                        >
                            Импортировать обстановку
                        </Button>
                        <input
                            type="file"
                            ref={fileInputRef}
                            style={{display: 'none'}}
                            accept=".fil"
                            onChange={handleFileChange}
                        />
                    </Grid>
                </Grid>
            </CardContent>
        </Card>

        {/* Правая часть экрана: Canvas + Статус/Подсказки */}
        <div className="field-area">
            <Card className="card-controls">
                <div className="field-container">
                    <div className="canvas-wrapper">
                        <canvas
                            ref={canvasRef}
                            width={(width + 2) * cellSize}
                            height={(height + 2) * cellSize}
                            className={editMode ? 'edit-mode' : ''}

                            // Важно: onMouseDown вместо onClick, чтобы обрабатывать левую кнопку
                            onMouseDown={(e) => {
                                if (e.button !== 0) return; // только левая кнопка!
                                handleMouseDown(e);
                            }}
                            onMouseMove={handleMouseMove}
                            onMouseUp={handleMouseUp}

                            onContextMenu={handleCanvasRightClick}
                            onWheel={handleCanvasWheel}
                        />
                    </div>
                </div>
            </Card>
            <Card className="status-card">
                {/* Здесь отображаем последнее сообщение (подсказку) */}
                <Typography variant="body2">{statusMessage}</Typography>
                <Typography variant="body2" style={{marginTop: 8}}>
                    Маркеров на поле: {Object.keys(markers).length} <br/>
                    Раскрашенных клеток: {coloredCells.size}
                </Typography>
            </Card>
        </div>

        {/* Модальное окно "Помощь" с инструкциями */}
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
    </div>);
};

export default RobotSimulator;