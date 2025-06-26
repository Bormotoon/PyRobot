/**
 * @file UserLog.jsx
 * @description Современный компонент для отображения лог-сообщений в стиле Material Design 3.
 * Подписывается на обновления Logger и рендерит каждую строку с применением современных стилей.
 * Добавлена автопрокрутка, группировка сообщений, иконки для разных типов логов.
 */

import React, { useState, useEffect, useRef } from 'react';
import {
	Card,
	CardContent,
	Typography,
	Box,
	Paper,
	Chip,
	Divider,
	IconButton,
	Tooltip,
	useTheme
} from '@mui/material';
import {
	Code as CodeIcon,
	PlayArrow as PlayIcon,
	Error as ErrorIcon,
	Info as InfoIcon,
	Navigation as MovementIcon,
	Edit as EditIcon,
	Clear as ClearIcon,
	Visibility as VisibilityIcon,
	FullscreenExit as FullscreenExitIcon
} from '@mui/icons-material';
import logger from '../../Logger';
import './UserLog.css';

const UserLog = ({ steps = [], error = '' }) => {
	const theme = useTheme();
	const [logText, setLogText] = useState(logger.getLog());
	const [isFullscreen, setIsFullscreen] = useState(false);
	const logContainer = useRef();
	const cardRef = useRef();

	const handleLogUpdate = (newLog) => {
		setLogText(newLog);
	};

	useEffect(() => {
		logger.subscribe(handleLogUpdate);
		scrollToBottom();
		
		return () => {
			logger.unsubscribe(handleLogUpdate);
		};
	}, []);

	useEffect(() => {
		scrollToBottom();
	}, [logText, steps, error]);

	// Обработчик ESC для закрытия fullscreen режима
	useEffect(() => {
		const handleEscape = (event) => {
			if (event.key === 'Escape' && isFullscreen) {
				setIsFullscreen(false);
			}
		};

		if (isFullscreen) {
			document.addEventListener('keydown', handleEscape);
			return () => document.removeEventListener('keydown', handleEscape);
		}
	}, [isFullscreen]);

	const scrollToBottom = () => {
		if (logContainer.current) {
			setTimeout(() => {
				logContainer.current.scrollTop = logContainer.current.scrollHeight;
			}, 100);
		}
	};

	const clearLog = () => {
		logger.clearLog();
		// Локальное состояние обновится автоматически через подписку, но можно и сразу
		// setLogText('');
	};

	const toggleFullscreen = () => {
		setIsFullscreen(prev => !prev);
	};

	// Получаем позицию карточки для правильного позиционирования в fullscreen
	const getCardPosition = () => {
		if (!cardRef.current || !isFullscreen) return {};
		
		const rect = cardRef.current.getBoundingClientRect();
		return {
			left: rect.left,
			width: rect.width,
		};
	};

	const getLogIcon = (line) => {
		if (line.startsWith('[Movement]')) return <MovementIcon fontSize="small" />;
		if (line.startsWith('[Event]')) return <InfoIcon fontSize="small" />;
		if (line.startsWith('[Command]')) return <CodeIcon fontSize="small" />;
		if (line.startsWith('[Error]')) return <ErrorIcon fontSize="small" />;
		if (line.startsWith('[Step]')) return <PlayIcon fontSize="small" />;
		if (line.startsWith('[EditMode]')) return <EditIcon fontSize="small" />;
		return <InfoIcon fontSize="small" />;
	};

	const getLogColor = (line) => {
		if (line.startsWith('[Movement]')) return theme.palette.primary.main;
		if (line.startsWith('[Event]')) return theme.palette.info.main;
		if (line.startsWith('[Command]')) return theme.palette.secondary.main;
		if (line.startsWith('[Error]')) return theme.palette.error.main;
		if (line.startsWith('[Step]')) return theme.palette.success.main;
		if (line.startsWith('[EditMode]')) return theme.palette.warning.main;
		return theme.palette.text.secondary;
	};

	const lines = logText ? logText.split('\n').filter(line => line.trim()) : [];
	const stepLines = steps.map((step, index) =>
		`[Step] Шаг ${index + 1}: Робот на (${step.robot.x}, ${step.robot.y}), закрашенные клетки: ${step.coloredCells.length > 0 ? step.coloredCells.join(', ') : 'нет'}`
	);
	const finalLines = [...lines, ...stepLines];
	
	if (error) {
		finalLines.push(`[Error] ${error}`);
		finalLines.push('[Error] Выполнение прервано из-за ошибки.');
	}

	return (
		<Card
			ref={cardRef}
			elevation={isFullscreen ? 8 : 1}
			sx={{
				display: 'flex',
				flexDirection: 'column',
				borderRadius: isFullscreen ? 2 : 3,
				overflow: 'hidden',
				height: isFullscreen ? 'calc(100vh - 32px)' : '100%',
				position: isFullscreen ? 'fixed' : 'relative',
				top: isFullscreen ? 16 : 'auto',
				left: isFullscreen ? getCardPosition().left : 'auto',
				right: isFullscreen ? 'auto' : 'auto',
				bottom: isFullscreen ? 16 : 'auto',
				width: isFullscreen ? getCardPosition().width : 'auto',
				zIndex: isFullscreen ? 9999 : 'auto',
				transition: 'all 0.3s ease',
				bgcolor: 'background.paper',
				...(isFullscreen && {
					boxShadow: theme.shadows[24],
					border: `2px solid ${theme.palette.primary.main}`,
				})
			}}
		>
			<CardContent sx={{ 
				px: isFullscreen ? { xs: 3, sm: 4 } : { xs: 2, sm: 3 },
				py: isFullscreen ? { xs: 2, sm: 3 } : { xs: 1.5, sm: 2 },
				display: 'flex',
				flexDirection: 'column',
				height: '100%',
				pb: isFullscreen ? { xs: 2, sm: 3 } : { xs: 1.5, sm: 2 }
			}}>
				{/* Заголовок консоли */}
				<Box sx={{
					display: 'flex',
					alignItems: 'center',
					justifyContent: 'space-between',
					mb: isFullscreen ? { xs: 2, sm: 2.5 } : { xs: 1.5, sm: 2 },
					flexShrink: 0,
					py: isFullscreen ? { xs: 1, sm: 1.5 } : 0,
					...(isFullscreen && {
						borderBottom: `1px solid ${theme.palette.divider}`,
						pb: { xs: 1.5, sm: 2 }
					})
				}}>
					<Box sx={{ 
						display: 'flex', 
						alignItems: 'center', 
						gap: 1,
						flex: 1,
						minWidth: 0 // Позволяет flex-элементу сжиматься
					}}>
						<CodeIcon 
							color="primary" 
							fontSize={isFullscreen ? 'medium' : 'small'}
							sx={{ flexShrink: 0 }}
						/>
						<Typography 
							variant={isFullscreen ? 'h6' : 'subtitle2'} 
							fontWeight={500}
							sx={{ 
								fontSize: isFullscreen ? '1.25rem' : { xs: '0.8rem', sm: '0.875rem' },
								flexShrink: 1,
								minWidth: 0,
								overflow: 'hidden',
								textOverflow: 'ellipsis',
								whiteSpace: 'nowrap'
							}}
						>
							Консоль выполнения
						</Typography>
						<Chip 
							label={`${finalLines.length} событий`}
							size={isFullscreen ? 'medium' : 'small'}
							variant="outlined"
							sx={{ 
								fontSize: isFullscreen ? '0.875rem' : { xs: '0.7rem', sm: '0.75rem' },
								height: isFullscreen ? 32 : { xs: 20, sm: 24 },
								flexShrink: 0
							}}
						/>
					</Box>
					
					<Box sx={{ 
						display: 'flex', 
						gap: 0.5,
						flexShrink: 0,
						minWidth: 'fit-content'
					}}>
						<Tooltip title="Очистить консоль">
							<IconButton 
								size={isFullscreen ? 'medium' : 'small'}
								onClick={clearLog}
								sx={{
									...(isFullscreen && {
										bgcolor: 'action.hover',
										'&:hover': {
											bgcolor: 'action.selected',
										}
									})
								}}
							>
								<ClearIcon fontSize={isFullscreen ? 'medium' : 'small'} />
							</IconButton>
						</Tooltip>
						
						<Tooltip title={isFullscreen ? 'Свернуть консоль (ESC)' : 'Развернуть консоль'}>
							<IconButton 
								size={isFullscreen ? 'medium' : 'small'}
								onClick={toggleFullscreen}
								sx={{
									color: isFullscreen ? 'error.main' : 'inherit',
									...(isFullscreen && {
										bgcolor: 'error.light',
										color: 'error.contrastText',
										'&:hover': {
											bgcolor: 'error.main',
										}
									})
								}}
							>
								{isFullscreen ? <FullscreenExitIcon fontSize="medium" /> : <VisibilityIcon fontSize="small" />}
							</IconButton>
						</Tooltip>
					</Box>
				</Box>

				<Divider sx={{ 
					mb: isFullscreen ? { xs: 2, sm: 2.5 } : { xs: 1.5, sm: 2 }, 
					flexShrink: 0,
					display: isFullscreen ? 'none' : 'block' // Скрываем разделитель в fullscreen, так как есть border
				}} />

				{/* Контент консоли */}
				<Box sx={{
					flexGrow: 1,
					minHeight: 0,
					overflow: 'hidden'
				}}>
					<Paper
						ref={logContainer}
						elevation={0}
						sx={{
							height: '100%',
							overflowY: 'auto',
							background: isFullscreen ? theme.palette.background.default : theme.palette.grey[50],
							border: `1px solid ${theme.palette.divider}`,
							borderRadius: isFullscreen ? 3 : 2,
							fontFamily: 'var(--font-family-monospace)',
							fontSize: isFullscreen ? { xs: '0.8rem', sm: '0.85rem' } : { xs: '0.7rem', sm: '0.75rem' },
							lineHeight: 1.4,
							'&::-webkit-scrollbar': {
								width: isFullscreen ? '8px' : '6px',
							},
							'&::-webkit-scrollbar-track': {
								background: theme.palette.grey[100],
							},
							'&::-webkit-scrollbar-thumb': {
								background: theme.palette.grey[400],
								borderRadius: '4px',
								'&:hover': {
									background: theme.palette.grey[500],
								}
							}
						}}
					>
						{finalLines.length === 0 ? (
							<Box sx={{ 
								p: isFullscreen ? { xs: 3, sm: 4 } : { xs: 2, sm: 3 }, 
								textAlign: 'center', 
								color: theme.palette.text.secondary,
								fontStyle: 'italic',
								fontSize: isFullscreen ? '1rem' : 'inherit'
							}}>
								Консоль пуста. Выполните код для просмотра логов.
							</Box>
						) : (
							finalLines.map((line, index) => {
								const icon = getLogIcon(line);
								const color = getLogColor(line);
								
								return (
									<Box
										key={index}
										sx={{
											display: 'flex',
											alignItems: 'flex-start',
											gap: isFullscreen ? 1.5 : 1,
											p: isFullscreen ? { xs: 1, sm: 1.25 } : { xs: 0.5, sm: 0.75 },
											px: isFullscreen ? { xs: 2, sm: 2.5 } : { xs: 1, sm: 1.5 },
											borderLeft: `${isFullscreen ? 4 : 3}px solid ${color}`,
											backgroundColor: index % 2 === 0 ? 'rgba(0, 0, 0, 0.02)' : 'transparent',
											'&:hover': {
												backgroundColor: isFullscreen ? 'rgba(0, 0, 0, 0.06)' : 'rgba(0, 0, 0, 0.04)',
											},
											transition: 'background-color 0.2s ease',
										}}
									>
										<Box sx={{ 
											color: color, 
											mt: 0.2,
											minWidth: isFullscreen ? '20px' : '16px',
											display: 'flex',
											justifyContent: 'center'
										}}>
											{React.cloneElement(icon, { 
												fontSize: isFullscreen ? 'medium' : 'small' 
											})}
										</Box>
										<Typography 
											variant="body2" 
											sx={{ 
												color: line.startsWith('[Error]') ? theme.palette.error.main : theme.palette.text.primary,
												fontWeight: line.startsWith('[Error]') ? 'bold' : 'normal',
												wordBreak: 'break-word',
												fontSize: 'inherit',
												lineHeight: isFullscreen ? 1.6 : 1.4
											}}
										>
											{line}
										</Typography>
									</Box>
								);
							})
						)}
					</Paper>
				</Box>
			</CardContent>
		</Card>
	);
};

export default UserLog;