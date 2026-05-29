import { useContext } from 'react';
import { AppDataContext } from '../context/AppDataContext';

export function useAppData() {
  const ctx = useContext(AppDataContext);
  if (!ctx) throw new Error('useAppData must be used inside <AppDataProvider>');
  return ctx;
}
