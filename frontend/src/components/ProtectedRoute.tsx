import { type ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAppData } from '../hooks/useAppData';
import { BootSplash } from './BootSplash';

interface ProtectedRouteProps {
  children: ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { user, isBootstrapping } = useAppData();

  if (isBootstrapping && !user) return <BootSplash />;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}
