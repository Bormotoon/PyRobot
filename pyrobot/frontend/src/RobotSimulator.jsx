/**
 * RobotSimulator.jsx
 *
 * В этом файле главный компонент приложения, который теперь использует useReducer
 * для хранения и управления состоянием (код, выполнение, размеры поля, стены, маркеры и т.д.).
 * Все изменения состояния осуществляются через dispatch, что обеспечивает более явную логику.
 *
 * Структура:
 * - initialState: объект со всеми начальными значениями
 * - reducer: функция, обрабатывающая различные действия (action.type), обновляя state
 * - RobotSimulator: компонент, который создаёт useReducer(reducer, initialState),
 *   а также определяет хендлеры (handleClearCode, handleStart и т.д.), которые диспатчат действия
 *   и передаёт нужные части state и колбэки в дочерние компоненты (CodeEditor, ControlPanel, Field).
 */

import React, {useCallback, useEffect, useReducer, useRef} from 'react';
import CodeEditor from './components/CodeEditor';
import ControlPanel from './components/ControlPanel';
import Field from './components/Field';

/**
 * Начальное состояние для useReducer,
 * содержит все ключи, которые мы храним в RobotSimulator:
 * - code: текст программы КУМИР
 * - isRunning: флаг выполнения
 * - statusMessage: строка для подсказок/сообщений
 * - width, height, cellSize: параметры поля
 * - robotPos: позиция робота (x,y)
 * - walls: множество обычных стен
 * - permanentWalls: множество постоянных (граничных) стен
 * - markers: объект с координатами маркеров
 * - coloredCells: множество закрашенных клеток
 * - editMode: режим рисования (true/false)
 */
const initialState = {
    code: `использовать Робот

алг
нач
  вправо
  вниз
  влево
  вверх
  закрасить
кон`,
    isRunning: false,
    statusMessage: '',
    width: 7,
    height: 7,
    cellSize: 50,
    robotPos: {x: 0, y: 0},
    walls: new Set(),
    permanentWalls: new Set(),
    markers: {},
    coloredCells: new Set(),
    editMode: false
};

/**
 * Функция reducer(state, action)
 * Принимает текущее состояние (state) и объект действия (action),
 * возвращает новое состояние на основе типа действия (action.type)
 * и дополнительных данных (action.payload).
 */
function reducer(state, action) {
    switch (action.type) {
        case 'SET_CODE':
            return {...state, code: action.payload};

        case 'SET_IS_RUNNING':
            return {...state, isRunning: action.payload};

        case 'SET_STATUS_MESSAGE':
            return {...state, statusMessage: action.payload};

        case 'SET_WIDTH':
            return {...state, width: action.payload};

        case 'SET_HEIGHT':
            return {...state, height: action.payload};

        case 'SET_CELL_SIZE':
            return {...state, cellSize: action.payload};

        case 'SET_ROBOT_POS':
            return {
                ...state,
                robotPos: typeof action.payload === 'function'
                    ? action.payload(state.robotPos)
                    : action.payload
            };

        case 'SET_WALLS':
            return {
                ...state,
                walls: typeof action.payload === 'function'
                    ? action.payload(state.walls)
                    : new Set(action.payload)
            };

        case 'SET_PERMANENT_WALLS':
            return {
                ...state,
                permanentWalls: typeof action.payload === 'function'
                    ? action.payload(state.permanentWalls)
                    : new Set(action.payload)
            };

        case 'SET_MARKERS':
            return {
                ...state,
                markers: typeof action.payload === 'function'
                    ? action.payload(state.markers)
                    : action.payload
            };

        case 'SET_COLORED_CELLS':
            return {
                ...state,
                coloredCells: typeof action.payload === 'function'
                    ? action.payload(state.coloredCells)
                    : new Set(action.payload)
            };

        case 'SET_EDIT_MODE':
            return {...state, editMode: action.payload};

        default:
            return state; // Если тип действия не распознан, возвращаем state без изменений
    }
}

/**
 * Функция setupPermanentWalls(width, height)
 * Генерирует множество строк (\"x1,y1,x2,y2\") для границ поля.
 */
function setupPermanentWalls(width, height) {
    const newWalls = new Set();
    // Горизонтальные границы
    for (let x = 0; x < width; x++) {
        newWalls.add(`${x},0,${x + 1},0`);           // Верх
        newWalls.add(`${x},${height},${x + 1},${height}`); // Низ
    }
    // Вертикальные границы
    for (let y = 0; y < height; y++) {
        newWalls.add(`0,${y},0,${y + 1}`);             // Лево
        newWalls.add(`${width},${y},${width},${y + 1}`);   // Право
    }
    return newWalls;
}

/**
 * Функция clampRobotPos(robotPos, width, height)
 * Ограничивает координаты робота внутри (0..width-1, 0..height-1).
 */
function clampRobotPos(robotPos, width, height) {
    const clampedX = Math.min(Math.max(robotPos.x, 0), width - 1);
    const clampedY = Math.min(Math.max(robotPos.y, 0), height - 1);
    return {x: clampedX, y: clampedY};
}

/**
 * Главный компонент RobotSimulator, с использованием useReducer.
 */
function RobotSimulator() {
    /**
     * Хук useReducer:
     *   - reducer: функция, обрабатывающая действия
     *   - initialState: объект начального состояния
     */
    const [state, dispatch] = useReducer(reducer, initialState);

    /**
     * Ссылка на canvas
     * (передаётся в Field, чтобы тот мог рисовать).
     */
    const canvasRef = useRef(null);

    /**
     * handleClearCode()
     * Очищает поле code и выводит сообщение.
     */
    const handleClearCode = useCallback(() => {
        dispatch({type: 'SET_CODE', payload: ''});
        dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Код программы очищен.'});
    }, []);

    /**
     * handleStop()
     * Ставит isRunning = false, выводит сообщение.
     */
    const handleStop = useCallback(() => {
        dispatch({type: 'SET_IS_RUNNING', payload: false});
        dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Выполнение остановлено.'});
    }, []);

    /**
     * handleStart()
     * Проверяем, не пуст ли код, включаем isRunning = true,
     * через таймаут выключаем и выводим демо-сообщение.
     */
    const handleStart = useCallback(() => {
        if (!state.code.trim()) {
            dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Ошибка: программа пустая.'});
            return;
        }
        dispatch({type: 'SET_IS_RUNNING', payload: true});

        setTimeout(() => {
            dispatch({type: 'SET_IS_RUNNING', payload: false});
            dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Код (демо) выполнен успешно!'});
        }, 800);
    }, [state.code]);

    /**
     * handleReset()
     * Сбрасывает всё состояние к начальному.
     */
    const handleReset = useCallback(() => {
        dispatch({type: 'SET_ROBOT_POS', payload: {x: 0, y: 0}});
        dispatch({type: 'SET_WALLS', payload: new Set()});
        dispatch({type: 'SET_COLORED_CELLS', payload: new Set()});
        dispatch({type: 'SET_MARKERS', payload: {}});
        dispatch({type: 'SET_WIDTH', payload: 7});
        dispatch({type: 'SET_HEIGHT', payload: 7});
        dispatch({
            type: 'SET_CODE', payload: `использовать Робот

алг
нач
  # Ваши команды здесь
кон`
        });
        dispatch({type: 'SET_IS_RUNNING', payload: false});
        dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Симулятор сброшен (демо).'});
    }, []);

    /**
     * useEffect, который следит за изменением width/height,
     * генерирует границы (permanentWalls)
     * и клэмпит позицию робота.
     */
    useEffect(() => {
        // Генерируем новые постоянные стены
        const newWalls = setupPermanentWalls(state.width, state.height);
        dispatch({type: 'SET_PERMANENT_WALLS', payload: newWalls});

        // Клэмпим робота
        const newPos = clampRobotPos(state.robotPos, state.width, state.height);
        dispatch({type: 'SET_ROBOT_POS', payload: newPos});
    }, [state.width, state.height]);

    return (<div className="container">
        {/**
         * Компонент CodeEditor:
         * передаём текущее state.code и isRunning,
         * а также колбэки handleClearCode, handleStop, handleStart, handleReset
         */}
        <CodeEditor
            code={state.code}
            setCode={(newCode) => dispatch({type: 'SET_CODE', payload: newCode})}
            isRunning={state.isRunning}
            onClearCode={handleClearCode}
            onStop={handleStop}
            onStart={handleStart}
            onReset={handleReset}
        />

        {/**
         * Компонент ControlPanel:
         * передаём нужные части state (robotPos, walls, markers и т.д.)
         * и dispatch или соответствующие setter-колбэки,
         * а также setStatusMessage для подсказок.
         */}
        <ControlPanel
            robotPos={state.robotPos}
            setRobotPos={(pos) => dispatch({type: 'SET_ROBOT_POS', payload: pos})}

            walls={state.walls}
            setWalls={(newWalls) => dispatch({type: 'SET_WALLS', payload: newWalls})}

            permanentWalls={state.permanentWalls}

            markers={state.markers}
            setMarkers={(m) => dispatch({type: 'SET_MARKERS', payload: m})}

            coloredCells={state.coloredCells}
            setColoredCells={(c) => dispatch({type: 'SET_COLORED_CELLS', payload: c})}

            width={state.width}
            setWidth={(val) => dispatch({type: 'SET_WIDTH', payload: val})}

            height={state.height}
            setHeight={(val) => dispatch({type: 'SET_HEIGHT', payload: val})}

            cellSize={state.cellSize}
            setCellSize={(val) => dispatch({type: 'SET_CELL_SIZE', payload: val})}

            editMode={state.editMode}
            setEditMode={(val) => dispatch({type: 'SET_EDIT_MODE', payload: val})}

            setStatusMessage={(msg) => dispatch({type: 'SET_STATUS_MESSAGE', payload: msg})}
        />

        {/**
         * Компонент Field:
         * передаём Canvas ref, а также все части state и setter для них,
         * в т.ч. statusMessage и setStatusMessage,
         * чтобы Field мог рисовать Canvas и обновлять сообщения.
         */}
        <Field
            canvasRef={canvasRef}

            robotPos={state.robotPos}
            walls={state.walls}
            permanentWalls={state.permanentWalls}
            coloredCells={state.coloredCells}
            markers={state.markers}

            width={state.width}
            height={state.height}
            cellSize={state.cellSize}
            editMode={state.editMode}

            setRobotPos={(pos) => dispatch({type: 'SET_ROBOT_POS', payload: pos})}
            setWalls={(newWalls) => dispatch({type: 'SET_WALLS', payload: newWalls})}
            setMarkers={(m) => dispatch({type: 'SET_MARKERS', payload: m})}
            setColoredCells={(c) => dispatch({type: 'SET_COLORED_CELLS', payload: c})}
            statusMessage={state.statusMessage}
            setStatusMessage={(msg) => dispatch({type: 'SET_STATUS_MESSAGE', payload: msg})}
        />
    </div>);
}

export default RobotSimulator;
