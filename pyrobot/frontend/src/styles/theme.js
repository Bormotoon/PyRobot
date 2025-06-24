/**
 * @file theme.js
 * @description Конфигурация темы Material-UI для симулятора робота.
 * Современная тема в стиле Material Design 3 с красивыми цветами и компонентами.
 */

import {createTheme} from '@mui/material/styles';

// Создаем тему с использованием функции createTheme из Material-UI.
const theme = createTheme({
	// Определение цветовой палитры в стиле Material Design 3
	palette: {
		mode: 'light',
		// Основные цвета
		primary: {
			main: '#1976d2',
			light: '#42a5f5',
			dark: '#1565c0',
			contrastText: '#ffffff',
		}, 
		secondary: {
			main: '#9c27b0',
			light: '#ba68c8',
			dark: '#7b1fa2',
			contrastText: '#ffffff',
		},

		// Дополнительные цвета для различных состояний
		success: {
			main: '#2e7d32',
			light: '#4caf50',
			dark: '#1b5e20',
			contrastText: '#ffffff',
		}, 
		error: {
			main: '#d32f2f',
			light: '#f44336',
			dark: '#c62828',
			contrastText: '#ffffff',
		}, 
		warning: {
			main: '#ed6c02',
			light: '#ff9800',
			dark: '#e65100',
			contrastText: '#ffffff',
		}, 
		info: {
			main: '#0288d1',
			light: '#03a9f4',
			dark: '#01579b',
			contrastText: '#ffffff',
		},

		// Фоновые цвета
		background: {
			default: '#fafafa',
			paper: '#ffffff',
		},
		
		// Дополнительный набор серых тонов
		grey: {
			50: '#fafafa',
			100: '#f5f5f5',
			200: '#eeeeee',
			300: '#e0e0e0',
			400: '#bdbdbd',
			500: '#9e9e9e',
			600: '#757575',
			700: '#616161',
			800: '#424242',
			900: '#212121',
		},
	},

	// Современные настройки формы
	shape: {
		borderRadius: 12, // Более округлые углы в стиле Material Design 3
	},

	// Обновленная типографика
	typography: {
		fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
		fontWeightLight: 300,
		fontWeightRegular: 400,
		fontWeightMedium: 500,
		fontWeightBold: 700,
		
		h1: {
			fontSize: '2.5rem',
			fontWeight: 300,
			lineHeight: 1.2,
		},
		h2: {
			fontSize: '2rem',
			fontWeight: 300,
			lineHeight: 1.2,
		},
		h3: {
			fontSize: '1.75rem',
			fontWeight: 400,
			lineHeight: 1.2,
		},
		h4: {
			fontSize: '1.5rem',
			fontWeight: 400,
			lineHeight: 1.2,
		},
		h5: {
			fontSize: '1.25rem',
			fontWeight: 400,
			lineHeight: 1.2,
		},
		h6: {
			fontSize: '1rem',
			fontWeight: 500,
			lineHeight: 1.2,
		},
		button: {
			fontWeight: 500,
			fontSize: '0.875rem',
			textTransform: 'none', // Убираем капитализацию кнопок
		},
	},

	// Кастомизация компонентов
	components: {
		// Стили для кнопок
		MuiButton: {
			styleOverrides: {
				root: {
					borderRadius: 8,
					padding: '8px 16px',
					boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
					transition: 'all 0.2s ease-in-out',
					'&:hover': {
						boxShadow: '0 4px 8px rgba(0,0,0,0.15)',
					},
				},
				contained: {
					boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
					'&:hover': {
						boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
					},
				},
			},
		},
		
		// Стили для карточек
		MuiCard: {
			styleOverrides: {
				root: {
					boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
					borderRadius: 16,
					transition: 'all 0.2s ease-in-out',
					'&:hover': {
						boxShadow: '0 8px 25px rgba(0, 0, 0, 0.15)',
					},
				},
			},
		},
		
		// Стили для текстовых полей
		MuiTextField: {
			styleOverrides: {
				root: {
					'& .MuiOutlinedInput-root': {
						borderRadius: 8,
						'&:hover .MuiOutlinedInput-notchedOutline': {
							borderColor: '#1976d2',
						},
					},
				},
			},
		},
		
		// Стили для диалогов
		MuiDialog: {
			styleOverrides: {
				paper: {
					borderRadius: 16,
					boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)',
				},
			},
		},
		
		// Стили для иконочных кнопок
		MuiIconButton: {
			styleOverrides: {
				root: {
					transition: 'all 0.2s ease-in-out',
					'&:hover': {
						backgroundColor: 'rgba(0, 0, 0, 0.04)',
						transform: 'scale(1.05)',
					},
				},
			},
		},
	},
});

// Экспорт темы для использования в ThemeProvider приложения.
export default theme;
