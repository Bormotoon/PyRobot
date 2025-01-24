// frontend/src/components/RobotSimulator.jsx

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
import Editor from 'react-simple-code-editor';
import Prism from 'prismjs';
import 'prismjs/themes/prism.css'; // Импорт темы Prism
import './styles.css';
import {drawField} from './canvasDrawing';
import {getHint} from './hints'; // Импорт функции для случайных подсказок

// Определение языка КУМИР для Prism.js
Prism.languages.kumir = {
    'keyword': /\b(использовать|Робот|алг|нач|кон|влево|вправо|вверх|вниз|закрасить|если|иначе|для|пока|температура|радиация)\b/g,
    'comment': /#.*/g,
    'string': /".*?"/g,
    'number': /\b\d+\b/g,
    'operator': /\b(==|!=|<=|>=|<|>|\+|\-|\*|\/)\b/g,
};

const RobotSimulator = () => {
    // Состояния
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

    // Ссылка и функции для импорта файлов .fil
    const fileInputRef = useRef(null);

    const handleImportField = () => {
        fileInputRef.current.click();
    };

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

    const parseAndApplyFieldFile = (content) => {
        try {
            // Полный сброс перед загрузкой
            resetFieldState();

            const lines = content.split('\n').filter(line => !line.startsWith(';') && line.trim() !== '');

            // Первая строка: размеры поля
            const [widthFile, heightFile] = lines[0].split(/\s+/).map(Number);
            setWidth(widthFile);
            setHeight(heightFile);

            // Вторая строка: позиция робота
            const [robotX, robotY] = lines[1].split(/\s+/).map(Number);
            setRobotPos({x: robotX, y: robotY});

            const newWalls = new Set();
            const newColored = new Set();
            const newMarkers = {};

            // Начиная с третьей строки – данные клеток
            for (let i = 2; i < lines.length; i++) {
                const parts = lines[i].split(/\s+/);
                const x = parseInt(parts[0]);
                const y = parseInt(parts[1]);
                const wallCode = parts[2];
                const color = parts[3];
                const point = parts[8];

                if (color === '1') newColored.add(`${x},${y}`);
                if (point === '1') newMarkers[`${x},${y}`] = 1;

                const wallsParsed = parseWallCode(Number(wallCode), x, y);
                wallsParsed.forEach(w => newWalls.add(w));
            }

            setWalls(newWalls);
            setColoredCells(newColored);
            setMarkers(newMarkers);

        } catch (error) {
            setStatusMessage("Ошибка парсинга файла: " + error.message);
            resetFieldState();
        }
    };

    const parseWallCode = (code, x, y) => {
        const wallsArr = [];
        if (code & 8) wallsArr.push(`${x},${y},${x + 1},${y}`);       // Верх
        if (code & 4) wallsArr.push(`${x + 1},${y},${x + 1},${y + 1}`); // Право
        if (code & 2) wallsArr.push(`${x},${y + 1},${x + 1},${y + 1}`); // Низ
        if (code & 1) wallsArr.push(`${x},${y},${x},${y + 1}`);       // Лево
        return wallsArr;
    };

    // Модальное окно "Помощь"
    const [helpOpen, setHelpOpen] = useState(false);

    // Состояния для кода и управления выполнением
    const [code, setCode] = useState(`использовать Робот

алг
нач
  вправо
  вниз
  влево
  вверх
  закрасить
кон`);
    const [isRunning, setIsRunning] = useState(false);

    // Подсветка синтаксиса
    const highlightCode = useCallback((code) => {
        return Prism.highlight(code, Prism.languages.kumir, 'kumir');
    }, []);

    // Очистка кода
    const handleClearCode = useCallback(() => {
        setCode('');
        setStatusMessage('Код программы очищен');
    }, []);

    // Запуск (пуск)
    const handleStart = useCallback(async () => {
        if (!code.trim()) {
            setStatusMessage('Ошибка: программа пустая');
            return;
        }

        try {
            const response = await fetch('http://localhost:5000/execute', {
                method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({code}),
            });

            // Если сервер вернул ошибку (4xx/5xx)
            if (!response.ok) {
                setStatusMessage(`HTTP-ошибка: ${response.status}`);
                return;
            }

            // Пытаемся распарсить JSON
            const data = await response.json();

            // Смотрим поле success из ответа сервера
            if (data.success) {
                // У нас есть robotPos, walls, markers, coloredCells
                setRobotPos(data.robotPos);
                setWalls(new Set(data.walls));
                setColoredCells(new Set(data.coloredCells));
                setMarkers(data.markers);

                setStatusMessage(data.message || 'Код выполнен успешно!');
                // Если вы используете isRunning — сбросите его, чтобы можно было жать ПУСК ещё раз
                setIsRunning(false);
            } else {
                // Если success=false
                setStatusMessage(`Ошибка: ${data.message}`);
            }
        } catch (error) {
            // Сюда попадёт, если реально нет связи с сервером, таймаут и т.п.
            setStatusMessage('Ошибка соединения с сервером');
            console.error('Ошибка при отправке запроса:', error);
        }
    }, [code]);


    // Сброс симулятора
    const handleReset = useCallback(async () => {
        try {
            const response = await fetch('http://localhost:5000/reset', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
            });
            const result = await response.json();

            if (response.ok && result.success) {
                setRobotPos({x: 0, y: 0});
                setWalls(new Set());
                setColoredCells(new Set());
                setMarkers({});
                setWidth(7);
                setHeight(7);
                setStatusMessage(result.message);
                setCode(`использовать Робот

алг
нач
  # Ваши команды здесь
кон`);
                setIsRunning(false);
            } else {
                setStatusMessage(`Ошибка: ${result.message}`);
            }
        } catch (error) {
            setStatusMessage('Ошибка соединения с сервером');
            console.error('Ошибка при отправке запроса:', error);
        }
    }, []);

    // Создание постоянных стен (границ поля)
    const setupPermanentWalls = useCallback(() => {
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

    // Пересоздаём постоянные стены при изменении width/height
    useEffect(() => {
        setupPermanentWalls();
    }, [width, height, setupPermanentWalls]);

    // Клэмпим координаты робота при изменении размеров поля
    useEffect(() => {
        setupPermanentWalls();

        setRobotPos(prev => {
            const clampedX = Math.min(Math.max(prev.x, 0), width - 1);
            const clampedY = Math.min(Math.max(prev.y, 0), height - 1);
            return {x: clampedX, y: clampedY};
        });
    }, [width, height, setupPermanentWalls]);

    // Рендерим поле при каждом изменении walls, robotPos, markers, и т. д.
    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        drawField(canvas, {
            coloredCells, robotPos, markers, walls, permanentWalls, width, height, cellSize,
        });
    }, [robotPos, width, height, walls, coloredCells, markers, cellSize, permanentWalls]);

    // Функция для получения координат мыши внутри Canvas
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

    // Перевод координат холста (x, y) в координаты сетки (gridX, gridY)
    const toGridCoords = (x, y) => {
        const gx = Math.floor(x / cellSize) - 1; // -1 из-за отступа
        const gy = Math.floor(y / cellSize) - 1;
        if (gx < 0 || gx >= width || gy < 0 || gy >= height) {
            return {gridX: null, gridY: null};
        }
        return {gridX: gx, gridY: gy};
    };

    // ---------------------------------------------------------
    // ПЕРЕТАСКИВАНИЕ РОБОТА
    // ---------------------------------------------------------
    const handleMouseDown = (event) => {
        if (!editMode) return;
        const {x, y} = getCanvasCoords(event);
        if (x === null || y === null) return;

        const {gridX, gridY} = toGridCoords(x, y);
        if (gridX === null || gridY === null) return;

        // Если клик именно по роботу
        if (gridX === robotPos.x && gridY === robotPos.y) {
            setIsDraggingRobot(true);
            setStatusMessage(getHint("moveRobotUp", editMode));
        } else {
            // Иначе — ставим/убираем стены или красим клетку
            handleCanvasClick(event);
        }
    };

    const handleMouseMove = (event) => {
        if (!isDraggingRobot) return;

        const {x, y} = getCanvasCoords(event);
        if (x === null || y === null) return;

        const {gridX, gridY} = toGridCoords(x, y);
        if (gridX === null || gridY === null) {
            setStatusMessage("Курсор за пределами поля — робот не выйдет за край.");
            return;
        }

        const clampedX = Math.min(Math.max(gridX, 0), width - 1);
        const clampedY = Math.min(Math.max(gridY, 0), height - 1);
        setRobotPos({x: clampedX, y: clampedY});
    };

    const handleMouseUp = (event) => {
        if (!isDraggingRobot) return;

        const {x, y} = getCanvasCoords(event);
        if (x === null || y === null) return;

        const {gridX, gridY} = toGridCoords(x, y);
        if (gridX === null || gridY === null) {
            setStatusMessage("Курсор за пределами поля.");
            return;
        }

        setIsDraggingRobot(false);
        setStatusMessage("Робот отпущен! Он остался в последней выбранной клетке.");
    };

    // ---------------------------------------------------------
    // ЛЕВЫЙ КЛИК (handleCanvasClick)
    // ---------------------------------------------------------
    const handleCanvasClick = (event) => {
        if (!editMode) {
            setStatusMessage(getHint("canvasLeftClickNoEdit", editMode));
            return;
        }

        const {x, y} = getCanvasCoords(event);
        if (x === null || y === null) return;

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

        // Проверяем, не клик ли на границе (стена)
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
                    setStatusMessage(getHint("canvasLeftClickEditMode", editMode) + " Стена удалена.");
                } else {
                    newWalls.add(wall);
                    setStatusMessage(getHint("canvasLeftClickEditMode", editMode) + " Вы поставили стену!");
                }
                return newWalls;
            });
        } else {
            // Иначе красим/очищаем клетку
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
    // ПРАВЫЙ КЛИК (handleCanvasRightClick): ставим/убираем маркер
    // ---------------------------------------------------------
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
    // КНОПКИ ДВИЖЕНИЯ РОБОТА
    // ---------------------------------------------------------
    const moveRobot = (direction) => {
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
            newPos.x = Math.min(Math.max(newPos.x, 0), width - 1);
            newPos.y = Math.min(Math.max(newPos.y, 0), height - 1);
            return newPos;
        });

        if (actionKey) {
            setStatusMessage(getHint(actionKey, editMode));
        }
    };

    // ---------------------------------------------------------
    // ПРОКРУТКА КОЛЁСИКОМ (Zoom)
    // ---------------------------------------------------------
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

    // Кнопка "Стоп"
    const handleStop = useCallback(() => {
        setIsRunning(false);
        setStatusMessage('Выполнение прервано');
    }, []);

    // Блокируем прокрутку всей страницы при прокрутке на холсте
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
    // КНОПКИ МАРКЕРОВ/ПОКРАСКИ ПОД РОБОТОМ
    // ---------------------------------------------------------
    const putMarker = () => {
        const pos = `${robotPos.x},${robotPos.y}`;
        setMarkers(prev => {
            const newMarkers = {...prev};
            if (!newMarkers[pos]) {
                newMarkers[pos] = 1;
                setStatusMessage("Маркер добавлен!");
            } else {
                setStatusMessage("Тут уже лежит маркер.");
                return prev;
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
                setStatusMessage("Маркер убран.");
            } else {
                setStatusMessage("Здесь нет маркера, чтобы поднять.");
                return prev;
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
                setStatusMessage("Клетка раскрашена!");
            } else {
                setStatusMessage("Клетка уже раскрашена, используйте 'Очистить клетку' чтобы убрать краску.");
                return prev;
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
                setStatusMessage("Клетка очищена от краски.");
            } else {
                setStatusMessage("Эта клетка и так не раскрашена.");
                return prev;
            }
            return newCells;
        });
    };

    // ---------------------------------------------------------
    // КНОПКИ ИЗМЕНЕНИЯ РАЗМЕРОВ ПОЛЯ
    // ---------------------------------------------------------
    const increaseWidth = () => {
        if (editMode) {
            setWidth(prev => prev + 1);
            setStatusMessage(getHint("increaseWidth", editMode));
        } else {
            setStatusMessage("Изменять ширину можно только в режиме рисования!");
        }
    };

    const decreaseWidth = () => {
        if (editMode && width > 1) {
            setWidth(prev => prev - 1);
            setStatusMessage(getHint("decreaseWidth", editMode));
        } else {
            setStatusMessage("Изменять ширину можно только в режиме рисования!");
        }
    };

    const increaseHeight = () => {
        if (editMode) {
            setHeight(prev => prev + 1);
            setStatusMessage(getHint("increaseHeight", editMode));
        } else {
            setStatusMessage("Изменять высоту можно только в режиме рисования!");
        }
    };

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
    // МОДАЛЬНОЕ ОКНО "ПОМОЩЬ"
    // ---------------------------------------------------------
    const openHelp = () => setHelpOpen(true);
    const closeHelp = () => setHelpOpen(false);

    // ---------------------------------------------------------
    // JSX (верстка)
    // ---------------------------------------------------------
    return (<div className="container">

        {/* Блок редактора кода (слева) */}
        <Card className="card code-editor">
            <CardContent style={{flex: '1 1 auto', display: 'flex', flexDirection: 'column'}}>
                <Typography variant="h5" gutterBottom style={{color: '#fff'}}>
                    Редактор Кода
                </Typography>
                <Editor
                    value={code}
                    onValueChange={code => setCode(code)}
                    highlight={highlightCode}
                    padding={10}
                    className="react-simple-code-editor"
                    style={{
                        fontFamily: '"Fira Code", monospace', fontSize: 14, flex: '1 1 auto', overflow: 'auto',
                    }}
                />
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
                    <Button
                        variant="outlined"
                        color="primary"
                        onClick={handleReset}
                        fullWidth
                    >
                        Сбросить симулятор
                    </Button>
                </div>
                {statusMessage && (<Typography variant="body1" color="primary" style={{marginTop: '16px'}}>
                    {statusMessage}
                </Typography>)}
            </CardContent>
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

                    {/* Маркеры и покраска */}
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

                    {/* Импорт обстановки */}
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

        {/* Поле (Canvas) и статус */}
        <div className="field-area">
            <Card className="card-controls">
                <div className="field-container">
                    <div className="canvas-wrapper">
                        <canvas
                            ref={canvasRef}
                            width={(width + 2) * cellSize}
                            height={(height + 2) * cellSize}
                            className={editMode ? 'edit-mode' : ''}

                            onMouseDown={(e) => {
                                if (e.button !== 0) return;
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
    </div>);
};

export default RobotSimulator;
