import React from 'react';
import { ThemeProvider, CssBaseline } from '@mui/material';
import RobotSimulator from './components/RobotSimulator';
import theme from './styles/theme';
import './styles/styles.css';

function App() {
    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <div className="App">
                <RobotSimulator/>
            </div>
        </ThemeProvider>
    );
}

export default App;