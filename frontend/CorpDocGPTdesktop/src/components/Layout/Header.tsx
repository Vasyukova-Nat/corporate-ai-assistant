import React from 'react';
import {
  AppBar,
  Toolbar,
  IconButton,
  Box,
  Typography,
  useTheme,
} from '@mui/material';
import {
  Menu as MenuIcon,
  LightMode as LightModeIcon,
  DarkMode as DarkModeIcon,
} from '@mui/icons-material';

interface HeaderProps {
  onThemeToggle: () => void;
  onMenuToggle: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onThemeToggle, onMenuToggle }) => {
  const theme = useTheme();

  return (
    <AppBar 
      position="static" 
      elevation={1}
      sx={{ 
        backgroundColor: 'background.paper',
        color: 'text.primary',
        borderBottom: 1,
        borderColor: 'divider',
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between', minHeight: '64px !important' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <IconButton
            edge="start"
            onClick={onMenuToggle}
            sx={{ color: 'text.primary' }}
          >
            <MenuIcon />
          </IconButton>
        </Box>

        <Typography variant="h6" component="div" fontWeight="medium">
          AI Ассистент для работы с документами
        </Typography>

        <IconButton onClick={onThemeToggle} sx={{ color: 'text.primary' }}>
          {theme.palette.mode === 'dark' ? <LightModeIcon /> : <DarkModeIcon />}
        </IconButton>
      </Toolbar>
    </AppBar>
  );
};