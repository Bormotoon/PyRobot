/**
 * Field.jsx
 *
 * Данный файл содержит компонент Field, который:
 * - Отображает Canvas (поле) и обрабатывает взаимодействие мыши (рисование стен, раскраска, маркеры, перетаскивание робота в режиме рисования).
 * - Выводит статус (позицию робота, количество маркеров/закрашенных) и строку подсказок (statusMessage) в отдельном блоке.
 * - Использует пропсы, переданные из RobotSimulator, где состояние хранится в useReducer.
 * - При необходимости вызывает setRobotPos, setWalls, setColoredCells и т. д., которые под капотом диспатчат действия в Reducer.
 */

import React, { useEffect, useCallback, useState } from 'react';
import { Card, Typography } from '@mui/material';
import { drawField } from '../canvasDrawing';
import { getHint } from '../hints';

/**
 * Компонент Field.
 * @param {Object} props - объект пропсов.
 * @param {React.MutableRefObject} props.canvasRef - ссылка на canvas DOM-элемент.
 * @param {{x:number,y:number}} props.robotPos - позиция робота.
 * @param {Set<string>} props.walls - множество обычных стен.
 * @param {Set<string>} props.permanentWalls - множество постоянных (внешних) стен.
 * @param {Set<string>} props.coloredCells - множество закрашенных клеток \"x,y\".
 * @param {Object} props.markers - объект маркеров { \"x,y\": 1 }.
 * @param {number} props.width - ширина поля (количество клеток).
 * @param {number} props.height - высота поля (количество клеток).
 * @param {number} props.cellSize - размер клетки (в пикселях).
 * @param {boolean} props.editMode - режим рисования.
 * @param {function} props.setRobotPos - функция-колбэк для изменения позиции робота.
 * @param {function} props.setWalls - функция-колбэк для изменения множества walls.
 * @param {function} props.setMarkers - функция-колбэк для изменения объекта markers.
 * @param {function} props.setColoredCells - функция-колбэк для изменения множества закрашенных клеток.
 * @param {string} props.statusMessage - текущая строка подсказок/сообщений.
 * @param {function} props.setStatusMessage - функция-колбэк для изменения statusMessage.
 * @returns {JSX.Element} Разметка, содержащая Canvas и блок статуса/подсказки.
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
  statusMessage,
  setStatusMessage
}) {
  /**
   * Локальное состояние: isDraggingRobot указывает, перетаскиваем ли мы робота в режиме рисования.
   */
  const [isDraggingRobot, setIsDraggingRobot] = useState(false);

  /**
   * useEffect, который при каждом рендере (или изменении зависимостей)
   * отрисовывает текущее состояние поля, робота, стен, маркеров на Canvas.
   */
  useEffect(() => {
    if (!canvasRef.current) return;
    drawField(canvasRef.current, {
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
    coloredCells,
    robotPos,
    markers,
    walls,
    permanentWalls,
    width,
    height,
    cellSize
  ]);

  /**
   * getCanvasCoords(event)
   * Возвращает координаты (x,y) внутри canvas, либо {x:null,y:null} если canvasRef пуст.
   * @param {MouseEvent} event - событие мыши
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
   * toGridCoords(px, py)
   * Перевод пиксельных координат (px, py) в координаты сетки (gridX, gridY).
   * Учитываем, что поле отсчитывается с отступом cellSize (т. е. \"+1\" в draw).
   * @param {number} px - координата X в пикселях внутри canvas
   * @param {number} py - координата Y в пикселях внутри canvas
   * @returns {{gridX:number|null, gridY:number|null}}
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
   * handleCanvasLeftClickEditMode(px, py)
   * Рисует/убирает стену, если клик на границе клетки, или красит/очищает клетку,
   * если клик внутри клетки (в режиме рисования).
   * Выводит подсказку getHint('canvasLeftClickEditMode', true).
   */
  const handleCanvasLeftClickEditMode = useCallback((px, py) => {
    const margin = 5;
    const gridX = Math.floor(px / cellSize) - 1;
    const gridY = Math.floor(py / cellSize) - 1;
    if (gridX == null || gridY == null ||
      gridX < 0 || gridX >= width || gridY < 0 || gridY >= height) {
      setStatusMessage('Клик за пределами поля рисования.');
      return;
    }

    const xRem = px % cellSize;
    const yRem = py % cellSize;
    let wall = null;

    // Проверка на границу (лево/право/верх/низ) с помощью margin
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
      // Если клик на границу => стена
      if (!permanentWalls.has(wall)) {
        setWalls(prev => {
          const copy = new Set(prev);
          if (copy.has(wall)) {
            copy.delete(wall);
            setStatusMessage('Стена удалена. ' + getHint('canvasLeftClickEditMode', true));
          } else {
            copy.add(wall);
            setStatusMessage('Стена поставлена. ' + getHint('canvasLeftClickEditMode', true));
          }
          return copy;
        });
      } else {
        setStatusMessage('Это постоянная стена. ' + getHint('canvasLeftClickEditMode', true));
      }
    } else {
      // Иначе считаем, что клик внутри клетки => красим/очищаем клетку
      const posKey = `${gridX},${gridY}`;
      setColoredCells(prev => {
        const c = new Set(prev);
        if (c.has(posKey)) {
          c.delete(posKey);
          setStatusMessage('Клетка очищена! ' + getHint('canvasLeftClickEditMode', true));
        } else {
          c.add(posKey);
          setStatusMessage('Клетка закрашена! ' + getHint('canvasLeftClickEditMode', true));
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
   * handleMouseDown(e)
   * Срабатывает при нажатии левой кнопки мыши на canvas.
   * Если не editMode => canvasLeftClickNoEdit,
   * иначе => либо начинаем перетаскивание робота, либо рисуем (handleCanvasLeftClickEditMode).
   */
  const handleMouseDown = useCallback((e) => {
    if (e.button !== 0) return; // только левая кнопка
    const { x, y } = getCanvasCoords(e);
    if (x === null || y === null) return;

    const { gridX, gridY } = toGridCoords(x, y);
    if (gridX === null || gridY === null) {
      setStatusMessage('Клик за пределами поля.');
      return;
    }

    if (!editMode) {
      setStatusMessage(getHint('canvasLeftClickNoEdit', false));
      return;
    }

    // Если editMode = true и клик по роботу => перетаскивание (без учёта стен)
    if (gridX === robotPos.x && gridY === robotPos.y) {
      setIsDraggingRobot(true);
      setStatusMessage('Перетаскивание робота (стены игнорируются).');
    } else {
      // Иначе рисуем стену/раскрашиваем клетку
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
   * handleMouseMove(e)
   * Если isDraggingRobot=true => двигаем робота, не обращая внимания на стены,
   * просто клэмпим в пределах поля (0..width-1, 0..height-1).
   */
  const handleMouseMove = useCallback((e) => {
    if (!isDraggingRobot) return;
    const { x, y } = getCanvasCoords(e);
    if (x === null || y === null) return;

    const { gridX, gridY } = toGridCoords(x, y);
    if (gridX === null || gridY === null) {
      setStatusMessage('Робот не выйдет за границы поля.');
      return;
    }
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
   * handleMouseUp()
   * Завершает перетаскивание робота, если оно было начато.
   */
  const handleMouseUp = useCallback(() => {
    if (isDraggingRobot) {
      setIsDraggingRobot(false);
      setStatusMessage('Перетаскивание робота завершено.');
    }
  }, [isDraggingRobot, setStatusMessage]);

  /**
   * handleCanvasRightClick(e)
   * При правом клике, если editMode=false => canvasRightClickNoEdit,
   * иначе ставим/убираем маркер (x,y).
   */
  const handleCanvasRightClick = useCallback((e) => {
    e.preventDefault();
    if (!editMode) {
      setStatusMessage(getHint('canvasRightClickNoEdit', false));
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
        setStatusMessage('Маркер добавлен! ' + getHint('canvasRightClickEditMode', true));
      } else {
        delete copy[posKey];
        setStatusMessage('Маркер убран. ' + getHint('canvasRightClickEditMode', true));
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
   * Формируем итоговую строку для статуса:
   * Позиция робота, количество маркеров, количество закрашенных клеток.
   */
  const displayString = `Позиция робота: (${robotPos.x}, ${robotPos.y})
Маркеров: ${Object.keys(markers).length}
Раскрашенных клеток: ${coloredCells.size}`;

  /**
   * Если есть statusMessage, добавляем двойной перевод строки перед ним,
   * чтобы подсказка отображалась отдельно ниже статуса.
   */
  const finalString = statusMessage
    ? `${displayString}\n\n${statusMessage}`
    : displayString;

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
            />
          </div>
        </div>
      </Card>

      <Card className="status-card">
        <Typography variant="body2" style={{ whiteSpace: 'pre-line' }}>
          {finalString}
        </Typography>
      </Card>
    </div>
  );
}

export default Field;
