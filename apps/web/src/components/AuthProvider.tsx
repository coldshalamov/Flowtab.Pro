"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { User } from "@/lib/apiTypes";
import { getMe, login as apiLogin, register as apiRegister } from "@/lib/api";
import { useRouter } from "next/navigation";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  completeLogin: (token: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem("token");
      if (token) {
        try {
          const userData = await getMe(token);
          setUser(userData);
        } catch (error) {
          console.error("Failed to fetch user:", error);
          localStorage.removeItem("token");
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const completeLogin = async (token: string) => {
    localStorage.setItem("token", token);
    const userData = await getMe(token);
    setUser(userData);
  };

  const login = async (email: string, password: string) => {
    try {
      const { access_token } = await apiLogin(email, password);
      await completeLogin(access_token);
      router.push("/");
      router.refresh();
    } catch (error) {
      throw error;
    }
  };

  const register = async (email: string, password: string) => {
    try {
      await apiRegister(email, password);
      // Auto login after register
      await login(email, password);
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
    router.push("/");
    router.refresh();
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, completeLogin, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
