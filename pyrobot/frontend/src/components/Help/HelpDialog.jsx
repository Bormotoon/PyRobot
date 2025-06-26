/**
 * @file HelpDialog.jsx
 * @description Современный компонент диалога помощи в стиле Material Design 3.
 * Отображает руководство по использованию с красивой анимацией и современным UX.
 */

import React, {useEffect, useState} from 'react';
import {
	Dialog, 
	DialogContent, 
	DialogTitle, 
	IconButton, 
	Typography,
	Box,
	Paper,
	Skeleton,
	Fade,
	useTheme
} from '@mui/material';
import {
	Close as CloseIcon,
	MenuBook as MenuBookIcon
} from '@mui/icons-material';

/**
 * Современный компонент диалога помощи.
 *
 * @param {Object} props - Свойства компонента.
 * @param {boolean} props.open - Флаг, указывающий, открыт ли диалог.
 * @param {function} props.onClose - Функция для закрытия диалога.
 * @returns {JSX.Element} Элемент диалога с инструкцией по использованию.
 */
const HelpDialog = ({open, onClose}) => {
	const theme = useTheme();
	// Локальное состояние для хранения содержимого руководства (HTML)
	const [manualContent, setManualContent] = useState('');
	const [isLoading, setIsLoading] = useState(false);

	/**
	 * Хук useEffect для загрузки содержимого руководства при открытии диалога.
	 */
	useEffect(() => {
		if (open && !manualContent && !isLoading) {
			setIsLoading(true);
			
			// process.env.PUBLIC_URL - это правильный способ получить путь к папке public
			fetch(`${process.env.PUBLIC_URL}/manual.html`)
				.then(response => {
					if (!response.ok) {
						throw new Error(`HTTP error ${response.status}`);
					}
					return response.text();
				})
				.then(html => {
					setManualContent(html);
				})
				.catch(err => {
					console.error("Failed to load manual.html:", err);
					setManualContent(`
						<div style="text-align: center; padding: 2rem; color: ${theme.palette.error.main};">
							<h3>⚠️ Ошибка загрузки</h3>
							<p>Не удалось загрузить файл справки.</p>
							<p style="font-size: 0.875rem; opacity: 0.7;">Код ошибки: ${err.message}</p>
						</div>
					`);
				})
				.finally(() => {
					setIsLoading(false);
				});
		}
	}, [open, manualContent, isLoading, theme.palette.error.main]);

	return (
		<Dialog 
			open={open} 
			onClose={onClose} 
			maxWidth="lg" 
			fullWidth
			PaperProps={{
				sx: {
					borderRadius: 3,
					background: `linear-gradient(135deg, ${theme.palette.background.paper} 0%, ${theme.palette.grey[50]} 100%)`,
					backdropFilter: 'blur(10px)',
					boxShadow: theme.shadows[24],
				}
			}}
			TransitionComponent={Fade}
			TransitionProps={{
				timeout: 400,
			}}
		>
			{/* Современный заголовок диалога */}
			<DialogTitle sx={{
				background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
				color: 'white',
				display: 'flex',
				alignItems: 'center',
				justifyContent: 'space-between',
				padding: theme.spacing(2, 3),
				borderRadius: '12px 12px 0 0',
			}}>
				<Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
					<MenuBookIcon sx={{ fontSize: 28 }} />
					<Typography variant="h5" component="h2" fontWeight="medium">
						Руководство по использованию
					</Typography>
				</Box>
				
				<IconButton
					aria-label="Закрыть справку"
					onClick={onClose}
					sx={{
						color: 'white',
						'&:hover': {
							backgroundColor: 'rgba(255, 255, 255, 0.1)',
							transform: 'scale(1.1)',
						},
						transition: 'all 0.2s ease',
					}}
				>
					<CloseIcon />
				</IconButton>
			</DialogTitle>
			
			{/* Контейнер для содержимого диалога */}
			<DialogContent sx={{
				padding: 0,
				background: theme.palette.background.paper,
			}}>
				{isLoading ? (
					// Красивый скелетон во время загрузки
					<Box sx={{ p: 3 }}>
						<Skeleton variant="text" height={40} sx={{ mb: 2 }} />
						<Skeleton variant="rectangular" height={200} sx={{ mb: 2, borderRadius: 2 }} />
						<Skeleton variant="text" height={30} sx={{ mb: 1 }} />
						<Skeleton variant="text" height={30} sx={{ mb: 1 }} />
						<Skeleton variant="text" height={30} width="60%" />
					</Box>
				) : (
					<Paper elevation={0} sx={{
						minHeight: 400,
						maxHeight: '70vh',
						overflow: 'auto',
						background: 'transparent',
						'&::-webkit-scrollbar': {
							width: '8px',
						},
						'&::-webkit-scrollbar-track': {
							background: theme.palette.grey[100],
							borderRadius: '4px',
						},
						'&::-webkit-scrollbar-thumb': {
							background: theme.palette.grey[400],
							borderRadius: '4px',
							'&:hover': {
								background: theme.palette.grey[600],
							}
						}
					}}>
						{/* Контейнер для HTML-контента с улучшенной типографикой */}
						<Box 
							sx={{
								p: 3,
								'& h1, & h2, & h3, & h4, & h5, & h6': {
									color: theme.palette.primary.main,
									fontFamily: theme.typography.fontFamily,
									fontWeight: 500,
									marginTop: theme.spacing(3),
									marginBottom: theme.spacing(1),
								},
								'& h1': { fontSize: '2rem' },
								'& h2': { fontSize: '1.75rem' },
								'& h3': { fontSize: '1.5rem' },
								'& p': {
									color: theme.palette.text.secondary,
									lineHeight: 1.7,
									marginBottom: theme.spacing(2),
									fontSize: '1rem',
								},
								'& ul, & ol': {
									paddingLeft: theme.spacing(3),
									marginBottom: theme.spacing(2),
								},
								'& li': {
									marginBottom: theme.spacing(0.5),
									color: theme.palette.text.secondary,
								},
								'& code': {
									backgroundColor: theme.palette.grey[100],
									color: theme.palette.primary.dark,
									padding: '2px 6px',
									borderRadius: '4px',
									fontFamily: 'monospace',
									fontSize: '0.875rem',
								},
								'& pre': {
									backgroundColor: theme.palette.grey[50],
									border: `1px solid ${theme.palette.grey[200]}`,
									borderRadius: theme.shape.borderRadius,
									padding: theme.spacing(2),
									overflow: 'auto',
									marginBottom: theme.spacing(2),
								},
								'& a': {
									color: theme.palette.primary.main,
									textDecoration: 'none',
									'&:hover': {
										textDecoration: 'underline',
									}
								},
								'& img': {
									maxWidth: '100%',
									height: 'auto',
									borderRadius: theme.shape.borderRadius,
									boxShadow: theme.shadows[2],
									marginBottom: theme.spacing(2),
								}
							}}
						>
							{/* Отображение содержимого руководства */}
							<div dangerouslySetInnerHTML={{__html: manualContent}} />
						</Box>
					</Paper>
				)}
			</DialogContent>
		</Dialog>
	);
};

export default HelpDialog;
