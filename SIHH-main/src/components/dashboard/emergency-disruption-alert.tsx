
'use client';

import { useEffect, useState } from 'react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { AlertTriangle, Lightbulb, Loader2 } from 'lucide-react';
import { Button } from '../ui/button';
import { generateRecommendations, GenerateRecommendationsInput, GenerateRecommendationsOutput } from '@/ai/flows/generate-recommendations';
import { Badge } from '../ui/badge';

type Disruption = {
  type: string;
  severity: 'Low' | 'Medium' | 'High';
  location: string;
  details: string;
};

type EmergencyDisruptionAlertProps = {
  disruption: Disruption;
  isOpen: boolean;
  onOpenChange: (isOpen: boolean) => void;
};

export default function EmergencyDisruptionAlert({
  disruption,
  isOpen,
  onOpenChange,
}: EmergencyDisruptionAlertProps) {
  const [suggestion, setSuggestion] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Generate suggestion when the dialog is opened
    if (isOpen && !suggestion) {
      handleGenerateSuggestion();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen]);

  const handleGenerateSuggestion = async () => {
    setIsLoading(true);
    try {
        const input: GenerateRecommendationsInput = {
            disruptions: [`${disruption.type} at ${disruption.location}: ${disruption.details}`],
            trainStatuses: ['Multiple trains at risk of significant delay.'],
        };

        const result = await generateRecommendations(input);
        if (result && result.recommendations && result.recommendations.length > 0) {
            setSuggestion(result.recommendations[0].recommendation);
        } else {
             setSuggestion('Could not generate a suggestion. Please refer to standard protocols.');
        }

    } catch (e) {
      console.error('Failed to generate suggestion:', e);
      setSuggestion('Could not generate a suggestion. Please refer to standard protocols.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!disruption) return null;

  return (
    <AlertDialog open={isOpen} onOpenChange={onOpenChange}>
      <AlertDialogContent className="max-w-2xl border-destructive ring-4 ring-destructive/10">
        <AlertDialogHeader>
          <AlertDialogTitle className="flex items-center gap-3 text-2xl">
            <AlertTriangle className="h-8 w-8 text-destructive" />
            <span>Emergency Alert: {disruption.type}</span>
          </AlertDialogTitle>
          <AlertDialogDescription className="pt-2 text-base">
            A new high-priority disruption has been detected at{' '}
            <span className="font-bold text-foreground">{disruption.location}</span>. Immediate action is required.
          </AlertDialogDescription>
        </AlertDialogHeader>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">
            <div className='space-y-4'>
                <div>
                    <h3 className='font-semibold text-foreground mb-2'>Disruption Details</h3>
                    <p className='text-muted-foreground'>{disruption.details}</p>
                    <div className='mt-2'>
                        <Badge variant="destructive">{disruption.severity} Severity</Badge>
                    </div>
                </div>
                 <div>
                    <h3 className='font-semibold text-foreground mb-2 flex items-center gap-2'>
                        <Lightbulb className='text-primary'/>
                        <span>AI Quick Suggestion</span>
                    </h3>
                    <div className='text-primary font-medium bg-primary/10 p-3 rounded-md min-h-[80px] flex items-center justify-center'>
                        {isLoading ? (
                            <Loader2 className='animate-spin h-6 w-6 text-primary' />
                        ) : (
                            <p className='text-center'>{suggestion}</p>
                        )}
                    </div>
                </div>
            </div>
            <div>
                 <h3 className='font-semibold text-foreground mb-2'>Impact Assessment Video</h3>
                <div className="aspect-video bg-muted rounded-lg flex items-center justify-center">
                    <video controls className="w-full h-full rounded-lg" key={disruption.type}>
                      <source src="https://photos.app.goo.gl/ZX5iV1qMn2LBDQMQ6" type="video/mp4" />
                      Your browser does not support the video tag. This video may not play because it is a Google Photos link. Please use a direct video file URL.
                    </video>
                </div>
            </div>

        </div>

        <AlertDialogFooter className="pt-4">
          <AlertDialogAction asChild>
            <Button onClick={() => onOpenChange(false)} className='w-full sm:w-auto'>
              Acknowledge & Close
            </Button>
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
