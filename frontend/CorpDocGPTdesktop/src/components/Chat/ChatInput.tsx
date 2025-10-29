import React, { useState } from 'react';
import {
  Box,
  TextField,
  IconButton,
  Paper,
} from '@mui/material';
import {
  Send as SendIcon,
} from '@mui/icons-material';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export const ChatInput: React.FC<ChatInputProps> = ({ 
  onSendMessage, 
  disabled = false,
  placeholder = "Задайте вопрос о документах университета..." 
}) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <Paper
      component="form"
      onSubmit={handleSubmit}
      elevation={1}
      sx={{
        p: 1.5, // Уменьшил padding
        borderRadius: 2,
        backgroundColor: 'background.paper',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <TextField
          fullWidth
          multiline
          maxRows={1}
          placeholder={placeholder}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={disabled}
          variant="outlined"
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 1.5,
              '& textarea': {
                resize: 'none',
                minHeight: '20px',
                maxHeight: '20px',
                lineHeight: '20px',
                padding: '8px 12px',
                fontSize: '0.9rem',
              },
              '& fieldset': {
                borderColor: 'divider',
              },
            },
          }}
        />
        
        <IconButton
          type="submit"
          disabled={!message.trim() || disabled}
          sx={{
            height: '40px',
            width: '40px',
            backgroundColor: 'primary.main',
            color: 'white',
            '&:hover': {
              backgroundColor: 'primary.dark',
            },
            '&:disabled': {
              backgroundColor: 'action.disabled',
            },
          }}
        >
          <SendIcon sx={{ fontSize: 18 }} />
        </IconButton>
      </Box>
    </Paper>
  );
};