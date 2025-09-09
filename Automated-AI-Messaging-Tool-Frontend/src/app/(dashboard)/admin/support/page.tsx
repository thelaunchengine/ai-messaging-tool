'use client';

import { useState, useRef, useEffect } from 'react';
import {
  Box,
  Grid,
  Typography,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Paper,
  Divider,
  Chip,
  IconButton,
  Badge,
  Stack,
  InputAdornment
} from '@mui/material';
import { Send, Search, Circle, AdminPanelSettings, Person, AttachFile, EmojiEmotions } from '@mui/icons-material';
import MainCard from '../../../../components/MainCard';

// Mock chat data
const mockChats = [
  {
    id: 1,
    userId: 'user1',
    userName: 'John Doe',
    userEmail: 'john@example.com',
    lastMessage: 'I need help with file upload',
    lastMessageTime: '2 minutes ago',
    unreadCount: 2,
    status: 'online',
    avatar: 'J'
  },
  {
    id: 2,
    userId: 'user2',
    userName: 'Jane Smith',
    userEmail: 'jane@example.com',
    lastMessage: 'Thank you for the help!',
    lastMessageTime: '1 hour ago',
    unreadCount: 0,
    status: 'offline',
    avatar: 'J'
  },
  {
    id: 3,
    userId: 'user3',
    userName: 'Mike Johnson',
    userEmail: 'mike@example.com',
    lastMessage: 'How do I export my reports?',
    lastMessageTime: '3 hours ago',
    unreadCount: 1,
    status: 'online',
    avatar: 'M'
  }
];

const mockMessages = [
  {
    id: 1,
    sender: 'user',
    message: 'Hello, I need help with uploading my file',
    timestamp: '10:30 AM',
    avatar: 'J'
  },
  {
    id: 2,
    sender: 'admin',
    message: "Hello! I'd be happy to help you with file upload. What specific issue are you experiencing?",
    timestamp: '10:32 AM',
    avatar: 'A'
  },
  {
    id: 3,
    sender: 'user',
    message: "The file upload keeps failing. I'm trying to upload a CSV file with website URLs",
    timestamp: '10:33 AM',
    avatar: 'J'
  },
  {
    id: 4,
    sender: 'admin',
    message: "I can help with that. Can you tell me what error message you're seeing? Also, what's the size of your CSV file?",
    timestamp: '10:35 AM',
    avatar: 'A'
  },
  {
    id: 5,
    sender: 'user',
    message: 'The error says "File format not supported" and my file is about 2MB',
    timestamp: '10:36 AM',
    avatar: 'J'
  },
  {
    id: 6,
    sender: 'admin',
    message:
      'I see the issue. Our system currently supports CSV files up to 1MB. You can either split your file into smaller parts or convert it to Excel format (.xlsx) which supports larger files. Would you like me to guide you through either option?',
    timestamp: '10:38 AM',
    avatar: 'A'
  }
];

export default function AdminSupportPage() {
  const [chats, setChats] = useState(mockChats);
  const [selectedChat, setSelectedChat] = useState(mockChats[0]);
  const [messages, setMessages] = useState(mockMessages);
  const [newMessage, setNewMessage] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = () => {
    if (newMessage.trim()) {
      const message = {
        id: messages.length + 1,
        sender: 'admin',
        message: newMessage,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        avatar: 'A'
      };
      setMessages([...messages, message]);
      setNewMessage('');

      // Update chat list
      setChats(
        chats.map((chat) =>
          chat.id === selectedChat.id ? { ...chat, lastMessage: newMessage, lastMessageTime: 'Just now', unreadCount: 0 } : chat
        )
      );
    }
  };

  const handleChatSelect = (chat: any) => {
    setSelectedChat(chat);
    // Mark messages as read
    setChats(chats.map((c) => (c.id === chat.id ? { ...c, unreadCount: 0 } : c)));
  };

  const filteredChats = chats.filter(
    (chat) =>
      chat.userName.toLowerCase().includes(searchTerm.toLowerCase()) || chat.userEmail.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const stats = [
    { label: 'Active Chats', value: chats.filter((c) => c.status === 'online').length, color: 'success' },
    { label: 'Total Users', value: chats.length, color: 'primary' },
    { label: 'Unread Messages', value: chats.reduce((sum, chat) => sum + chat.unreadCount, 0), color: 'warning' },
    { label: 'Resolved Today', value: 12, color: 'info' }
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={700} sx={{ color: '#23272E' }}>
          Support Chat
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} mb={3}>
        {stats.map((stat, idx) => (
          <Grid item xs={12} sm={6} md={3} key={idx}>
            <MainCard sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h4" fontWeight={700} color={`${stat.color}.main`}>
                {stat.value}
              </Typography>
              <Typography variant="subtitle2" color="text.secondary">
                {stat.label}
              </Typography>
            </MainCard>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3} sx={{ height: 'calc(100vh - 300px)' }}>
        {/* Chat List */}
        <Grid item xs={12} md={4}>
          <MainCard sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
              <TextField
                fullWidth
                placeholder="Search users..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  )
                }}
              />
            </Box>

            <List sx={{ flex: 1, overflow: 'auto' }}>
              {filteredChats.map((chat) => (
                <ListItem
                  key={chat.id}
                  button
                  selected={selectedChat?.id === chat.id}
                  onClick={() => handleChatSelect(chat)}
                  sx={{
                    borderBottom: '1px solid',
                    borderColor: 'divider',
                    '&.Mui-selected': {
                      backgroundColor: 'primary.light',
                      '&:hover': {
                        backgroundColor: 'primary.light'
                      }
                    }
                  }}
                >
                  <ListItemAvatar>
                    <Badge
                      overlap="circular"
                      anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                      badgeContent={
                        <Circle
                          sx={{
                            fontSize: 12,
                            color: chat.status === 'online' ? 'success.main' : 'grey.400'
                          }}
                        />
                      }
                    >
                      <Avatar sx={{ bgcolor: chat.status === 'online' ? 'success.main' : 'grey.400' }}>{chat.avatar}</Avatar>
                    </Badge>
                  </ListItemAvatar>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="subtitle2" fontWeight={600}>
                          {chat.userName}
                        </Typography>
                        {chat.unreadCount > 0 && (
                          <Chip label={chat.unreadCount} size="small" color="primary" sx={{ minWidth: 20, height: 20 }} />
                        )}
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="caption" color="text.secondary" noWrap>
                          {chat.lastMessage}
                        </Typography>
                        <Typography variant="caption" color="text.secondary" display="block">
                          {chat.lastMessageTime}
                        </Typography>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </MainCard>
        </Grid>

        {/* Chat Messages */}
        <Grid item xs={12} md={8}>
          <MainCard sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            {/* Chat Header */}
            <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Avatar sx={{ mr: 2, bgcolor: selectedChat?.status === 'online' ? 'success.main' : 'grey.400' }}>
                  {selectedChat?.avatar}
                </Avatar>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="h6" fontWeight={600}>
                    {selectedChat?.userName}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {selectedChat?.userEmail} • {selectedChat?.status}
                  </Typography>
                </Box>
                <Chip label={selectedChat?.status} color={selectedChat?.status === 'online' ? 'success' : 'default'} size="small" />
              </Box>
            </Box>

            {/* Messages */}
            <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
              <Stack spacing={2}>
                {messages.map((message) => (
                  <Box
                    key={message.id}
                    sx={{
                      display: 'flex',
                      justifyContent: message.sender === 'admin' ? 'flex-end' : 'flex-start'
                    }}
                  >
                    <Box
                      sx={{
                        maxWidth: '70%',
                        display: 'flex',
                        alignItems: 'flex-end',
                        gap: 1
                      }}
                    >
                      {message.sender === 'user' && (
                        <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>{message.avatar}</Avatar>
                      )}
                      <Paper
                        sx={{
                          p: 2,
                          backgroundColor: message.sender === 'admin' ? 'primary.main' : 'grey.100',
                          color: message.sender === 'admin' ? 'white' : 'text.primary',
                          borderRadius: 2,
                          maxWidth: '100%'
                        }}
                      >
                        <Typography variant="body2">{message.message}</Typography>
                        <Typography
                          variant="caption"
                          sx={{
                            opacity: 0.7,
                            display: 'block',
                            mt: 0.5
                          }}
                        >
                          {message.timestamp}
                        </Typography>
                      </Paper>
                      {message.sender === 'admin' && (
                        <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
                          <AdminPanelSettings />
                        </Avatar>
                      )}
                    </Box>
                  </Box>
                ))}
                <div ref={messagesEndRef} />
              </Stack>
            </Box>

            {/* Message Input */}
            <Box sx={{ p: 2, borderTop: '1px solid', borderColor: 'divider' }}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <IconButton size="small">
                  <AttachFile />
                </IconButton>
                <IconButton size="small">
                  <EmojiEmotions />
                </IconButton>
                <TextField
                  fullWidth
                  placeholder="Type your message..."
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  variant="outlined"
                  size="small"
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 3 } }}
                />
                <Button
                  variant="contained"
                  onClick={handleSendMessage}
                  disabled={!newMessage.trim()}
                  sx={{ borderRadius: 3, minWidth: 50 }}
                >
                  <Send />
                </Button>
              </Box>
            </Box>
          </MainCard>
        </Grid>
      </Grid>
    </Box>
  );
}
