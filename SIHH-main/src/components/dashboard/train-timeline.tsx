'use client';
import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Clock, Users, ArrowRight, MapPin, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '../ui/button';
import { useCSVTrains } from '@/hooks/use-api-data';

type TrainStatus = 'On Time' | 'At Risk' | 'Delayed' | 'scheduled' | 'departed' | 'arrived';

type Train = {
  id: string;
  status: TrainStatus;
  route: string;
  current_station: string;
  nextStop: string;
  progress: number;
  passengers: number;
  delay_minutes: number;
};

type TrainTimelineProps = {
  trains?: Train[]; // Make optional since we'll fetch data internally
};

const statusConfig: { [key in TrainStatus]: { color: string; badge: string } } = {
  'On Time': { color: 'bg-green-500', badge: 'bg-green-100 text-green-800 border-green-200' },
  'At Risk': { color: 'bg-green-500', badge: 'bg-yellow-100 text-yellow-800 border-yellow-200' },
  'Delayed': { color: 'bg-green-500', badge: 'bg-red-100 text-red-800 border-red-200' },
  'scheduled': { color: 'bg-green-500', badge: 'bg-blue-100 text-blue-800 border-blue-200' },
  'departed': { color: 'bg-green-500', badge: 'bg-green-100 text-green-800 border-green-200' },
  'arrived': { color: 'bg-green-500', badge: 'bg-gray-100 text-gray-800 border-gray-200' },
};

export default function TrainTimeline({ trains: propTrains }: TrainTimelineProps) {
  const [activeTab, setActiveTab] = useState<'current' | 'next2'>('current');
  const [currentPage, setCurrentPage] = useState(1);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const itemsPerPage = 10;
  
  // Use CSV trains data (all 100 trains)
  const { data: allTrains, loading, error, refetch } = useCSVTrains();
  
  // Use prop trains as fallback for backward compatibility
  const trainsData = allTrains || propTrains || [];
  
  // Implement local pagination
  const totalTrains = trainsData.length;
  const totalPages = Math.ceil(totalTrains / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const trains = trainsData.slice(startIndex, endIndex);
  
  const pagination = {
    page: currentPage,
    limit: itemsPerPage,
    total: totalTrains,
    total_pages: totalPages,
    has_prev: currentPage > 1,
    has_next: currentPage < totalPages
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await refetch();
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleNextPage = () => {
    if (pagination.has_next) {
      setCurrentPage(prev => prev + 1);
    }
  };

  const handlePrevPage = () => {
    if (pagination.has_prev) {
      setCurrentPage(prev => prev - 1);
    }
  };

  if (loading && !propTrains) {
    return (
      <div className='max-h-[60vh] overflow-y-auto pr-2'>
        <div className="flex justify-center items-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  if (error && !propTrains) {
    return (
      <div className='max-h-[60vh] overflow-y-auto pr-2'>
        <div className="flex justify-center items-center h-32 text-red-500">
          <p>Error loading trains: {error}</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className='max-h-[60vh] overflow-y-auto pr-2'>
        <div className="flex justify-between items-center mb-4">
             <h3 className="font-semibold text-foreground">Live Train Positions</h3>
             <div className='flex items-center gap-2'>
                <div className='flex items-center border p-1 rounded-lg bg-muted'>
                  <Button size="sm" onClick={() => setActiveTab('current')} variant={activeTab === 'current' ? 'default' : 'ghost'} className='h-7 text-xs'>Current Hour</Button>
                  <Button size="sm" onClick={() => setActiveTab('next2')} variant={activeTab === 'next2' ? 'default' : 'ghost'} className='h-7 text-xs'>Next 2 Hours</Button>
                </div>
                <Button 
                  size="sm" 
                  variant="outline" 
                  onClick={handleRefresh}
                  disabled={isRefreshing}
                  className='h-7 text-xs'
                >
                  <RefreshCw className={`h-3 w-3 mr-1 ${isRefreshing ? 'animate-spin' : ''}`} />
                  Refresh
                </Button>
             </div>
        </div>
     
      <div className="space-y-2">
        <Accordion type="single" collapsible className="w-full">
          {trains.map((train) => (
            <AccordionItem value={train.id} key={train.id} className="border-b-0">
               <Card className="mb-2 overflow-hidden">
                <AccordionTrigger className='p-4 hover:no-underline'>
                  <div className="w-full">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-bold text-sm text-primary">{train.id}</span>
                      <Badge className={`text-xs ${statusConfig[train.status].badge}`}>
                        {train.status} {train.delay_minutes > 0 && `(${train.delay_minutes} min)`}
                      </Badge>
                    </div>
                    <Progress value={train.progress} className="h-2" indicatorClassName={statusConfig[train.status].color} />
                     <div className="flex justify-between items-center text-xs text-muted-foreground mt-1">
                        <span>{train.route.split(' to ')[0]}</span>
                        <span>{train.route.split(' to ')[1]}</span>
                    </div>
                  </div>
                </AccordionTrigger>
                <AccordionContent>
                  <div className="p-4 pt-0 text-sm bg-muted/50">
                    <div className='grid grid-cols-2 gap-4'>
                        <div>
                            <div className='flex items-center gap-2 text-muted-foreground'><MapPin size={14}/> <span>Current Location</span></div>
                            <p className='font-semibold'>{train.current_station}</p>
                        </div>
                         <div>
                            <div className='flex items-center gap-2 text-muted-foreground'><ArrowRight size={14}/> <span>Next Stop</span></div>
                            <p className='font-semibold'>{train.nextStop}</p>
                        </div>
                         <div>
                            <div className='flex items-center gap-2 text-muted-foreground'><Users size={14}/> <span>Passengers</span></div>
                            <p className='font-semibold'>{train.passengers}</p>
                        </div>
                        <div>
                            <div className='flex items-center gap-2 text-muted-foreground'><Clock size={14}/> <span>Delay</span></div>
                            <p className={`font-semibold ${train.delay_minutes > 0 ? 'text-red-500' : 'text-green-600'}`}>{train.delay_minutes > 0 ? `${train.delay_minutes} minutes` : 'On Time'}</p>
                        </div>
                    </div>
                  </div>
                </AccordionContent>
              </Card>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
      
      {/* Pagination Controls */}
      {totalTrains > 0 && (
        <div className="flex justify-between items-center mt-4 pt-3 border-t">
          <div className="text-sm text-muted-foreground">
            Showing {startIndex + 1} to {Math.min(endIndex, totalTrains)} of {totalTrains} trains
          </div>
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={handlePrevPage}
              disabled={!pagination.has_prev}
              className="h-7 text-xs"
            >
              <ChevronLeft className="h-3 w-3 mr-1" />
              Previous
            </Button>
            <span className="text-sm text-muted-foreground px-2">
              Page {pagination.page} of {pagination.total_pages}
            </span>
            <Button
              size="sm"
              variant="outline"
              onClick={handleNextPage}
              disabled={!pagination.has_next}
              className="h-7 text-xs"
            >
              Next
              <ChevronRight className="h-3 w-3 ml-1" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
