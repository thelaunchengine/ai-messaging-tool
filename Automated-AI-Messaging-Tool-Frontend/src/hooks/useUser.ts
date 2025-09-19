import { useState, useEffect } from 'react';

interface UserProps {
  name: string;
  email: string;
  avatar: string;
  thumb: string;
  role: string;
}

export default function useUser() {
  const [user, setUser] = useState<UserProps | false>(false);

  useEffect(() => {
    // Check localStorage for user data
    const adminUser = localStorage.getItem('adminUser');
    const regularUser = localStorage.getItem('user');
    
    let userData = null;
    if (adminUser) {
      userData = JSON.parse(adminUser);
    } else if (regularUser) {
      userData = JSON.parse(regularUser);
    }

    if (userData) {
      const newUser: UserProps = {
        name: userData.name || 'User',
        email: userData.email || 'user@example.com',
        avatar: '/assets/images/users/avatar-1.png',
        thumb: '/assets/images/users/avatar-thumb-1.png',
        role: userData.role || 'USER'
      };
      setUser(newUser);
    } else {
      setUser(false);
    }
  }, []);

  return user;
}
