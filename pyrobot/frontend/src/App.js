import React from 'react';
import RobotSimulator from './RobotSimulator';
import './App.css';
import './styles.css'; // Подключаем новый файл стилей

function App() {
    return (
        <div className="App">
            <header className="App-header">
                <h1>Robot Simulator</h1>
                <RobotSimulator/>
            </header>
        </div>
    );
}

export default App;