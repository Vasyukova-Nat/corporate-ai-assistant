import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Chip,
  Avatar,
  useTheme,
} from '@mui/material';
import { Person as UserIcon } from '@mui/icons-material';
import { Logo } from '../Common/Logo';
import { ChatMessage } from '../../types';

interface MessageBubbleProps {
  message: ChatMessage;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  const isUser = message.role === 'user';

  const logoColor = theme.palette.primary.main;

  const assistantBg = isDark ? theme.palette.grey[800] : theme.palette.grey[50];
  const assistantTextColor = isDark
    ? theme.palette.getContrastText(theme.palette.grey[800])
    : theme.palette.text.primary;

  const userAvatarBg = isDark ? theme.palette.common.white : logoColor;
  const userIconColor = isDark ? logoColor : theme.palette.common.white;
  const userTextColor = theme.palette.getContrastText(logoColor);

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        mb: 2,
        px: 3,
      }}
    >
      <Box
        sx={{
          display: 'flex',
          alignItems: 'flex-start',
          gap: 1.5,
          maxWidth: '65%',
          flexDirection: isUser ? 'row-reverse' : 'row',
        }}
      >
        {/* Avatar */}
        {isUser ? (
          <Avatar
            sx={{
              width: 34,
              height: 34,
              bgcolor: userAvatarBg,
              color: userIconColor,
              flexShrink: 0,
            }}
          >
            <UserIcon sx={{ fontSize: 18, color: userIconColor }} />
          </Avatar>
        ) : (
          <Avatar
            sx={{
              width: 34,
              height: 34,
              bgcolor: 'transparent',
              flexShrink: 0,
            }}
          >
            <Box sx={{ width: 22, height: 22, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Logo size="small" forceWhite={isDark} />
            </Box>
          </Avatar>
        )}

        {/* Message bubble */}
        <Paper
          elevation={1}
          sx={{
            p: 1.5,
            backgroundColor: isUser ? logoColor : assistantBg,
            color: isUser ? userTextColor : assistantTextColor,
            borderRadius: isUser ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
            border: isUser ? 'none' : `1px solid ${theme.palette.divider}`,
            minWidth: '100px',
            position: 'relative',
            boxShadow: isDark ? '0 1px 4px rgba(0,0,0,0.6)' : '0 1px 6px rgba(16,24,40,0.04)',
          }}
        >
          <Typography
            variant="body1"
            sx={{
              whiteSpace: 'pre-wrap',
              lineHeight: 1.45,
              fontSize: '0.95rem',
              color: 'inherit',
            }}
          >
            {message.content}
          </Typography>

          {message.sources && message.sources.length > 0 && (
            <Box sx={{ mt: 1 }}>
              <Typography
                variant="caption"
                sx={{
                  opacity: 0.85,
                  display: 'block',
                  mb: 0.5,
                  fontSize: '0.72rem',
                  color: isUser ? userTextColor : assistantTextColor,
                }}
              >
                Источники:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {message.sources.map((source, index) => (
                  <Chip
                    key={index}
                    label={source}
                    size="small"
                    variant="outlined"
                    sx={{
                      fontSize: '0.72rem',
                      height: '24px',
                      color: isUser ? userTextColor : assistantTextColor,
                      borderColor: isUser ? 'rgba(255,255,255,0.12)' : theme.palette.divider,
                      backgroundColor: isUser ? 'rgba(255,255,255,0.04)' : 'transparent',
                    }}
                  />
                ))}
              </Box>
            </Box>
          )}

          <Typography
            variant="caption"
            sx={{
              display: 'block',
              mt: 0.5,
              opacity: 0.6,
              textAlign: isUser ? 'right' : 'left',
              fontSize: '0.68rem',
              color: isUser ? userTextColor : assistantTextColor,
            }}
          >
            {new Date(message.timestamp).toLocaleTimeString('ru-RU', {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </Typography>
        </Paper>
      </Box>
    </Box>
  );
};