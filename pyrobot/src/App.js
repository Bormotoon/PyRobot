import React from 'react';
import RobotSimulator from './RobotSimulator';
import './App.css';
import './styles.css'; // Подключаем новый файл стилей
import { createTheme, ThemeProvider } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: { main: '#4CAF50' },
    secondary: { main: '#FF9800' },
  },
});

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Robot Simulator</h1>
        <RobotSimulator />
      </header>
    </div>
  );
}

export default App;