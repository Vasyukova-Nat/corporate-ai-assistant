import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';
import { MessageBubble } from './MessageBubble';
import { ChatMessage } from '../../types';

interface MessageListProps {
  messages: ChatMessage[];
  isLoading: boolean;
}

export const MessageList: React.FC<MessageListProps> = ({ messages, isLoading }) => {
  return (
    <Box sx={{ maxWidth: 800, mx: 'auto' }}>
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
      
      {isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'flex-start', my: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 2 }}>
            <CircularProgress size={20} />
            <Typography variant="body2" color="text.secondary">
              Ассистент печатает...
            </Typography>
          </Box>
        </Box>
      )}
    </Box>
  );
};