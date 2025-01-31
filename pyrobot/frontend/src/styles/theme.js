// theme.js
import {createTheme} from '@mui/material/styles';

const theme = createTheme({
	palette: {
		// Основные стандартные цвета (MUI использует их для color="primary" и color="secondary")
		primary: {
			main: '#2196f3', // Синий (ранее примерно соответствовал --button-info-bg)
		},
		secondary: {
			main: '#9c27b0', // Фиолетовый, можно подправить по вкусу
		},

		// Дополнительные цвета (для color="success" и т.д.)
		success: {
			main: '#4caf50', // Зелёный
		},
		error: {
			main: '#f44336', // Красный
		},
		warning: {
			main: '#ff9800', // Оранжевый
		},
		info: {
			main: '#03a9f4', // Голубой
		},

		// Если нужно использовать "серый" в стиле "default",
		// можно ориентироваться на palette.grey (MUI v5)
		grey: {
			500: '#9e9e9e',
			700: '#757575',
		},
	},

	shape: {
		// Глобальное скругление углов в MUI-компонентах
		borderRadius: 8,
	},

	typography: {
		// Общий шрифт для Material UI
		fontFamily: 'Arial, sans-serif',
	},
});

export default theme;
