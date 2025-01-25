// RobotSimulator.jsx

import React, { useState, useRef, useCallback, useEffect } from 'react';
import CodeEditor from './components/CodeEditor';
import ControlPanel from './components/ControlPanel';
import Field from './components/Field';

/**
 * Главный компонент приложения.
 * Хранит глобальное состояние робота, стены, поле, а также
 * осуществляет связь с сервером (execute/reset).
 */
function RobotSimulator() {
  // Код в редакторе
  const [code, setCode] = useState(`использовать Робот

алг
нач
  вправо
  вниз
  влево
  вверх
  закрасить
кон`);

  // Сообщения о состоянии/ошибках
  const [statusMessage, setStatusMessage] = useState('Готов к работе!');

  // Флаг выполнения кода
  const [isRunning, setIsRunning] = useState(false);

  // Размеры поля (в клетках)
  const [width, setWidth] = useState(7);
  const [height, setHeight] = useState(7);

  // Размер клетки (пиксели)
  const [cellSize, setCellSize] = useState(50);

  // Позиция робота (x,y)
  const [robotPos, setRobotPos] = useState({ x: 0, y: 0 });

  // Множество обычных стен (string: "x1,y1,x2,y2")
  const [walls, setWalls] = useState(new Set());

  // Множество постоянных (граничных) стен
  const [permanentWalls, setPermanentWalls] = useState(new Set());

  // Маркеры (object: { "x,y": 1 })
  const [markers, setMarkers] = useState({});

  // Множество раскрашенных клеток
  const [coloredCells, setColoredCells] = useState(new Set());

  // Режим рисования (true/false)
  const [editMode, setEditMode] = useState(false);

  // Ссылка на canvas
  const canvasRef = useRef(null);

  /**
   * setupPermanentWalls(): Создаём границы поля (верх, низ, лево, право).
   */
  const setupPermanentWalls = useCallback(() => {
    const newSet = new Set();
    // Горизонтальные
    for (let x = 0; x < width; x++) {
      newSet.add(`${x},0,${x + 1},0`);         // верх
      newSet.add(`${x},${height},${x + 1},${height}`); // низ
    }
    // Вертикальные
    for (let y = 0; y < height; y++) {
      newSet.add(`0,${y},0,${y + 1}`);         // лево
      newSet.add(`${width},${y},${width},${y + 1}`);   // право
    }
    setPermanentWalls(newSet);
  }, [width, height]);

  /**
   * clampRobotPos(): Клэмпим позицию робота, если он «вышел» за поле.
   */
  const clampRobotPos = useCallback(() => {
    setRobotPos(prev => {
      const clampedX = Math.min(Math.max(prev.x, 0), width - 1);
      const clampedY = Math.min(Math.max(prev.y, 0), height - 1);
      return { x: clampedX, y: clampedY };
    });
  }, [width, height]);

  // Вызываем setupPermanentWalls() и clampRobotPos при изменении width/height
  useEffect(() => {
    setupPermanentWalls();
    clampRobotPos();
  }, [width, height, setupPermanentWalls, clampRobotPos]);

  /**
   * Очистка кода
   */
  const handleClearCode = useCallback(() => {
    setCode('');
    setStatusMessage('Код очищен.');
  }, []);

  /**
   * Остановка выполнения
   */
  const handleStop = useCallback(() => {
    setIsRunning(false);
    setStatusMessage('Выполнение прервано.');
  }, []);

  /**
   * Запуск кода (POST /execute)
   */
  const handleStart = useCallback(async () => {
    if (!code.trim()) {
      setStatusMessage('Ошибка: программа пустая');
      return;
    }
    setIsRunning(true);
    try {
      const resp = await fetch('http://localhost:5000/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      });
      if (!resp.ok) {
        setStatusMessage(`HTTP-ошибка: ${resp.status}`);
        setIsRunning(false);
        return;
      }
      const data = await resp.json();
      if (data.success) {
        setRobotPos(data.robotPos);
        setWalls(new Set(data.walls));
        setColoredCells(new Set(data.coloredCells));
        setMarkers(data.markers);
        setStatusMessage(data.message || 'Код выполнен успешно!');
      } else {
        setStatusMessage(`Ошибка: ${data.message}`);
      }
    } catch (error) {
      setStatusMessage('Ошибка соединения с сервером.');
    } finally {
      setIsRunning(false);
    }
  }, [code]);

  /**
   * Сброс симулятора (POST /reset)
   */
  const handleReset = useCallback(async () => {
    try {
      const resp = await fetch('http://localhost:5000/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const result = await resp.json();
      if (resp.ok && result.success) {
        // Сбрасываем локально
        setRobotPos({ x: 0, y: 0 });
        setWalls(new Set());
        setColoredCells(new Set());
        setMarkers({});
        setWidth(7);
        setHeight(7);
        setCode(`использовать Робот

алг
нач
  # Ваши команды здесь
кон`);
        setIsRunning(false);
        setStatusMessage(result.message);
      } else {
        setStatusMessage(`Ошибка: ${result.message}`);
      }
    } catch (error) {
      setStatusMessage('Ошибка соединения с сервером.');
    }
  }, []);

  return (
    <div className="container">
      <CodeEditor
        code={code}
        setCode={setCode}
        statusMessage={statusMessage}
        setStatusMessage={setStatusMessage}
        isRunning={isRunning}
        onClearCode={handleClearCode}
        onStop={handleStop}
        onStart={handleStart}
        onReset={handleReset}
      />

      <ControlPanel
        robotPos={robotPos}
        setRobotPos={setRobotPos}
        walls={walls}
        setWalls={setWalls}
        permanentWalls={permanentWalls}
        markers={markers}
        setMarkers={setMarkers}
        coloredCells={coloredCells}
        setColoredCells={setColoredCells}
        width={width}
        setWidth={setWidth}
        height={height}
        setHeight={setHeight}
        cellSize={cellSize}
        setCellSize={setCellSize}
        editMode={editMode}
        setEditMode={setEditMode}
        setStatusMessage={setStatusMessage}
      />

      <Field
        canvasRef={canvasRef}
        robotPos={robotPos}
        walls={walls}
        permanentWalls={permanentWalls}
        coloredCells={coloredCells}
        markers={markers}
        width={width}
        height={height}
        cellSize={cellSize}
        editMode={editMode}
        setRobotPos={setRobotPos}
        setWalls={setWalls}
        setMarkers={setMarkers}
        setColoredCells={setColoredCells}
        setStatusMessage={setStatusMessage}
        setCellSize={setCellSize}
      />
    </div>
  );
}

export default RobotSimulator;
