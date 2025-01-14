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
    const [cellSize, setCellSize] = useState(50); // Add state for cell size

    useEffect(() => {
        setupPermanentWalls();
    }, [width, height]); // Add width and height to dependencies

    useEffect(() => {
        drawField();
    }, [robotPos, width, height, walls, coloredCells, markers, cellSize, permanentWalls]); // Add permanentWalls to dependencies

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
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw colored cells
        ctx.fillStyle = 'gray';
        coloredCells.forEach(cell => {
            const [x, y] = cell.split(',').map(Number);
            ctx.fillRect((x + 1) * cellSize, (y + 1) * cellSize, cellSize, cellSize);
        });

        // Draw robot
        const robotX = (robotPos.x + 1) * cellSize + cellSize / 2;
        const robotY = (robotPos.y + 1) * cellSize + cellSize / 2;
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
            ctx.arc((x + 1.75) * cellSize, (y + 1.75) * cellSize, cellSize * 0.15, 0, 2 * Math.PI);
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
            ctx.moveTo((x1 + 1) * cellSize, (y1 + 1) * cellSize);
            ctx.lineTo((x2 + 1) * cellSize, (y2 + 1) * cellSize);
            ctx.stroke();
        });

        // Draw permanent walls
        permanentWalls.forEach(wall => {
            const [x1, y1, x2, y2] = wall.split(',').map(Number);
            ctx.beginPath();
            ctx.moveTo((x1 + 1) * cellSize, (y1 + 1) * cellSize);
            ctx.lineTo((x2 + 1) * cellSize, (y2 + 1) * cellSize);
            ctx.stroke();
        });

        // Draw grid
        ctx.strokeStyle = '#C8C80F';
        ctx.lineWidth = 2;
        for (let x = 0; x <= width + 2; x++) {
            for (let y = 0; y <= height + 2; y++) {
                ctx.strokeRect(x * cellSize, y * cellSize, cellSize, cellSize);
            }
        }
    };

    const handleCanvasClick = (event) => {
        if (!editMode) return;

        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const gridX = Math.floor(x / cellSize) - 1;
        const gridY = Math.floor(y / cellSize) - 1;
        const margin = 5;

        if (gridX < 0 || gridX >= width || gridY < 0 || gridY >= height) {
            return; // Prevent actions outside the main field
        }

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
            const pos = `${gridX},${gridY}`;
            setColoredCells((prev) => {
                const newCells = new Set(prev);
                if (newCells.has(pos)) {
                    newCells.delete(pos);
                } else {
                    newCells.add(pos);
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
        const gridX = Math.floor(x / cellSize) - 1;
        const gridY = Math.floor(y / cellSize) - 1;

        if (gridX < 0 || gridX >= width || gridY < 0 || gridY >= height) return; // Prevent placing markers outside the main field

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

    const moveRobot = (direction) => {
        setRobotPos((prevPos) => {
            let newPos = { ...prevPos };
            switch (direction) {
                case 'up':
                    if (newPos.y > 0) newPos.y -= 1;
                    break;
                case 'down':
                    if (newPos.y < height - 1) newPos.y += 1;
                    break;
                case 'left':
                    if (newPos.x > 0) newPos.x -= 1;
                    break;
                case 'right':
                    if (newPos.x < width - 1) newPos.x += 1;
                    break;
                default:
                    break;
            }
            return newPos;
        });
    };

    const handleCanvasWheel = (event) => {
        event.preventDefault();
        event.stopPropagation(); // Stop the event from propagating to parent elements
        setCellSize((prev) => Math.max(10, prev + (event.deltaY > 0 ? -5 : 5))); // Adjust cell size with a minimum value
    };

    useEffect(() => {
        const canvas = canvasRef.current;
        if (canvas) {
            const preventScroll = (event) => {
                event.preventDefault();
            };
            canvas.addEventListener('wheel', preventScroll, { passive: false });
            return () => {
                canvas.removeEventListener('wheel', preventScroll);
            };
        }
    }, []);

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
        <div className="container">
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
                    width={(width + 2) * cellSize} // Increase canvas width
                    height={(height + 2) * cellSize} // Increase canvas height
                    className={editMode ? 'edit-mode' : ''}
                    onClick={handleCanvasClick}
                    onContextMenu={handleCanvasRightClick} // Add right-click event listener
                    onWheel={handleCanvasWheel} // Add wheel event listener
                />
                <Typography variant="body2">{statusMessage}</Typography>
            </Card>
        </div>
    );
};

export default RobotSimulator;