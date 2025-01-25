/**
 * Field.jsx
 *
 * В этом варианте, когда включён editMode, при перетаскивании робота
 * игнорируется наличие обычных или постоянных стен, и он может двигаться
 * свободно по всем клеткам поля. При этом перемещение по кнопкам
 * (ControlPanel) по-прежнему учитывает стены.
 */

import React, { useEffect, useCallback, useState } from 'react';
import { Card, Typography } from '@mui/material';
import { drawField } from '../canvasDrawing';

/**
 * Компонент поля (Canvas).
 * Реализует:
 * - Перемещение робота путём перетаскивания (в режиме рисования — без учёта стен).
 * - Рисование стен и раскраску клеток (левый клик).
 * - Маркеры (правый клик).
 * - Зумирование (колёсико мыши).
 */
function Field({
  canvasRef,
  robotPos,
  walls,
  permanentWalls,
  coloredCells,
  markers,
  width,
  height,
  cellSize,
  editMode,
  setRobotPos,
  setWalls,
  setMarkers,
  setColoredCells,
  setStatusMessage,
  setCellSize
}) {
  // Флаг, перетаскиваем ли робота
  const [isDraggingRobot, setIsDraggingRobot] = useState(false);

  /**
   * Рисуем поле при изменении зависимостей
   */
  useEffect(() => {
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
      cellSize
    });
  }, [
    canvasRef,
    robotPos,
    walls,
    permanentWalls,
    coloredCells,
    markers,
    width,
    height,
    cellSize
  ]);

  /**
   * Функция getCanvasCoords(event):
   * Возвращает координаты мыши внутри Canvas.
   */
  const getCanvasCoords = useCallback((event) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: null, y: null };
    const rect = canvas.getBoundingClientRect();
    return {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top
    };
  }, [canvasRef]);

  /**
   * Функция toGridCoords(px, py):
   * Перевод пиксельных координат Canvas в координаты сетки (целочисленные x,y).
   */
  const toGridCoords = useCallback((px, py) => {
    const gx = Math.floor(px / cellSize) - 1;
    const gy = Math.floor(py / cellSize) - 1;
    if (gx < 0 || gx >= width || gy < 0 || gy >= height) {
      return { gridX: null, gridY: null };
    }
    return { gridX: gx, gridY: gy };
  }, [cellSize, width, height]);

  /**
   * handleCanvasLeftClickEditMode(px, py):
   * Ставим/убираем стены или красим клетку в режиме рисования (если не на роботе).
   */
  const handleCanvasLeftClickEditMode = useCallback((px, py) => {
    const margin = 5;
    const gridX = Math.floor(px / cellSize) - 1;
    const gridY = Math.floor(py / cellSize) - 1;
    if (gridX < 0 || gridX >= width || gridY < 0 || gridY >= height) {
      setStatusMessage('Клик за пределами поля рисования.');
      return;
    }
    const xRem = px % cellSize;
    const yRem = py % cellSize;
    let wall = null;

    // Проверяем, попали ли в границу клетки
    if (xRem < margin) {
      wall = `${gridX},${gridY},${gridX},${gridY + 1}`;
    } else if (xRem > cellSize - margin) {
      wall = `${gridX + 1},${gridY},${gridX + 1},${gridY + 1}`;
    } else if (yRem < margin) {
      wall = `${gridX},${gridY},${gridX + 1},${gridY}`;
    } else if (yRem > cellSize - margin) {
      wall = `${gridX},${gridY + 1},${gridX + 1},${gridY + 1}`;
    }

    if (wall) {
      // Ставим/убираем стену (если не постоянная)
      if (!permanentWalls.has(wall)) {
        setWalls(prev => {
          const copy = new Set(prev);
          if (copy.has(wall)) {
            copy.delete(wall);
            setStatusMessage('Стена удалена.');
          } else {
            copy.add(wall);
            setStatusMessage('Стена поставлена.');
          }
          return copy;
        });
      } else {
        setStatusMessage('Это граничная стена, нельзя убрать.');
      }
    } else {
      // Красим или очищаем клетку
      const posKey = `${gridX},${gridY}`;
      setColoredCells(prev => {
        const c = new Set(prev);
        if (c.has(posKey)) {
          c.delete(posKey);
          setStatusMessage('Клетка очищена!');
        } else {
          c.add(posKey);
          setStatusMessage('Клетка раскрашена!');
        }
        return c;
      });
    }
  }, [
    cellSize,
    width,
    height,
    permanentWalls,
    setWalls,
    setColoredCells,
    setStatusMessage
  ]);

  /**
   * handleMouseDown(e):
   * Если editMode включён, клик по роботу => начинаем перетаскивать без учёта стен.
   * Иначе — ставим/убираем стены или красим клетку.
   */
  const handleMouseDown = useCallback((e) => {
    if (e.button !== 0) return; // только левая
    const { x, y } = getCanvasCoords(e);
    if (x === null || y === null) return;

    const { gridX, gridY } = toGridCoords(x, y);
    if (gridX === null || gridY === null) {
      setStatusMessage('Клик за пределами поля.');
      return;
    }
    if (!editMode) {
      setStatusMessage('Режим рисования не включён.');
      return;
    }

    // Если клик по роботу — перетаскиваем (без учёта стен)
    if (gridX === robotPos.x && gridY === robotPos.y) {
      setIsDraggingRobot(true);
      setStatusMessage('Начато перетаскивание робота (стены не учитываются).');
    } else {
      // Иначе рисуем стены / красим клетку
      handleCanvasLeftClickEditMode(x, y);
    }
  }, [
    editMode,
    robotPos,
    getCanvasCoords,
    toGridCoords,
    handleCanvasLeftClickEditMode,
    setStatusMessage
  ]);

  /**
   * handleMouseMove(e):
   * Если перетаскиваем робота, разрешаем перемещение по клеткам без учёта стен.
   */
  const handleMouseMove = useCallback((e) => {
    if (!isDraggingRobot) return;
    // Получаем курсор
    const { x, y } = getCanvasCoords(e);
    if (x === null || y === null) return;
    // Определяем клетку
    const { gridX, gridY } = toGridCoords(x, y);
    if (gridX === null || gridY === null) {
      setStatusMessage('Курсор вне поля, робот не перемещён.');
      return;
    }
    // Просто клэмпим внутри поля (без проверки стен)
    const newX = Math.min(Math.max(gridX, 0), width - 1);
    const newY = Math.min(Math.max(gridY, 0), height - 1);
    setRobotPos({ x: newX, y: newY });
  }, [
    isDraggingRobot,
    getCanvasCoords,
    toGridCoords,
    setStatusMessage,
    setRobotPos,
    width,
    height
  ]);

  /**
   * handleMouseUp(): завершаем перетаскивание
   */
  const handleMouseUp = useCallback(() => {
    if (isDraggingRobot) {
      setIsDraggingRobot(false);
      setStatusMessage('Перетаскивание робота завершено.');
    }
  }, [isDraggingRobot, setStatusMessage]);

  /**
   * Правый клик — ставим/убираем маркер (только если editMode включён).
   */
  const handleCanvasRightClick = useCallback((e) => {
    e.preventDefault();
    if (!editMode) {
      setStatusMessage('Правый клик — режим рисования не включён.');
      return;
    }
    const { x, y } = getCanvasCoords(e);
    if (x === null || y === null) return;
    const { gridX, gridY } = toGridCoords(x, y);
    if (gridX === null || gridY === null) {
      setStatusMessage('Правый клик за пределами поля.');
      return;
    }
    const posKey = `${gridX},${gridY}`;
    setMarkers(prev => {
      const copy = { ...prev };
      if (!copy[posKey]) {
        copy[posKey] = 1;
        setStatusMessage('Маркер добавлен!');
      } else {
        delete copy[posKey];
        setStatusMessage('Маркер убран.');
      }
      return copy;
    });
  }, [
    editMode,
    getCanvasCoords,
    toGridCoords,
    setMarkers,
    setStatusMessage
  ]);

  /**
   * Колёсико — меняем масштаб cellSize
   */
  const handleCanvasWheel = useCallback((e) => {
    e.preventDefault();
    setCellSize(prev => {
      const newSize = Math.max(10, prev + (e.deltaY > 0 ? -5 : 5));
      return newSize;
    });
  }, [setCellSize]);

  return (
    <div className="field-area">
      <Card className="card-controls">
        <div className="field-container">
          <div className="canvas-wrapper">
            <canvas
              ref={canvasRef}
              width={(width + 2) * cellSize}
              height={(height + 2) * cellSize}
              className={editMode ? 'edit-mode' : ''}
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onContextMenu={handleCanvasRightClick}
              onWheel={handleCanvasWheel}
            />
          </div>
        </div>
      </Card>

      <Card className="status-card">
        <Typography variant="body2">
          Позиция робота: ({robotPos.x}, {robotPos.y})
        </Typography>
        <Typography variant="body2" style={{ marginTop: 8 }}>
          Маркеров на поле: {Object.keys(markers).length} <br />
          Раскрашенных клеток: {coloredCells.size}
        </Typography>
      </Card>
    </div>
  );
}

export default Field;
