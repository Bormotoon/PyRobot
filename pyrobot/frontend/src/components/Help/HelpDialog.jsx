/**
 * @file HelpDialog.jsx
 * @description Компонент диалога помощи. Данный компонент отображает руководство по использованию,
 * загруженное из файла manual.html, когда диалог открыт. При ошибке загрузки выводится сообщение об ошибке.
 */

import React, {useEffect, useState} from 'react';
import {Dialog, DialogContent, DialogTitle, IconButton} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

/**
 * Компонент диалога помощи.
 *
 * @param {Object} props - Свойства компонента.
 * @param {boolean} props.open - Флаг, указывающий, открыт ли диалог.
 * @param {function} props.onClose - Функция для закрытия диалога.
 * @returns {JSX.Element} Элемент диалога с инструкцией по использованию.
 */
const HelpDialog = ({open, onClose}) => {
	// Локальное состояние для хранения содержимого руководства (HTML)
	const [manualContent, setManualContent] = useState('');

	/**
	 * Хук useEffect для загрузки содержимого руководства при открытии диалога.
	 * Если диалог открыт, происходит запрос к файлу manual.html, расположенного в PUBLIC_URL.
	 */
	useEffect(() => {
		if (open) {
			// process.env.PUBLIC_URL - это правильный способ получить путь к папке public
			fetch(`${process.env.PUBLIC_URL}/manual.html`)
				.then(response => response.ok ? response.text() : Promise.reject(`HTTP error ${response.status}`)) // Проверка статуса ответа
				.then(html => setManualContent(html))
				.catch(err => {
					console.error("Failed to load manual.html:", err);
					setManualContent('<p style="color: red;"><strong>Ошибка:</strong> Не удалось загрузить файл справки.</p>');
				});
		}
	}, [open]);

	return (<Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
			{/* Заголовок диалога с названием и кнопкой закрытия */}
			<DialogTitle>
				Руководство по использованию
				<IconButton
					aria-label="close"
					onClick={onClose}
					// Кнопка закрытия расположена в правом верхнем углу
					style={{position: 'absolute', right: 8, top: 8}}
				>
					<CloseIcon/>
				</IconButton>
			</DialogTitle>
			{/* Контейнер для содержимого диалога с разделителями */}
			<DialogContent dividers>
				{/* Отображение содержимого руководства. Для вставки HTML используется dangerouslySetInnerHTML */}
				<div dangerouslySetInnerHTML={{__html: manualContent}}/>
			</DialogContent>
		</Dialog>);
};

export default HelpDialog;
