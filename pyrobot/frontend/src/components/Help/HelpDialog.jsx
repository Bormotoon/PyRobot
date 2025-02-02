import React, {useState, useEffect} from 'react';
import {Dialog, DialogTitle, DialogContent, IconButton} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

const HelpDialog = ({open, onClose}) => {
	const [manualContent, setManualContent] = useState('');

	useEffect(() => {
		if (open) {
			fetch(`${process.env.PUBLIC_URL}/manual.html`)
				.then(response => response.text())
				.then(html => setManualContent(html))
				.catch(err => setManualContent('<p>Ошибка загрузки инструкции.</p>'));
		}
	}, [open]);

	return (
		<Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
			<DialogTitle>
				Руководство по использованию
				<IconButton
					aria-label="close"
					onClick={onClose}
					style={{position: 'absolute', right: 8, top: 8}}
				>
					<CloseIcon/>
				</IconButton>
			</DialogTitle>
			<DialogContent dividers>
				{/* Если контент безопасен, можно использовать dangerouslySetInnerHTML */}
				<div dangerouslySetInnerHTML={{__html: manualContent}}/>
			</DialogContent>
		</Dialog>
	);
};

export default HelpDialog;
