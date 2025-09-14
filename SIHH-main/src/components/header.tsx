
'use client';
import { Train, SlidersHorizontal } from 'lucide-react';
import { Button } from './ui/button';
import { Bell, Wifi, WifiOff } from 'lucide-react';
import { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';

type HeaderProps = {
  isManualMode: boolean;
  onToggleManualMode: () => void;
};

export default function Header({ isManualMode, onToggleManualMode }: HeaderProps) {
  const [currentTime, setCurrentTime] = useState('');
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString('en-IN', { timeZone: 'Asia/Kolkata' }));
    }, 1000);

    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    // Set initial status
    if (typeof navigator.onLine !== 'undefined') {
        setIsOnline(navigator.onLine);
    }


    return () => {
      clearInterval(timer);
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return (
    <header className="bg-primary text-primary-foreground shadow-md sticky top-0 z-20">
      <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-4">
            <div className="bg-primary-foreground text-primary p-2 rounded-md">
              <Train size={24} />
            </div>
            <h1 className="text-2xl font-bold tracking-tight">
              Indian Railways RailFlow
            </h1>
          </div>
          <div className="flex items-center gap-6">
             <div className="flex items-center gap-2 text-sm">
                {isOnline ? <Wifi size={16} className="text-green-300"/> : <WifiOff size={16} className="text-red-300" />}
                <span className={isOnline ? 'text-green-300' : 'text-red-300'}>{isOnline ? 'LIVE' : 'OFFLINE'}</span>
                <span className="text-primary-foreground/80">|</span>
                <span className="font-mono">{currentTime} (IST)</span>
             </div>
            <div className="flex items-center gap-2">
                <Button 
                  variant="ghost" 
                  size="icon" 
                  onClick={onToggleManualMode}
                  className={cn(
                    'hover:bg-primary/80',
                    isManualMode && 'bg-amber-400/20 text-amber-300 hover:bg-amber-400/30'
                  )}
                  title={isManualMode ? 'Disable Manual Control' : 'Enable Manual Control'}
                >
                  <SlidersHorizontal className="h-5 w-5" />
                  <span className="sr-only">Manual Control</span>
                </Button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
