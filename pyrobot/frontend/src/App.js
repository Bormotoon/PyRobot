import React from 'react';
import RobotSimulator from './components/RobotSimulator';
import './App.css';
import './styles/styles.css'; // Подключаем новый файл стилей

function App() {
    return (
        <div className="App">
            <header className="App-header">
                <RobotSimulator/>
            </header>
        </div>
    );
}

export default App;