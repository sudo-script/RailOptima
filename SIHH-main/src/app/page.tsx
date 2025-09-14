
'use client';

import { useState, useEffect } from 'react';
import Header from '@/components/header';
import KpiBar from '@/components/dashboard/kpi-bar';
import DisruptionsPanel from '@/components/dashboard/disruptions-panel';
import RecommendationsPanel from '@/components/dashboard/recommendations-panel';
import DecisionLog from '@/components/dashboard/decision-log';
import TrainTimeline from '@/components/dashboard/train-timeline';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import EmergencyDisruptionAlert from '@/components/dashboard/emergency-disruption-alert';
import { generateRecommendations, GenerateRecommendationsInput, GenerateRecommendationsOutput } from '@/ai/flows/generate-recommendations';
import { useRealtimeData } from '@/hooks/use-api-data';
import { useCSVTrains } from '@/hooks/use-api-data';
import { Train, Disruption } from '@/lib/api';


// Helper function to convert API data to frontend format
const convertTrainData = (apiTrains: Train[]) => {
  return apiTrains.map(train => {
    // Determine status based on API data
    let status: 'On Time' | 'At Risk' | 'Delayed' = 'On Time';
    if (train.delay_minutes > 10) {
      status = 'Delayed';
    } else if (train.delay_minutes > 5) {
      status = 'At Risk';
    }

    // Map API status to frontend status
    if (train.status === 'departed') {
      status = 'On Time'; // Departed trains are considered on time unless delayed
    } else if (train.status === 'arrived') {
      status = 'On Time'; // Arrived trains are on time
    } else if (train.status === 'scheduled') {
      status = train.delay_minutes > 0 ? 'At Risk' : 'On Time';
    }

    return {
      id: train.id,
      status,
      route: train.route,
      currentLocation: train.current_station || 'Unknown',
      nextStop: 'Next Station',
      progress: 0, // Use API progress if available
      passengers: train.capacity || 0,
      delay: train.delay_minutes || 0,
    };
  });
};

const convertDisruptionData = (apiDisruptions: Disruption[]) => {
  return apiDisruptions.map(disruption => ({
    type: disruption.type as 'Signal Failure' | 'Track Blockage' | 'Passenger Incident',
    severity: disruption.severity === 'critical' ? 'High' : disruption.severity.charAt(0).toUpperCase() + disruption.severity.slice(1) as 'Low' | 'Medium' | 'High',
    location: disruption.affected_stations.join(', '),
    details: disruption.description,
    affectedTrains: disruption.affected_trains,
    isEmergency: disruption.severity === 'high' || disruption.severity === 'critical',
  }));
};


export default function Home() {
  const [isAlertOpen, setIsAlertOpen] = useState(false);
  const [isManualMode, setIsManualMode] = useState(false);
  const [recommendations, setRecommendations] = useState<GenerateRecommendationsOutput['recommendations']>([]);
  const [isLoadingRecs, setIsLoadingRecs] = useState(true);

  // Use CSV data from API
  const { data: csvTrains, loading: csvLoading, error: csvError } = useCSVTrains();
  const { disruptions: apiDisruptions, kpiData, loading: apiLoading, error: apiError } = useRealtimeData();

  // Convert CSV data to frontend format
  const trainData = convertTrainData(csvTrains || []);
  const disruptionData = convertDisruptionData(apiDisruptions);
  const emergencyDisruption = disruptionData.find(d => d.isEmergency);

  useEffect(() => {
    async function fetchRecommendations() {
      if (csvLoading || !csvTrains?.length || !apiDisruptions.length) return;
      
      setIsLoadingRecs(true);
      try {
        const trainStatuses = trainData.map(t => `${t.id} (${t.route}) is ${t.status}`);
        const currentDisruptions = disruptionData.map(d => `${d.type} at ${d.location}: ${d.details}`);
        
        const input: GenerateRecommendationsInput = {
          trainStatuses: trainStatuses,
          disruptions: currentDisruptions,
        };

        const result = await generateRecommendations(input);
        setRecommendations(result.recommendations);
      } catch (error) {
        console.error("AI recommendation failed:", error);
        // Fallback recommendations
        setRecommendations([
          {
            recommendation: "Review manual protocols",
            reason: "Could not fetch AI-powered recommendations due to a network or system error.",
            confidence: 0,
            impact: 'High',
            timeSaving: 0,
            performanceImprovement: 0,
          }
        ]);
      }
      setIsLoadingRecs(false);
    }

    fetchRecommendations();
    
    // Auto-trigger the alert on initial load to simulate a live event
    const timer = setTimeout(() => {
      if (emergencyDisruption) {
        setIsAlertOpen(true);
      }
    }, 2500);
    return () => clearTimeout(timer);
  }, [csvTrains, apiDisruptions, csvLoading]);

  // Show loading state while CSV data is being fetched
  if (csvLoading) {
    return (
      <div className="flex flex-col min-h-screen bg-background font-sans">
        <Header isManualMode={isManualMode} onToggleManualMode={() => setIsManualMode(!isManualMode)} />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading railway data...</p>
          </div>
        </main>
      </div>
    );
  }

  // Show error state if API fails
  if (apiError) {
    return (
      <div className="flex flex-col min-h-screen bg-background font-sans">
        <Header isManualMode={isManualMode} onToggleManualMode={() => setIsManualMode(!isManualMode)} />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="text-destructive text-lg mb-2">⚠️ Connection Error</div>
            <p className="text-muted-foreground mb-4">Unable to connect to the railway API</p>
            <p className="text-sm text-muted-foreground">{apiError}</p>
          </div>
        </main>
      </div>
    );
  }

  const centralColSpan = isManualMode ? 'lg:col-span-3' : 'lg:col-span-2';

  return (
    <div className="flex flex-col min-h-screen bg-background font-sans">
      <Header isManualMode={isManualMode} onToggleManualMode={() => setIsManualMode(!isManualMode)} />
      <main className="flex-1 flex flex-col">
        {emergencyDisruption && (
           <EmergencyDisruptionAlert 
             disruption={emergencyDisruption} 
             isOpen={isAlertOpen}
             onOpenChange={setIsAlertOpen}
           />
        )}
        <KpiBar data={kpiData || {
          punctuality: { value: 0, target: 95, trend: 0 },
          avgDelay: { value: 0, target: 5, trend: 0 },
          activeTrains: { value: 0, capacity: 600, trend: 0 },
          disruptions: { value: 0, last24h: 0, trend: 0 },
        }} />
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-4 p-4 items-start">
          <div className="lg:col-span-1 bg-card p-4 rounded-lg shadow-sm border h-full">
            <DisruptionsPanel disruptions={disruptionData} onShowAlert={() => setIsAlertOpen(true)} />
          </div>
          <div className={`${centralColSpan} flex flex-col gap-4`}>
             <Tabs defaultValue="timeline" className="bg-card p-4 rounded-lg shadow-sm border w-full">
              <TabsList className='mb-2'>
                <TabsTrigger value="timeline">Train Timeline</TabsTrigger>
                <TabsTrigger value="log">Decision Log</TabsTrigger>
              </TabsList>
              <TabsContent value="timeline">
                <TrainTimeline />
              </TabsContent>
              <TabsContent value="log">
                <DecisionLog />
              </TabsContent>
            </Tabs>
          </div>
          {!isManualMode && (
            <div className="lg:col-span-1 bg-card p-4 rounded-lg shadow-sm border h-full">
              <RecommendationsPanel recommendations={recommendations} isLoading={isLoadingRecs} />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
