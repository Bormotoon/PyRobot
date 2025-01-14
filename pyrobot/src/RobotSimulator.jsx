import React, { useEffect, useRef, useState } from 'react';
import { Button, Card, CardContent, CardHeader, Typography, Grid } from '@mui/material';
import { ChevronUp, ChevronDown, ChevronLeft, ChevronRight } from 'lucide-react';

const RobotSimulator = () => {
    const [width, setWidth] = useState(7);
    const [height, setHeight] = useState(7);
    const [editMode, setEditMode] = useState(false);
    const [robotPos, setRobotPos] = useState({ x: 0, y: 0 });
    const [walls, setWalls] = useState(new Set());
    const [permanentWalls, setPermanentWalls] = useState(new Set());
    const [markers, setMarkers] = useState({});
    const [coloredCells, setColoredCells] = useState(new Set());
    const [statusMessage, setStatusMessage] = useState("Click between cells to add/remove walls");
    const canvasRef = useRef(null);

    useEffect(() => {
        setupPermanentWalls();
        drawField();
    }, [robotPos, width, height, walls, coloredCells, markers]);

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

    const drawField = () => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const cellSize = 50;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw colored cells
        ctx.fillStyle = 'gray';
        coloredCells.forEach(cell => {
            const [x, y] = cell.split(',').map(Number);
            ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
        });

        // Draw robot
        const robotX = robotPos.x * cellSize + cellSize / 2;
        const robotY = robotPos.y * cellSize + cellSize / 2;
        const diamondSize = cellSize * 0.4 * 1.5; // Increase size by 1.5 times
        ctx.fillStyle = '#FF4500';
        ctx.beginPath();
        ctx.moveTo(robotX, robotY - diamondSize / 2);
        ctx.lineTo(robotX + diamondSize / 2, robotY);
        ctx.lineTo(robotX, robotY + diamondSize / 2);
        ctx.lineTo(robotX - diamondSize / 2, robotY);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        // Draw markers
        Object.keys(markers).forEach(key => {
            const [x, y] = key.split(',').map(Number);
            ctx.fillStyle = 'white';
            ctx.beginPath();
            ctx.arc((x + 0.75) * cellSize, (y + 0.75) * cellSize, cellSize * 0.15, 0, 2 * Math.PI);
            ctx.fill();
            ctx.strokeStyle = 'black'; // Change outline color to black
            ctx.lineWidth = 1; // Halve the thickness of the outline
            ctx.stroke();
        });

        // Draw walls
        ctx.strokeStyle = '#C8C80F';
        ctx.lineWidth = 8;
        walls.forEach(wall => {
            const [x1, y1, x2, y2] = wall.split(',').map(Number);
            ctx.beginPath();
            ctx.moveTo(x1 * cellSize, y1 * cellSize);
            ctx.lineTo(x2 * cellSize, y2 * cellSize);
            ctx.stroke();
        });

        // Draw grid
        ctx.strokeStyle = '#C8C80F';
        ctx.lineWidth = 2;
        for (let x = 0; x <= width; x++) {
            for (let y = 0; y <= height; y++) {
                ctx.strokeRect(x * cellSize, y * cellSize, cellSize, cellSize);
            }
        }
    };

    const moveRobot = (direction) => {
        setRobotPos((prev) => {
            let { x, y } = prev;
            if (direction === 'up' && y > 0 && !walls.has(`${x},${y},${x},${y - 1}`)) y -= 1;
            if (direction === 'down' && y < height - 1 && !walls.has(`${x},${y + 1},${x},${y + 1}`)) y += 1;
            if (direction === 'left' && x > 0 && !walls.has(`${x},${y},${x - 1},${y}`)) x -= 1;
            if (direction === 'right' && x < width - 1 && !walls.has(`${x + 1},${y},${x + 1},${y}`)) x += 1;
            return { x, y };
        });
    };

    const handleCanvasClick = (event) => {
        if (!editMode) return;

        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const cellSize = 50;
        const gridX = Math.floor(x / cellSize);
        const gridY = Math.floor(y / cellSize);
        const margin = 5;

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
            const cell = `${gridX},${gridY}`;
            setColoredCells((prev) => {
                const newCells = new Set(prev);
                if (newCells.has(cell)) {
                    newCells.delete(cell);
                } else {
                    newCells.add(cell);
                }
                return newCells;
            });
        }
    };

    const handleCanvasRightClick = (event) => {
        event.preventDefault(); // Prevent the default context menu from appearing
        if (!editMode) return;

        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const cellSize = 50;
        const gridX = Math.floor(x / cellSize);
        const gridY = Math.floor(y / cellSize);

        const pos = `${gridX},${gridY}`;
        setMarkers((prev) => {
            const newMarkers = { ...prev };
            if (!newMarkers[pos]) {
                newMarkers[pos] = 1;
            } else {
                delete newMarkers[pos];
            }
            return newMarkers;
        });
    };

    const putMarker = () => {
        const pos = `${robotPos.x},${robotPos.y}`;
        setMarkers((prev) => {
            const newMarkers = { ...prev };
            if (!newMarkers[pos]) {
                newMarkers[pos] = 1;
            }
            return newMarkers;
        });
    };

    const pickMarker = () => {
        const pos = `${robotPos.x},${robotPos.y}`;
        setMarkers((prev) => {
            const newMarkers = { ...prev };
            if (newMarkers[pos]) {
                delete newMarkers[pos];
            }
            return newMarkers;
        });
    };

    const paintCell = () => {
        const pos = `${robotPos.x},${robotPos.y}`;
        setColoredCells((prev) => new Set(prev).add(pos));
    };

    const clearCell = () => {
        const pos = `${robotPos.x},${robotPos.y}`;
        setColoredCells((prev) => {
            const newCells = new Set(prev);
            newCells.delete(pos);
            return newCells;
        });
    };

    const increaseWidth = () => {
        if (editMode) {
            setWidth((prev) => prev + 1);
            setupPermanentWalls();
        }
    };

    const decreaseWidth = () => {
        if (editMode && width > 1) {
            setWidth((prev) => prev - 1);
            setupPermanentWalls();
        }
    };

    const increaseHeight = () => {
        if (editMode) {
            setHeight((prev) => prev + 1);
            setupPermanentWalls();
        }
    };

    const decreaseHeight = () => {
        if (editMode && height > 1) {
            setHeight((prev) => prev - 1);
            setupPermanentWalls();
        }
    };

    return (
        <div style={{ display: 'flex', gap: '16px', padding: '16px' }}>
            {/* Controls */}
            <Card className="card">
                <CardHeader
                    title={<Typography variant="h6" style={{ textAlign: 'center' }}>Controls</Typography>}
                />
                <CardContent>
                    <Grid container spacing={2} alignItems="center" justifyContent="center">
                        {/* Directional Buttons */}
                        <Grid item xs={4}></Grid>
                        <Grid item xs={4}>
                            <Button
                                variant="contained"
                                className="button"
                                onClick={() => moveRobot('up')}
                            >
                                <ChevronUp />
                            </Button>
                        </Grid>
                        <Grid item xs={4}></Grid>

                        <Grid item xs={4}>
                            <Button
                                variant="contained"
                                className="button"
                                onClick={() => moveRobot('left')}
                            >
                                <ChevronLeft />
                            </Button>
                        </Grid>
                        <Grid item xs={4}></Grid>
                        <Grid item xs={4}>
                            <Button
                                variant="contained"
                                className="button"
                                onClick={() => moveRobot('right')}
                            >
                                <ChevronRight />
                            </Button>
                        </Grid>

                        <Grid item xs={4}></Grid>
                        <Grid item xs={4}>
                            <Button
                                variant="contained"
                                className="button"
                                onClick={() => moveRobot('down')}
                            >
                                <ChevronDown />
                            </Button>
                        </Grid>
                        <Grid item xs={4}></Grid>

                        {/* Other Buttons */}
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

                        <Grid item xs={12}>
                            <Button
                                variant="outlined"
                                className="button full-width-outlined"
                                onClick={() => setEditMode(!editMode)}
                            >
                                {editMode ? 'Exit Edit Mode' : 'Enter Edit Mode'}
                            </Button>
                        </Grid>

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

            {/* Canvas */}
            <Card className="card-controls">
                <canvas
                    ref={canvasRef}
                    width={width * 50}
                    height={height * 50}
                    className={editMode ? 'edit-mode' : ''}
                    onClick={handleCanvasClick}
                    onContextMenu={handleCanvasRightClick} // Add right-click event listener
                />
                <Typography variant="body2">{statusMessage}</Typography>
            </Card>
        </div>
    );
};

export default RobotSimulator;