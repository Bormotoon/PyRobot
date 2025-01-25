// /frontend/src/RobotSimulator.jsx

import React, { useState, useRef, useCallback, useEffect } from 'react';
import CodeEditor from './components/CodeEditor';
import ControlPanel from './components/ControlPanel';
import Field from './components/Field';

/**
 * Главный компонент приложения.
 * Хранит глобальное состояние (включая statusMessage),
 * передаёт нужные пропсы в CodeEditor, ControlPanel, Field.
 */
function RobotSimulator() {
  // Код редактора
  const [code, setCode] = useState(`использовать Робот

алг
нач
  вправо
  вниз
  влево
  вверх
  закрасить
кон`);

  // Выполняется ли код
  const [isRunning, setIsRunning] = useState(false);

  // Главное поле для подсказок
  const [statusMessage, setStatusMessage] = useState('');

  // Параметры поля
  const [width, setWidth] = useState(7);
  const [height, setHeight] = useState(7);
  const [cellSize, setCellSize] = useState(50);

  // Позиция робота
  const [robotPos, setRobotPos] = useState({ x: 0, y: 0 });

  // Стены (обычные)
  const [walls, setWalls] = useState(new Set());
  // Постоянные стены (границы) — здесь будут внешние стены
  const [permanentWalls, setPermanentWalls] = useState(new Set());

  // Маркеры и раскрашенные клетки
  const [markers, setMarkers] = useState({});
  const [coloredCells, setColoredCells] = useState(new Set());

  // Режим рисования
  const [editMode, setEditMode] = useState(false);

  // Ссылка на canvas (используется в Field)
  const canvasRef = useRef(null);

  /**
   * Функции управления кодом (onClear, onStart, onStop, onReset)
   */
  const handleClearCode = useCallback(() => {
    setCode('');
    setStatusMessage('Код программы очищен.');
  }, []);

  const handleStop = useCallback(() => {
    setIsRunning(false);
    setStatusMessage('Выполнение остановлено.');
  }, []);

  const handleStart = useCallback(() => {
    if (!code.trim()) {
      setStatusMessage('Ошибка: программа пустая.');
      return;
    }
    setIsRunning(true);
    // Пример без реального сервера
    setTimeout(() => {
      setIsRunning(false);
      setStatusMessage('Код (демо) выполнен успешно!');
    }, 800);
  }, [code]);

  const handleReset = useCallback(() => {
    // Сброс состояния
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
    setStatusMessage('Симулятор сброшен (демо).');
  }, []);

  /**
   * setupPermanentWalls:
   * При каждом изменении width/height создаём заново внешние стены (границы).
   */
  const setupPermanentWalls = useCallback(() => {
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
    setPermanentWalls(newWalls);
  }, [width, height]);

  /**
   * clampRobotPos:
   * Удерживает робота внутри поля (0..width-1, 0..height-1)
   * при изменении размеров поля.
   */
  const clampRobotPos = useCallback(() => {
    setRobotPos(prev => {
      const clampedX = Math.min(Math.max(prev.x, 0), width - 1);
      const clampedY = Math.min(Math.max(prev.y, 0), height - 1);
      return { x: clampedX, y: clampedY };
    });
  }, [width, height]);

  /**
   * useEffect: при любом изменении width/height ->
   *  - пересоздать внешние стены (setupPermanentWalls)
   *  - clampRobotPos, чтобы робот не остался за границей.
   */
  useEffect(() => {
    setupPermanentWalls();
    clampRobotPos();
  }, [width, height, setupPermanentWalls, clampRobotPos]);

  return (
    <div className="container">
      <CodeEditor
        code={code}
        setCode={setCode}
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
        statusMessage={statusMessage}
        setStatusMessage={setStatusMessage}
      />
    </div>
  );
}

export default RobotSimulator;
